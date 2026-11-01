import { useEffect, useLayoutEffect, useState } from 'react'
import './App.css'
import { api, clearTokens, getAccessToken } from './api/client'
import type { Usuario } from './api/types'
import Login from './components/Login'
import Shell from './components/Shell'
import { applyTheme, readStoredTheme } from './theme'

/**
 * Raiz da aplicação.
 * Controla a sessão: restaura o usuário a partir do token salvo, exibe o login
 * quando não há sessão válida e delega o restante para o Shell.
 */
function App() {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(true)

  // Aplica o tema salvo antes da primeira pintura para evitar "flash" de cor.
  useLayoutEffect(() => {
    applyTheme(readStoredTheme())
  }, [])

  useEffect(() => {
    let ativo = true

    // Se existe token local, valida com /auth/me antes de mostrar o sistema.
    async function restaurarSessao() {
      if (!getAccessToken()) {
        setCarregando(false)
        return
      }

      try {
        const atual = await api.auth.me()
        if (ativo) setUsuario(atual)
      } catch {
        // Token inválido/expirado: limpa a sessão e volta para o login.
        clearTokens()
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void restaurarSessao()
    return () => {
      ativo = false
    }
  }, [])

  if (carregando) {
    return (
      <div className="app-loading">
        <span className="spinner" />
        Carregando sessão...
      </div>
    )
  }

  if (!usuario) {
    return <Login onLogin={setUsuario} />
  }

  return (
    <Shell
      usuario={usuario}
      onUsuarioAtualizado={setUsuario}
      onLogout={() => {
        clearTokens()
        setUsuario(null)
      }}
    />
  )
}

export default App
