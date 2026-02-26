import * as React from 'react'
const { StrictMode, Component } = React
type ReactNode = React.ReactNode
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

class ErrorBoundary extends Component<{ children: ReactNode }, { err: Error | null }> {
  state = { err: null as Error | null }
  static getDerivedStateFromError(e: Error) { return { err: e } }
  componentDidCatch(e: Error, info: React.ErrorInfo) {
    console.error('App error:', e, info.componentStack)
  }
  render() {
    if (this.state.err) {
      return (
        <div style={{ padding: '1.5rem', fontFamily: 'system-ui', color: '#c00', maxWidth: 600 }}>
          <h2>App error</h2>
          <pre style={{ whiteSpace: 'pre-wrap', background: '#f5f5f5', padding: '1rem' }}>
            {this.state.err.message}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}

function showError(msg: string) {
  const root = document.getElementById('root')
  if (root) {
    root.innerHTML = '<div style="padding:1.5rem;font-family:system-ui;color:#c00;"><h2>App failed to load</h2><pre style="white-space:pre-wrap;">' + msg.replace(/</g, '&lt;') + '</pre></div>'
  }
}

try {
  const el = document.getElementById('root')
  if (!el) {
    showError('Root element not found.')
  } else {
    createRoot(el).render(
      <StrictMode>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </StrictMode>,
    )
  }
} catch (e) {
  showError(e instanceof Error ? e.message : String(e))
}
