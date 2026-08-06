import { Icons } from './Icons'
import { priorityMeta } from '../utils/format'

export function PageHeader({ eyebrow, title, description, action }) {
  return (
    <div className="page-header">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  )
}

export function StatCard({ label, value, detail, tone = 'default' }) {
  return (
    <article className={`stat-card stat-card--${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  )
}

export function PriorityBadge({ priority }) {
  const meta = priorityMeta(priority)

  return <span className={meta.className}>{meta.label}</span>
}

export function StatusBadge({ status }) {
  const normalized = (status || '').toLowerCase()

  return (
    <span className={`status status--${normalized || 'default'}`}>
      {status || 'Sin estado'}
    </span>
  )
}

export function EmptyState({ title, description }) {
  return (
    <div className="empty-state">
      <div className="empty-state__icon">○</div>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  )
}

export function ErrorMessage({ message }) {
  if (!message) return null

  return <div className="message message--error">{message}</div>
}

export function SuccessMessage({ message }) {
  if (!message) return null

  return <div className="message message--success">{message}</div>
}

export function LoadingBlock({ label = 'Cargando información…' }) {
  return (
    <div className="loading-block">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  )
}

export function RefreshButton({ onClick, loading }) {
  return (
    <button
      className="button button--secondary"
      onClick={onClick}
      disabled={loading}
    >
      <Icons.refresh />
      Actualizar
    </button>
  )
}
