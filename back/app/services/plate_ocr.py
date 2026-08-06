from collections import Counter
from difflib import SequenceMatcher

import cv2
import numpy as np
import pytesseract
from pytesseract import Output


class PlateOCR:
    """
    Servicio OCR para matrículas.

    Genera distintas versiones del recorte, prueba varios modos
    de segmentación de Tesseract y elige el resultado con mayor
    consenso y calidad.
    """

    OCR_CONFIGS = [
        (
            "--oem 1 --psm 7 "
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ),
        (
            "--oem 1 --psm 8 "
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ),
        (
            "--oem 1 --psm 13 "
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ),
        (
            "--oem 1 --psm 6 "
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ),
    ]

    MIN_LENGTH = 4
    MAX_LENGTH = 10

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Conserva solamente letras y números.
        """
        return "".join(character for character in text.upper() if character.isalnum())

    @staticmethod
    def normalize_three_letters_four_numbers(
        text: str,
    ) -> str:
        """
        Corrige errores comunes cuando una lectura de siete
        caracteres parece corresponder al patrón LLLNNNN.

        No se aplica a matrículas con otra longitud.
        """
        text = PlateOCR.clean_text(text)

        if len(text) != 7:
            return text

        # Equivalencias cuando se espera una letra.
        number_to_letter = {
            "0": "O",
            "1": "I",
            "2": "Z",
            "5": "S",
            "6": "G",
            "7": "Z",
            "8": "B",
        }

        # Equivalencias cuando se espera un número.
        letter_to_number = {
            "O": "0",
            "Q": "0",
            "D": "0",
            "I": "1",
            "L": "1",
            "Z": "7",
            "S": "5",
            "G": "6",
            "B": "8",
        }

        first_section = "".join(
            number_to_letter.get(character, character) for character in text[:3]
        )

        second_section = "".join(
            letter_to_number.get(character, character) for character in text[3:]
        )

        if first_section.isalpha() and second_section.isdigit():
            return first_section + second_section

        return text

    @staticmethod
    def build_variants(
        plate_crop: np.ndarray,
    ) -> list[tuple[str, np.ndarray]]:
        """
        Genera diferentes versiones del recorte para mejorar
        la posibilidad de lectura de Tesseract.
        """
        if plate_crop.size == 0:
            return []

        gray = cv2.cvtColor(
            plate_crop,
            cv2.COLOR_BGR2GRAY,
        )

        height = gray.shape[0]

        if height < 50:
            scale_factor = 6
        elif height < 90:
            scale_factor = 5
        else:
            scale_factor = 4

        enlarged = cv2.resize(
            gray,
            None,
            fx=scale_factor,
            fy=scale_factor,
            interpolation=cv2.INTER_CUBIC,
        )

        gaussian = cv2.GaussianBlur(
            enlarged,
            (3, 3),
            0,
        )

        bilateral = cv2.bilateralFilter(
            enlarged,
            9,
            75,
            75,
        )

        equalized = cv2.equalizeHist(bilateral)

        clahe = cv2.createCLAHE(
            clipLimit=2.5,
            tileGridSize=(8, 8),
        )

        clahe_image = clahe.apply(bilateral)

        sharpen_kernel = np.array(
            [
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0],
            ],
            dtype=np.float32,
        )

        sharpened = cv2.filter2D(
            clahe_image,
            -1,
            sharpen_kernel,
        )

        _, otsu = cv2.threshold(
            equalized,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )

        _, otsu_inverted = cv2.threshold(
            equalized,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )

        adaptive = cv2.adaptiveThreshold(
            clahe_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            9,
        )

        adaptive_inverted = cv2.bitwise_not(adaptive)

        close_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (2, 2),
        )

        closed = cv2.morphologyEx(
            otsu,
            cv2.MORPH_CLOSE,
            close_kernel,
        )

        variants = [
            ("enlarged", enlarged),
            ("gaussian", gaussian),
            ("bilateral", bilateral),
            ("equalized", equalized),
            ("clahe", clahe_image),
            ("sharpened", sharpened),
            ("otsu", otsu),
            ("otsu_inverted", otsu_inverted),
            ("adaptive", adaptive),
            ("adaptive_inverted", adaptive_inverted),
            ("closed", closed),
        ]

        final_variants: list[tuple[str, np.ndarray]] = []

        for name, variant in variants:
            bordered = cv2.copyMakeBorder(
                variant,
                40,
                40,
                40,
                40,
                cv2.BORDER_CONSTANT,
                value=255,
            )

            final_variants.append((name, bordered))

        return final_variants

    def read_variant(
        self,
        image: np.ndarray,
        config: str,
    ) -> tuple[str, float]:
        """
        Ejecuta Tesseract sobre una versión de la imagen.
        """
        data = pytesseract.image_to_data(
            image,
            config=config,
            output_type=Output.DICT,
        )

        pieces: list[str] = []
        confidences: list[float] = []

        for text, confidence in zip(
            data.get("text", []),
            data.get("conf", []),
        ):
            cleaned = self.clean_text(str(text))

            try:
                numeric_confidence = float(confidence)
            except (TypeError, ValueError):
                numeric_confidence = -1.0

            if cleaned:
                pieces.append(cleaned)

                if numeric_confidence >= 0:
                    confidences.append(numeric_confidence / 100.0)

        combined = self.clean_text("".join(pieces))

        # Segunda oportunidad usando image_to_string.
        if not combined:
            raw_text = pytesseract.image_to_string(
                image,
                config=config,
            )

            combined = self.clean_text(raw_text)

        if not combined:
            return "", 0.0

        average_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.20
        )

        return combined, average_confidence

    @staticmethod
    def candidate_quality(
        text: str,
        confidence: float,
        frequency: int,
        all_texts: list[str],
    ) -> float:
        """
        Calcula una puntuación combinando confianza, frecuencia,
        longitud, mezcla de caracteres y similitud entre lecturas.
        """
        length = len(text)

        if 6 <= length <= 8:
            length_score = 1.0
        elif length in (5, 9):
            length_score = 0.55
        else:
            length_score = 0.20

        contains_letters = any(character.isalpha() for character in text)

        contains_numbers = any(character.isdigit() for character in text)

        mixed_score = 1.0 if contains_letters and contains_numbers else 0.35

        other_texts = [other for other in all_texts if other != text]

        similarities = [
            SequenceMatcher(
                None,
                text,
                other,
            ).ratio()
            for other in other_texts
        ]

        consensus_score = sum(similarities) / len(similarities) if similarities else 0.0

        frequency_score = min(
            frequency / 4.0,
            1.0,
        )

        return (
            confidence * 0.30
            + frequency_score * 0.25
            + length_score * 0.20
            + mixed_score * 0.15
            + consensus_score * 0.10
        )

    def read(
        self,
        plate_crop: np.ndarray,
    ) -> tuple[str, float]:
        """
        Devuelve la mejor matrícula y su confianza OCR.
        """
        if plate_crop.size == 0:
            return "", 0.0

        raw_candidates: list[tuple[str, float, str]] = []

        for variant_name, variant in self.build_variants(plate_crop):
            for config in self.OCR_CONFIGS:
                text, confidence = self.read_variant(
                    variant,
                    config,
                )

                if not (self.MIN_LENGTH <= len(text) <= self.MAX_LENGTH):
                    continue

                raw_candidates.append(
                    (
                        text,
                        confidence,
                        variant_name,
                    )
                )

                print(
                    "[OCR] Candidato:",
                    {
                        "texto": text,
                        "confianza": round(
                            confidence,
                            4,
                        ),
                        "variante": variant_name,
                    },
                )

        if not raw_candidates:
            print("[OCR] No se obtuvo ninguna " "lectura válida.")

            return "", 0.0

        frequencies = Counter(text for text, _, _ in raw_candidates)

        best_confidence_by_text: dict[
            str,
            float,
        ] = {}

        for text, confidence, _ in raw_candidates:
            current_confidence = best_confidence_by_text.get(
                text,
                0.0,
            )

            best_confidence_by_text[text] = max(
                current_confidence,
                confidence,
            )

        all_texts = list(best_confidence_by_text.keys())

        ranked_candidates: list[tuple[float, str, float]] = []

        for text, confidence in best_confidence_by_text.items():
            score = self.candidate_quality(
                text=text,
                confidence=confidence,
                frequency=frequencies[text],
                all_texts=all_texts,
            )

            ranked_candidates.append(
                (
                    score,
                    text,
                    confidence,
                )
            )

        ranked_candidates.sort(
            key=lambda candidate: candidate[0],
            reverse=True,
        )

        best_score, best_text, best_confidence = ranked_candidates[0]

        normalized_text = self.normalize_three_letters_four_numbers(best_text)

        if normalized_text != best_text:
            print(
                "[OCR] Normalización aplicada:",
                {
                    "original": best_text,
                    "normalizada": normalized_text,
                },
            )

        # Evita reportar confianza cero cuando Tesseract sí
        # produjo una lectura utilizable.
        if normalized_text:
            best_confidence = max(
                best_confidence,
                0.20,
            )

        print(
            "[OCR] Clasificación final:",
            [
                {
                    "texto": text,
                    "puntuacion": round(
                        score,
                        4,
                    ),
                    "confianza": round(
                        confidence,
                        4,
                    ),
                    "repeticiones": frequencies[text],
                }
                for score, text, confidence in ranked_candidates[:10]
            ],
        )

        print(
            "[OCR] Mejor resultado:",
            {
                "texto_original": best_text,
                "texto_final": normalized_text,
                "confianza": round(
                    best_confidence,
                    4,
                ),
                "puntuacion": round(
                    best_score,
                    4,
                ),
            },
        )

        return normalized_text, best_confidence
