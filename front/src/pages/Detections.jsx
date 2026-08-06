import { useMemo, useState } from 'react'
import {
  EmptyState,
  PageHeader,
  RefreshButton,
  StatusBadge,
} from '../components/Common'
import { formatDate, percentage } from '../utils/format'

export default function Detections({ detections, loading, onRefresh }) {
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('all')

  const filtered = useMemo(() => {
    return detections.filter((detection) => {
      const matchesQuery = detection.placa
        ?.toLowerCase()
        .includes(query.toLowerCase())

      const matchesFilter =
        filter === 'all' ||
        (filter === 'alerts' && detection.tiene_alerta) ||
        (filter === 'clear' && !detection.tiene_alerta)

      return matchesQuery && matchesFilter
    })
  }, [detections, query, filter])

  return (
    <>
      <PageHeader
        eyebrow="Bitácora"
        title="Historial de detecciones"
        description="Todas las matrículas reconocidas, tengan o no una coincidencia."
        action={<RefreshButton onClick={onRefresh} loading={loading} />}
      />

      <div className="toolbar toolbar--wrap">
        <input
          className="search-input"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Buscar matrícula…"
        />

        <div className="filter-buttons">
          {[
            ['all', 'Todas'],
            ['alerts', 'Con alerta'],
            ['clear', 'Sin alerta'],
          ].map(([value, label]) => (
            <button
              key={value}
              className={filter === value ? 'active' : ''}
              onClick={() => setFilter(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <article className="panel table-panel">
        {filtered.length ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Fecha y hora</th>
                  <th>Confianza</th>
                  <th>Origen</th>
                  <th>Cámara</th>
                  <th>Ubicación</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((detection) => (
                  <tr key={detection.id}>
                    <td>
                      <span className="plate plate--table">
                        {detection.placa}
                      </span>
                    </td>
                    <td>{formatDate(detection.fecha_hora)}</td>
                    <td>
                      <strong>{percentage(detection.confianza)}</strong>
                      <small>
                        YOLO {percentage(detection.confianza_yolo)} · OCR{' '}
                        {percentage(detection.confianza_ocr)}
                      </small>
                    </td>
                    <td>{detection.origen || '—'}</td>
                    <td>{detection.camara_id || '—'}</td>
                    <td>{detection.ubicacion || '—'}</td>
                    <td>
                      <StatusBadge
                        status={
                          detection.tiene_alerta
                            ? 'coincidencia'
                            : 'sin alerta'
                        }
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="Sin resultados"
            description="No hay detecciones que coincidan con los filtros."
          />
        )}
      </article>
    </>
  )
}
