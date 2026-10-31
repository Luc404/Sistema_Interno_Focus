import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  IconBook,
  IconCalendar,
  IconCheck,
  IconEye,
  IconEyeOff,
  IconFolder,
  IconGrid,
  IconLayers,
  IconNotebook,
} from './icons'
import ThemePicker from './ThemePicker'

interface LoginProps {
  onLogin: (name: string) => void
}

const modules = [
  { icon: IconGrid, name: 'Focus' },
  { icon: IconFolder, name: 'Arquivos' },
  { icon: IconCalendar, name: 'Agenda' },
  { icon: IconLayers, name: 'Backlog' },
  { icon: IconNotebook, name: 'Notebooks' },
]

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (username.trim()) {
      onLogin(username.trim())
    }
  }

  return (
    <div className="login">
      <div className="login-theme">
        <ThemePicker />
      </div>
      <aside className="login-brand">
        <div className="login-brand-top">
          <div className="logo-mark">
            <IconBook size={22} />
          </div>
          <div className="logo-text">
            <strong>Librarium</strong>
            <span>FOCUS SOLUTIONS</span>
          </div>
        </div>

        <div className="login-brand-copy">
          <h1>Uma só plataforma,<br />todo o sistema interno.</h1>
          <p>
            Arquivos, agenda, backlog, assistentes de IA e documentação —
            centralizados para o seu time Focus.
          </p>
        </div>

        <div className="login-modules">
          {modules.map((m) => {
            const Icon = m.icon
            return (
              <div className="login-module" key={m.name}>
                <Icon size={18} />
                <span>{m.name}</span>
                <IconCheck size={15} className="login-module-check" />
              </div>
            )
          })}
        </div>

        <div className="login-brand-foot">
          <span className="login-dots">
            <i />
            <i />
            <i />
          </span>
          <p>
            Acesse e gerencie tudo em um só lugar.
            <br />
            <strong>Sistema Interno Focus Solutions.</strong>
          </p>
        </div>
      </aside>

      <main className="login-main">
        <div className="login-card">
          <div className="login-card-head">
            <div className="logo-mark dark">
              <IconBook size={22} />
            </div>
            <h2>Login</h2>
            <p>Bem-vindo de volta. Acesse o sistema interno.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Usuário</span>
              <input
                type="text"
                placeholder="Seu nome ou e-mail"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </label>

            <label className="field">
              <span>Senha</span>
              <div className="field-password">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="field-eye"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                  onClick={() => setShowPassword((v) => !v)}
                >
                  {showPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                </button>
              </div>
            </label>

            <div className="login-form-row">
              <label className="remember">
                <input type="checkbox" />
                <span>Manter conectado</span>
              </label>
              <button type="button" className="link">
                Esqueci minha senha
              </button>
            </div>

            <button type="submit" className="btn-primary login-submit" disabled={!username.trim()}>
              Acessar
            </button>
          </form>

          <p className="login-card-foot">
            Acesso restrito a colaboradores da Focus Solutions.
          </p>
        </div>
      </main>
    </div>
  )
}