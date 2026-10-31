import { useState } from 'react'
import type { ComponentType } from 'react'
import type { Usuario } from '../api/types'
import {
  IconBell,
  IconBook,
  IconBot,
  IconCalendar,
  IconFolder,
  IconGrid,
  IconLayers,
  IconLogout,
  IconNotebook,
  IconSearch,
} from './icons'
import Dashboard from './Dashboard'
import Librarium from './Librarium'
import CalendarView from './CalendarView'
import Backlogs from './Backlogs'
import Chatbots from './Chatbots'
import Notebooks from './Notebooks'
import ThemePicker from './ThemePicker'

export type Section = 'home' | 'files' | 'calendar' | 'backlogs' | 'chatbots' | 'notebooks'

interface ShellProps {
  /** Usuário autenticado, usado no cabeçalho e no controle de permissões. */
  usuario: Usuario
  onLogout: () => void
}

const nav: { id: Section; label: string; icon: ComponentType<{ size?: number }> }[] = [
  { id: 'home', label: 'Início', icon: IconGrid },
  { id: 'files', label: 'Arquivos', icon: IconFolder },
  { id: 'calendar', label: 'Agenda', icon: IconCalendar },
  { id: 'backlogs', label: 'Backlog', icon: IconLayers },
  { id: 'chatbots', label: 'Chatbots', icon: IconBot },
  { id: 'notebooks', label: 'Notebooks', icon: IconNotebook },
]

const meta: Record<Section, { title: string; subtitle: string; placeholder: string }> = {
  home: { title: 'Painel', subtitle: 'Visão geral do sistema interno', placeholder: 'Pesquisar em todo o sistema' },
  files: { title: 'Librarium', subtitle: 'Biblioteca de arquivos e links', placeholder: 'Search system wide' },
  calendar: { title: 'Agenda', subtitle: 'Reuniões, tarefas e mensalidades', placeholder: 'Pesquisar compromissos' },
  backlogs: { title: 'Backlog', subtitle: 'Demandas, melhorias e correções', placeholder: 'Pesquisar itens do backlog' },
  chatbots: { title: 'Assistente IA', subtitle: 'Bots ativos do Focus', placeholder: 'Search bots' },
  notebooks: { title: 'Notebooks', subtitle: 'Documentação interna', placeholder: 'Search notebooks' },
}

export default function Shell({ usuario, onLogout }: ShellProps) {
  const [section, setSection] = useState<Section>('home')

  const initial = usuario.nome_completo.charAt(0).toUpperCase()

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="logo-mark">
            <IconBook size={22} />
          </div>
          <div className="logo-text">
            <strong>Librarium</strong>
            <span>FOCUS SOLUTIONS</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <span className="sidebar-label">Módulos</span>
          {nav.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                className={`nav-item${section === item.id ? ' active' : ''}`}
                onClick={() => setSection(item.id)}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="sidebar-foot">
          <div className="sidebar-user">
            <span className="avatar">{initial}</span>
            <div className="sidebar-user-info">
              <strong>{usuario.nome_completo}</strong>
              <span>{usuario.perfil === 'ADMIN' ? 'Administrador' : 'Membro'}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={onLogout}>
            <IconLogout size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <div className="shell-main">
        <header className="topbar">
          <div className="topbar-title">
            <h1>{meta[section].title}</h1>
            <p>{meta[section].subtitle}</p>
          </div>

          <div className="topbar-actions">
            <label className="search-bar">
              <IconSearch size={17} />
              <input type="text" placeholder={meta[section].placeholder} />
              <kbd>Ctrl K</kbd>
            </label>
            <button className="icon-btn" aria-label="Notificações">
              <IconBell size={19} />
              <i className="icon-btn-dot" />
            </button>
            <ThemePicker />
            <span className="avatar">{initial}</span>
          </div>
        </header>

        <main className="content">
          {section === 'home' && (
            <Dashboard usuario={usuario} onNavigate={setSection} />
          )}
          {section === 'files' && <Librarium />}
          {section === 'calendar' && <CalendarView />}
          {section === 'backlogs' && <Backlogs />}
          {section === 'chatbots' && <Chatbots />}
          {section === 'notebooks' && <Notebooks />}
        </main>
      </div>
    </div>
  )
}