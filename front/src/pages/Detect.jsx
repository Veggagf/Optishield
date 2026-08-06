import { useEffect, useRef, useState } from 'react'
import {
  ErrorMessage,
  PageHeader,
  PriorityBadge,
} from '../components/Common'
import { Icons } from '../components/Icons'
import { percentage } from '../utils/format'

export default function Detect({ api, onDataChanged }) {
  const [mode, setMode] = useState('upload')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [cameraActive, setCameraActive] = useState(false)
  const videoRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    return () => stopCamera()
  }, [])

  function selectFile(selectedFile) {
    if (!selectedFile) return

    setFile(selectedFile)
    setPreview(URL.createObjectURL(selectedFile))
    setResult(null)
    setError('')
  }

  async function analyzeFile() {
    if (!file) {
      setError('Selecciona una imagen antes de analizar.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const data = await api.predictImage(file, true)
      setResult(data)
      await onDataChanged()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  async function startCamera() {
    setError('')

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      })

      streamRef.current = stream
      videoRef.current.srcObject = stream
      await videoRef.current.play()
      setCameraActive(true)
    } catch {
      setError(
        'No se pudo abrir la cámara. Revisa los permisos del navegador.',
      )
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
    setCameraActive(false)

    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }

  async function captureFrame() {
    const video = videoRef.current

    if (!video || !cameraActive || !video.videoWidth) {
      setError('Activa la cámara antes de capturar.')
      return
    }

    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const context = canvas.getContext('2d')
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    setLoading(true)
    setError('')

    try {
      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, 'image/jpeg', 0.9),
      )

      if (!blob) throw new Error('No fue posible capturar el fotograma.')

      const data = await api.predictFrame(blob, true)
      setResult(data)
      await onDataChanged()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Reconocimiento"
        title="Analizar matrícula"
        description="Carga una fotografía o captura un fotograma desde la cámara."
      />

      <div className="segmented-control">
        <button
          className={mode === 'upload' ? 'active' : ''}
          onClick={() => setMode('upload')}
        >
          <Icons.upload />
          Subir imagen
        </button>
        <button
          className={mode === 'camera' ? 'active' : ''}
          onClick={() => setMode('camera')}
        >
          <Icons.camera />
          Cámara
        </button>
      </div>

      <ErrorMessage message={error} />

      <section className="detect-grid">
        <article className="panel detect-panel">
          {mode === 'upload' ? (
            <>
              <label className="dropzone">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={(event) => selectFile(event.target.files?.[0])}
                />
                {preview ? (
                  <img src={preview} alt="Imagen seleccionada" />
                ) : (
                  <div className="dropzone__content">
                    <Icons.upload />
                    <strong>Selecciona una fotografía</strong>
                    <span>PNG, JPG o WEBP · máximo 10 MB</span>
                  </div>
                )}
              </label>

              <button
                className="button button--primary button--full"
                onClick={analyzeFile}
                disabled={loading || !file}
              >
                {loading ? 'Analizando…' : 'Analizar imagen'}
              </button>
            </>
          ) : (
            <>
              <div className="camera-frame">
                <video ref={videoRef} muted playsInline />
                {!cameraActive && (
                  <div className="camera-frame__placeholder">
                    <Icons.camera />
                    <strong>Cámara inactiva</strong>
                    <span>Actívala para capturar una matrícula.</span>
                  </div>
                )}
              </div>

              <div className="button-row">
                {!cameraActive ? (
                  <button
                    className="button button--primary"
                    onClick={startCamera}
                  >
                    Activar cámara
                  </button>
                ) : (
                  <>
                    <button
                      className="button button--primary"
                      onClick={captureFrame}
                      disabled={loading}
                    >
                      {loading ? 'Analizando…' : 'Capturar y analizar'}
                    </button>
                    <button
                      className="button button--secondary"
                      onClick={stopCamera}
                    >
                      Detener cámara
                    </button>
                  </>
                )}
              </div>
            </>
          )}
        </article>

        <article className="panel result-panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Resultado</span>
              <h2>Lectura procesada</h2>
            </div>
          </div>

          {!result ? (
            <div className="result-placeholder">
              <div className="result-placeholder__scan" />
              <strong>Aún no hay un análisis</strong>
              <span>El resultado aparecerá en este panel.</span>
            </div>
          ) : (
            <div className="result-content">
              {result.annotated_image && (
                <img
                  className="result-image"
                  src={result.annotated_image}
                  alt="Imagen con matrícula detectada"
                />
              )}

              {result.detections.map((detection, index) => {
                const vehicle = detection.alerta?.vehiculo

                return (
                  <div className="detection-result" key={`${detection.placa}-${index}`}>
                    <div className="detection-result__top">
                      <div>
                        <span>Matrícula detectada</span>
                        <div className="plate">{detection.placa}</div>
                      </div>
                      <strong className="confidence">
                        {percentage(detection.confianza)}
                      </strong>
                    </div>

                    <div className="confidence-grid">
                      <div>
                        <span>YOLO</span>
                        <strong>{percentage(detection.confianza_yolo)}</strong>
                      </div>
                      <div>
                        <span>OCR</span>
                        <strong>{percentage(detection.confianza_ocr)}</strong>
                      </div>
                    </div>

                    {detection.alerta ? (
                      <div className="alert-card">
                        <div className="alert-card__header">
                          <div>
                            <span>Coincidencia activa</span>
                            <strong>{vehicle?.motivo || 'Vehículo buscado'}</strong>
                          </div>
                          <PriorityBadge priority={vehicle?.prioridad || 1} />
                        </div>
                        <p>
                          {vehicle?.marca || 'Marca no registrada'}{' '}
                          {vehicle?.modelo || ''} ·{' '}
                          {vehicle?.color || 'Color no registrado'}
                        </p>
                      </div>
                    ) : (
                      <div className="clear-card">
                        No existen coincidencias activas para esta matrícula.
                      </div>
                    )}
                  </div>
                )
              })}

              {!result.detections.length && (
                <div className="clear-card">
                  No se encontró una matrícula legible en la imagen.
                </div>
              )}
            </div>
          )}
        </article>
      </section>
    </>
  )
}
