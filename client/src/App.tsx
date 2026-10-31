import { useLayoutEffect, useState } from 'react'
import './App.css'
import Login from './components/Login'
import Shell from './components/Shell'
import { applyTheme, readStoredTheme } from './theme'

function App() {
  const [user, setUser] = useState<string | null>(null)

  useLayoutEffect(() => {
    applyTheme(readStoredTheme())
  }, [])

  if (!user) {
    return <Login onLogin={setUser} />
  }

  return <Shell user={user} onLogout={() => setUser(null)} />
}

export default App