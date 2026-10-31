import { useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError, saveTokens } from '../api/client'
import type { Usuario } from '../api/types'
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
  /** Chamado após autenticar e carregar os dados do usuário. */
  onLogin: (usuario: Usuario) => void
}

/** Módulos exibidos no painel lateral ilustrativo da tela de login. */
const modules = [
  { icon: IconGrid, name: 'Focus' },
  { icon: IconFolder, name: 'Arquivos' },
  { icon: IconCalendar, name: 'Agenda' },
  { icon: IconLayers, name: 'Backlog' },
  { icon: IconNotebook, name: 'Notebooks' },
]

export default function Login({ onLogin }: LoginProps) {
  const [modoRegistro, setModoRegistro] = useState(false)
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [carregando, setCarregando] = useState(false)

  /** Alterna entre login e criação do primeiro administrador. */
  function alternarModo() {
    setModoRegistro((valor) => !valor)
    setErro(null)
    setNome('')
    setSenha('')
  }

  async function handleSubmit(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const emailLimpo = email.trim()
    if (!emailLimpo || !senha || (modoRegistro && !nome.trim())) return

    setErro(null)
    setCarregando(true)

    try {
      // O backend só permite o cadastro público enquanto o banco estiver vazio.
      if (modoRegistro) {
        await api.auth.registrar({
          nome_completo: nome.trim(),
          email: emailLimpo,
          senha,
          perfil: 'ADMIN',
        })
      }

      const tokens = await api.auth.login(emailLimpo, senha)
      saveTokens(tokens)

      // O login devolve apenas tokens; buscamos o perfil em /auth/me.
      const usuario = await api.auth.me()
      onLogin(usuario)
    } catch (error) {
      setErro(
        error instanceof ApiError
          ? error.message
          : 'Não foi possível acessar o sistema. Tente novamente.',
      )
    } finally {
      setCarregando(false)
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
          <h1>
            Uma só plataforma,
            <br />
            todo o sistema interno.
          </h1>
          <p>
            Arquivos, agenda, backlog, assistentes de IA e documentação —
            centralizados para o seu time Focus.
          </p>
        </div>

        <div className="login-modules">
          {modules.map((modulo) => {
            const Icone = modulo.icon
            return (
              <div className="login-module" key={modulo.name}>
                <Icone size={18} />
                <span>{modulo.name}</span>
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
            <h2>{modoRegistro ? 'Primeiro acesso' : 'Login'}</h2>
            <p>
              {modoRegistro
                ? 'Crie o administrador inicial do sistema.'
                : 'Bem-vindo de volta. Acesse o sistema interno.'}
            </p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            {modoRegistro && (
              <label className="field">
                <span>Nome completo</span>
                <input
                  type="text"
                  placeholder="Seu nome completo"
                  autoComplete="name"
                  value={nome}
                  onChange={(evento) => setNome(evento.target.value)}
                />
              </label>
            )}

            <label className="field">
              <span>E-mail</span>
              <input
                type="email"
                placeholder="voce@focus.com"
                autoComplete="username"
                value={email}
                onChange={(evento) => setEmail(evento.target.value)}
              />
            </label>

            <label className="field">
              <span>Senha</span>
              <div className="field-password">
                <input
                  type={mostrarSenha ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete={modoRegistro ? 'new-password' : 'current-password'}
                  value={senha}
                  onChange={(evento) => setSenha(evento.target.value)}
                />
                <button
                  type="button"
                  className="field-eye"
                  aria-label={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
                  onClick={() => setMostrarSenha((valor) => !valor)}
                >
                  {mostrarSenha ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                </button>
              </div>
            </label>

            {erro && (
              <p className="form-error" role="alert">
                {erro}
              </p>
            )}

            <div className="login-form-row">
              <span className="muted login-hint">
                {modoRegistro
                  ? 'Disponível apenas enquanto não houver usuários.'
                  : 'Sessão protegida por token JWT.'}
              </span>
              <button type="button" className="link" onClick={alternarModo}>
                {modoRegistro ? 'Já tenho conta' : 'Primeiro acesso'}
              </button>
            </div>

            <button
              type="submit"
              className="btn-primary login-submit"
              disabled={
                carregando ||
                !email.trim() ||
                !senha ||
                (modoRegistro && !nome.trim())
              }
            >
              {carregando
                ? modoRegistro
                  ? 'Criando administrador...'
                  : 'Entrando...'
                : modoRegistro
                  ? 'Criar administrador'
                  : 'Acessar'}
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
