export function formatDate(value) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function percentage(value) {
  const number = Number(value)

  if (!Number.isFinite(number)) return '—'

  return `${Math.round(number * 100)}%`
}

export function normalizePlate(value = '') {
  return value.toUpperCase().replace(/[^A-Z0-9]/g, '')
}

export function priorityMeta(priority) {
  const numericPriority = Number(priority)

  if (numericPriority === 3) {
    return { label: 'Alta', className: 'priority priority--high' }
  }

  if (numericPriority === 2) {
    return { label: 'Media', className: 'priority priority--medium' }
  }

  return { label: 'Baja', className: 'priority priority--low' }
}
