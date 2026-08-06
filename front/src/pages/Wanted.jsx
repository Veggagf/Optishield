import { useMemo, useState } from 'react'
import {
  EmptyState,
  ErrorMessage,
  PageHeader,
  PriorityBadge,
  SuccessMessage,
} from '../components/Common'
import { formatDate, normalizePlate } from '../utils/format'

const initialForm = {
  placa: '',
  motivo: '',
  prioridad: 1,
  color: '',
  modelo: '',
  marca: '',
  anio: '',
  registrado_por: '',
}

export default function Wanted({ vehicles, api, onDataChanged }) {
  const [form, setForm] = useState(initialForm)
  const [query, setQuery] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()

    if (!normalizedQuery) return vehicles

    return vehicles.filter((vehicle) =>
      [
        vehicle.placa,
        vehicle.motivo,
        vehicle.marca,
        vehicle.modelo,
        vehicle.registrado_por,
      ]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(normalizedQuery)),
    )
  }, [vehicles, query])

  function updateField(event) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: name === 'placa' ? normalizePlate(value) : value,
    }))
  }

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')

    try {
      await api.createWanted({
        ...form,
        prioridad: Number(form.prioridad),
        anio: form.anio ? Number(form.anio) : null,
        color: form.color || null,
        modelo: form.modelo || null,
        marca: form.marca || null,
      })

      setMessage('Vehículo agregado a la lista de búsqueda.')
      setForm(initialForm)
      setShowForm(false)
      await onDataChanged()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  async function deactivate(id) {
    if (!window.confirm('¿Deseas desactivar esta búsqueda?')) return

    setError('')

    try {
      await api.deactivateWanted(id)
      await onDataChanged()
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Control de búsquedas"
        title="Vehículos buscados"
        description="Registra y administra matrículas con búsqueda activa."
        action={
          <button
            className="button button--primary"
            onClick={() => setShowForm((current) => !current)}
          >
            {showForm ? 'Cerrar formulario' : 'Registrar vehículo'}
          </button>
        }
      />

      <ErrorMessage message={error} />
      <SuccessMessage message={message} />

      {showForm && (
        <form className="panel form-panel" onSubmit={submit}>
          <div className="form-grid">
            <label>
              <span>Placa *</span>
              <input
                name="placa"
                value={form.placa}
                onChange={updateField}
                placeholder="XYZ5678"
                required
              />
            </label>

            <label>
              <span>Prioridad *</span>
              <select
                name="prioridad"
                value={form.prioridad}
                onChange={updateField}
                required
              >
                <option value={1}>Baja</option>
                <option value={2}>Media</option>
                <option value={3}>Alta</option>
              </select>
            </label>

            <label className="form-grid__wide">
              <span>Motivo de búsqueda *</span>
              <input
                name="motivo"
                value={form.motivo}
                onChange={updateField}
                placeholder="Reporte de robo"
                required
              />
            </label>

            <label>
              <span>Color</span>
              <input
                name="color"
                value={form.color}
                onChange={updateField}
                placeholder="Negro"
              />
            </label>

            <label>
              <span>Marca</span>
              <input
                name="marca"
                value={form.marca}
                onChange={updateField}
                placeholder="Nissan"
              />
            </label>

            <label>
              <span>Modelo</span>
              <input
                name="modelo"
                value={form.modelo}
                onChange={updateField}
                placeholder="Versa"
              />
            </label>

            <label>
              <span>Año</span>
              <input
                name="anio"
                type="number"
                min="1900"
                max="2100"
                value={form.anio}
                onChange={updateField}
                placeholder="2020"
              />
            </label>

            <label className="form-grid__wide">
              <span>Nombre de quien registra *</span>
              <input
                name="registrado_por"
                value={form.registrado_por}
                onChange={updateField}
                placeholder="Nombre completo"
                required
              />
            </label>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="button button--secondary"
              onClick={() => setShowForm(false)}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="button button--primary"
              disabled={loading}
            >
              {loading ? 'Registrando…' : 'Guardar vehículo'}
            </button>
          </div>
        </form>
      )}

      <div className="toolbar">
        <input
          className="search-input"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Buscar por placa, motivo, marca o responsable…"
        />
        <span>{filtered.length} registros</span>
      </div>

      <article className="panel table-panel">
        {filtered.length ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Prioridad</th>
                  <th>Motivo</th>
                  <th>Vehículo</th>
                  <th>Registrado por</th>
                  <th>Fecha</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {filtered.map((vehicle) => (
                  <tr key={vehicle.id}>
                    <td>
                      <span className="plate plate--table">
                        {vehicle.placa}
                      </span>
                    </td>
                    <td>
                      <PriorityBadge priority={vehicle.prioridad} />
                    </td>
                    <td>{vehicle.motivo}</td>
                    <td>
                      <strong>
                        {[vehicle.marca, vehicle.modelo]
                          .filter(Boolean)
                          .join(' ') || '—'}
                      </strong>
                      <small>
                        {[vehicle.color, vehicle.anio]
                          .filter(Boolean)
                          .join(' · ') || 'Sin detalles'}
                      </small>
                    </td>
                    <td>{vehicle.registrado_por}</td>
                    <td>{formatDate(vehicle.fecha_registro || vehicle.creado_en)}</td>
                    <td className="table-action">
                      {vehicle.activo && (
                        <button
                          className="text-button text-button--danger"
                          onClick={() => deactivate(vehicle.id)}
                        >
                          Desactivar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="Sin vehículos"
            description="Registra una matrícula para comenzar la lista de búsqueda."
          />
        )}
      </article>
    </>
  )
}
