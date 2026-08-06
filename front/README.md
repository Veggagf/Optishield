# OptiShield Frontend

Frontend en React + Vite para el backend FastAPI de OptiShield.

## Requisitos

La guía oficial de Vite indica Node.js 20.19+ o 22.12+ para las versiones actuales.

## Instalación

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Abre:

```text
http://localhost:5173
```

## API

El archivo `.env` debe contener:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Funciones incluidas

- Dashboard operativo.
- Tema claro y oscuro.
- Subida de imágenes.
- Captura desde cámara del navegador.
- Registro y desactivación de vehículos buscados.
- Historial de detecciones.
- Administración de alertas.
- Colores por prioridad:
  - Baja: verde.
  - Media: amarillo.
  - Alta: rojo.

## Producción

Para construir:

```powershell
npm run build
```

La carpeta generada será `dist`.
