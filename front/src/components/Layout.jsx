import { Icons } from './Icons'

const navigation = [
  { id: 'dashboard', label: 'Resumen', icon: Icons.dashboard },
  { id: 'detect', label: 'Detectar', icon: Icons.scan },
  { id: 'wanted', label: 'Vehículos buscados', icon: Icons.wanted },
  { id: 'detections', label: 'Detecciones', icon: Icons.history },
  { id: 'alerts', label: 'Alertas', icon: Icons.alert },
]

export default function Layout({
  children,
  page,
  onPageChange,
  theme,
  onToggleTheme,
  sidebarOpen,
  setSidebarOpen,
  health,
}) {
  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar--open' : ''}`}>
        <div className="brand">
          <div className="brand__mark">OS</div>
          <div>
            <strong>OptiShield</strong>
            <span>ALPR Pericial</span>
          </div>
          <button
            className="icon-button sidebar__close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Cerrar menú"
          >
            <Icons.close />
          </button>
        </div>

        <nav className="navigation" aria-label="Navegación principal">
          {navigation.map((item) => {
            const Icon = item.icon

            return (
              <button
                key={item.id}
                className={`navigation__item ${
                  page === item.id ? 'navigation__item--active' : ''
                }`}
                onClick={() => {
                  onPageChange(item.id)
                  setSidebarOpen(false)
                }}
              >
                <Icon />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="sidebar__footer">
          <div className="connection">
            <span
              className={`connection__dot ${
                health?.status === 'ok' ? 'connection__dot--online' : ''
              }`}
            />
            <div>
              <strong>
                {health?.status === 'ok' ? 'Sistema en línea' : 'Sin conexión'}
              </strong>
              <span>FastAPI · Supabase</span>
            </div>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-label="Cerrar menú"
        />
      )}

      <main className="main">
        <header className="topbar">
          <button
            className="icon-button menu-button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Abrir menú"
          >
            <Icons.menu />
          </button>

          <div className="topbar__title">
            <span>Centro de control</span>
            <strong>
              {navigation.find((item) => item.id === page)?.label}
            </strong>
          </div>

          <button
            className="theme-toggle"
            onClick={onToggleTheme}
            aria-label="Cambiar tema"
          >
            {theme === 'dark' ? <Icons.sun /> : <Icons.moon />}
            <span>{theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}</span>
          </button>
        </header>

        <div className="page-container">{children}</div>
      </main>
    </div>
  )
}
