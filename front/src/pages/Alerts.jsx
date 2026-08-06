import { useMemo, useState } from 'react'
import {
  EmptyState,
  ErrorMessage,
  PageHeader,
  PriorityBadge,
  StatusBadge,
} from '../components/Common'
import { formatDate } from '../utils/format'

export default function Alerts({ alerts, api, onDataChanged }) {
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState('')
  const [updating, setUpdating] = useState(null)

  const filtered = useMemo(
    () =>
      filter === 'all'
        ? alerts
        : alerts.filter((alert) => alert.estatus === filter),
    [alerts, filter],
  )

  async function changeStatus(id, status) {
    setUpdating(id)
    setError('')

    try {
      await api.updateAlert(id, status)
      await onDataChanged()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setUpdating(null)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Coincidencias"
        title="Centro de alertas"
        description="Revisa y clasifica las coincidencias generadas por el sistema."
      />

      <ErrorMessage message={error} />

      <div className="filter-buttons filter-buttons--large">
        {[
          ['all', 'Todas'],
          ['nueva', 'Nuevas'],
          ['atendida', 'Atendidas'],
          ['descartada', 'Descartadas'],
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

      {filtered.length ? (
        <section className="alerts-grid">
          {filtered.map((alert) => {
            const vehicle = alert.vehiculos_buscados || {}
            const detection = alert.detecciones || {}

            return (
              <article
                className={`alert-item alert-item--priority-${
                  vehicle.prioridad || 1
                }`}
                key={alert.id}
              >
                <div className="alert-item__top">
                  <div>
                    <span>Alerta #{alert.id}</span>
                    <div className="plate">
                      {vehicle.placa || detection.placa || '—'}
                    </div>
                  </div>
                  <div className="alert-item__badges">
                    <PriorityBadge priority={vehicle.prioridad || 1} />
                    <StatusBadge status={alert.estatus} />
                  </div>
                </div>

                <div className="alert-item__details">
                  <div>
                    <span>Motivo</span>
                    <strong>{vehicle.motivo || 'No registrado'}</strong>
                  </div>
                  <div>
                    <span>Vehículo</span>
                    <strong>
                      {[vehicle.marca, vehicle.modelo]
                        .filter(Boolean)
                        .join(' ') || 'Sin datos'}
                    </strong>
                  </div>
                  <div>
                    <span>Color</span>
                    <strong>{vehicle.color || 'No registrado'}</strong>
                  </div>
                  <div>
                    <span>Detectado</span>
                    <strong>{formatDate(alert.fecha_alerta)}</strong>
                  </div>
                </div>

                <div className="alert-item__actions">
                  <button
                    className="button button--secondary"
                    disabled={updating === alert.id}
                    onClick={() => changeStatus(alert.id, 'descartada')}
                  >
                    Descartar
                  </button>
                  <button
                    className="button button--primary"
                    disabled={updating === alert.id}
                    onClick={() => changeStatus(alert.id, 'atendida')}
                  >
                    Marcar atendida
                  </button>
                </div>
              </article>
            )
          })}
        </section>
      ) : (
        <article className="panel">
          <EmptyState
            title="Sin alertas"
            description="No hay alertas que coincidan con el filtro seleccionado."
          />
        </article>
      )}
    </>
  )
}
