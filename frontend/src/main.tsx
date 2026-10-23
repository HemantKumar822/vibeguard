import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// This import and all example data are eliminated in production builds.
if (import.meta.env.DEV) {
  void import('./DevelopmentFixtures.tsx').then(({ default: DevelopmentFixtures }) => {
    const host = document.createElement('div')
    host.className = 'fixture-host'
    document.body.append(host)
    createRoot(host).render(<DevelopmentFixtures />)
  })
}
