import {
  EmptyState,
  PageHeader,
  PriorityBadge,
  RefreshButton,
  StatCard,
  StatusBadge,
} from '../components/Common'
import { formatDate, percentage } from '../utils/format'

export default function Dashboard({
  wanted,
  detections,
  alerts,
  loading,
  onRefresh,
}) {
  const activeWanted = wanted.filter((vehicle) => vehicle.activo)
  const newAlerts = alerts.filter((alert) => alert.estatus === 'nueva')
  const alertDetections = detections.filter(
    (detection) => detection.tiene_alerta,
  )

  return (
    <>
      <PageHeader
        eyebrow="OptiShield ALPR"
        title="Resumen operativo"
        description="Seguimiento centralizado de matrículas, vehículos de interés y alertas."
        action={<RefreshButton onClick={onRefresh} loading={loading} />}
      />

      <section className="stats-grid">
        <StatCard
          label="Detecciones"
          value={detections.length}
          detail="Registros recientes"
        />
        <StatCard
          label="Vehículos buscados"
          value={activeWanted.length}
          detail="Búsquedas activas"
          tone="navy"
        />
        <StatCard
          label="Alertas nuevas"
          value={newAlerts.length}
          detail="Requieren revisión"
          tone="danger"
        />
        <StatCard
          label="Coincidencias"
          value={alertDetections.length}
          detail="Detecciones con alerta"
          tone="warning"
        />
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Actividad reciente</span>
              <h2>Últimas detecciones</h2>
            </div>
          </div>

          {detections.length ? (
            <div className="compact-list">
              {detections.slice(0, 6).map((detection) => (
                <div className="compact-list__item" key={detection.id}>
                  <div className="plate plate--small">{detection.placa}</div>
                  <div className="compact-list__body">
                    <strong>
                      {detection.tiene_alerta
                        ? 'Coincidencia encontrada'
                        : 'Sin coincidencias'}
                    </strong>
                    <span>{formatDate(detection.fecha_hora)}</span>
                  </div>
                  <div className="compact-list__meta">
                    <strong>{percentage(detection.confianza)}</strong>
                    <span>{detection.origen || '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="Sin detecciones"
              description="Las matrículas procesadas aparecerán aquí."
            />
          )}
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Atención</span>
              <h2>Alertas recientes</h2>
            </div>
          </div>

          {alerts.length ? (
            <div className="compact-list">
              {alerts.slice(0, 6).map((alert) => {
                const vehicle = alert.vehiculos_buscados || {}
                const detection = alert.detecciones || {}

                return (
                  <div className="compact-list__item" key={alert.id}>
                    <div className="compact-list__body">
                      <strong>
                        {vehicle.placa || detection.placa || 'Matrícula'}
                      </strong>
                      <span>{vehicle.motivo || 'Coincidencia detectada'}</span>
                    </div>
                    <div className="compact-list__badges">
                      <PriorityBadge priority={vehicle.prioridad || 1} />
                      <StatusBadge status={alert.estatus} />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <EmptyState
              title="Sin alertas"
              description="Las coincidencias con vehículos buscados aparecerán aquí."
            />
          )}
        </article>
      </section>
    </>
  )
}
