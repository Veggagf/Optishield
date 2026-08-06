from pathlib import Path

import onnxruntime as ort


MODEL_PATH = Path("models/best.onnx")


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No se encontró el modelo: {MODEL_PATH.resolve()}")

    session = ort.InferenceSession(
        str(MODEL_PATH),
        providers=["CPUExecutionProvider"],
    )

    print("\nMODELO CARGADO CORRECTAMENTE")
    print(f"Ruta: {MODEL_PATH.resolve()}")

    print("\nENTRADAS:")
    for model_input in session.get_inputs():
        print(f"Nombre: {model_input.name}")
        print(f"Forma: {model_input.shape}")
        print(f"Tipo: {model_input.type}")
        print("-" * 40)

    print("\nSALIDAS:")
    for model_output in session.get_outputs():
        print(f"Nombre: {model_output.name}")
        print(f"Forma: {model_output.shape}")
        print(f"Tipo: {model_output.type}")
        print("-" * 40)


if __name__ == "__main__":
    main()
