import { useCallback, useEffect, useState } from 'react'
import { api } from './api/client'
import Layout from './components/Layout'
import Alerts from './pages/Alerts'
import Dashboard from './pages/Dashboard'
import Detect from './pages/Detect'
import Detections from './pages/Detections'
import Wanted from './pages/Wanted'

function getInitialTheme() {
  const saved = localStorage.getItem('optishield-theme')

  if (saved === 'dark' || saved === 'light') return saved

  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [theme, setTheme] = useState(getInitialTheme)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [health, setHealth] = useState(null)
  const [wanted, setWanted] = useState([])
  const [detections, setDetections] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [globalError, setGlobalError] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    setGlobalError('')

    const results = await Promise.allSettled([
      api.health(),
      api.getWanted({ activeOnly: false }),
      api.getDetections(100),
      api.getAlerts({ limit: 100 }),
    ])

    const [healthResult, wantedResult, detectionResult, alertsResult] = results

    if (healthResult.status === 'fulfilled') {
      setHealth(healthResult.value)
    } else {
      setHealth(null)
    }

    if (wantedResult.status === 'fulfilled') {
      setWanted(wantedResult.value.vehicles || [])
    }

    if (detectionResult.status === 'fulfilled') {
      setDetections(detectionResult.value.detections || [])
    }

    if (alertsResult.status === 'fulfilled') {
      setAlerts(alertsResult.value.alerts || [])
    }

    const rejected = results.find((result) => result.status === 'rejected')

    if (rejected) {
      setGlobalError(
        'No fue posible cargar toda la información. Verifica que FastAPI esté encendido.',
      )
    }

    setLoading(false)
  }, [])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('optishield-theme', theme)
  }, [theme])

  useEffect(() => {
    loadData()
  }, [loadData])

  function renderPage() {
    switch (page) {
      case 'detect':
        return <Detect api={api} onDataChanged={loadData} />

      case 'wanted':
        return (
          <Wanted
            vehicles={wanted}
            api={api}
            onDataChanged={loadData}
          />
        )

      case 'detections':
        return (
          <Detections
            detections={detections}
            loading={loading}
            onRefresh={loadData}
          />
        )

      case 'alerts':
        return (
          <Alerts alerts={alerts} api={api} onDataChanged={loadData} />
        )

      default:
        return (
          <Dashboard
            wanted={wanted}
            detections={detections}
            alerts={alerts}
            loading={loading}
            onRefresh={loadData}
          />
        )
    }
  }

  return (
    <Layout
      page={page}
      onPageChange={setPage}
      theme={theme}
      onToggleTheme={() =>
        setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
      }
      sidebarOpen={sidebarOpen}
      setSidebarOpen={setSidebarOpen}
      health={health}
    >
      {globalError && (
        <div className="message message--error">{globalError}</div>
      )}
      {renderPage()}
    </Layout>
  )
}
