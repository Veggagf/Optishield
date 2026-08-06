# OptiShield ALPR — Backend FastAPI

## 1. Estructura

Coloca `yolov8n.pt` en la raíz del backend:

```text
optishield_fastapi_backend/
├── app/
├── yolov8n.pt
├── requirements.txt
└── .env
```

## 2. Crear entorno virtual

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 3. Variables de entorno

Copia `.env.example` como `.env` y agrega las credenciales de Supabase.

## 4. Ejecutar

```powershell
python -m uvicorn app.main:app --reload
```

Abre:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## 5. Endpoints

- `POST /api/predict/image`: analiza una imagen subida.
- `POST /api/predict/frame`: analiza un fotograma de la cámara web.
- `GET /api/detections`: devuelve la bitácora.
- `GET /api/wanted`: devuelve vehículos buscados.
- `GET /api/wanted/{plate}`: consulta una placa.

## Nota importante

`yolov8n.pt` detecta vehículos generales. El OCR se ejecuta sobre el vehículo
completo, por lo que puede leer otros textos. Para precisión real se recomienda
un segundo modelo YOLO entrenado específicamente para detectar placas.
