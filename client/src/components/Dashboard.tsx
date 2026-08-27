import type { ComponentType } from 'react'
import {
  IconBot,
  IconCalendar,
  IconChart,
  IconChevronRight,
  IconFile,
  IconFolder,
  IconLayers,
  IconNotebook,
  IconUsers,
} from './icons'
import type { Section } from './Shell'

interface DashboardProps {
  user: string
  onNavigate: (s: Section) => void
}

const stats = [
  { icon: IconCalendar, label: 'Reuniões hoje', value: '4', tone: 'violet' },
  { icon: IconChart, label: 'Mensalidades pendentes', value: '7', tone: 'amber' },
  { icon: IconFile, label: 'Arquivos na biblioteca', value: '182', tone: 'blue' },
  { icon: IconLayers, label: 'Itens no backlog', value: '36', tone: 'green' },
]

const modules: { id: Section; label: string; desc: string; icon: ComponentType<{ size?: number }> }[] = [
  { id: 'files', label: 'Arquivos', desc: 'Biblioteca de arquivos e links úteis', icon: IconFolder },
  { id: 'calendar', label: 'Agenda', desc: 'Reuniões, tarefas pessoais e mensalidades', icon: IconCalendar },
  { id: 'backlogs', label: 'Backlog', desc: 'Demandas, melhorias e correções do time', icon: IconLayers },
  { id: 'chatbots', label: 'Chatbots', desc: 'Assistentes de IA e automações ativas', icon: IconBot },
  { id: 'notebooks', label: 'Notebooks', desc: 'Documentação e boas práticas internas', icon: IconNotebook },
]

const meetings = [
  { time: '09:30', title: 'Daily — Equipe de desenvolvimento', who: 'Backend · 6 participantes', tag: 'Reunião' },
  { time: '11:00', title: 'Review de mensalidades — Clientes', who: 'Financeiro · 3 participantes', tag: 'Reunião' },
  { time: '14:30', title: 'Planejamento do backlog da sprint', who: 'Produto · 8 participantes', tag: 'Reunião' },
]

const tasks = [
  { title: 'Revisar migração de banco de dados', status: 'EM ANDAMENTO' },
  { title: 'Subir relatório de vendas de agosto', status: 'PENDENTE' },
  { title: 'Atualizar pasta de contratos 2026', status: 'CONCLUÍDA' },
]

export default function Dashboard({ user, onNavigate }: DashboardProps) {
  const firstName = user.split(' ')[0]

  return (
    <div className="page home-page">
      <div className="home-hero">
        <div>
          <span className="eyebrow">Sistema Interno</span>
          <h2>Olá, {firstName}. 👋</h2>
          <p>Veja o que está acontecendo hoje na Focus Solutions.</p>
        </div>
        <div className="home-hero-badge">
          <span className="status-dot on" />
          Todos os sistemas operando
        </div>
      </div>

      <section className="stats-grid">
        {stats.map((s) => {
          const Icon = s.icon
          return (
            <div className="stat-card" key={s.label}>
              <div className={`stat-icon tone-${s.tone}`}>
                <Icon size={20} />
              </div>
              <div>
                <span>{s.label}</span>
                <strong>{s.value}</strong>
              </div>
            </div>
          )
        })}
      </section>

      <div className="home-columns">
        <section className="panel">
          <div className="panel-head">
            <h3>Próximas reuniões</h3>
            <button className="link" onClick={() => onNavigate('calendar')}>
              Ver agenda <IconChevronRight size={15} />
            </button>
          </div>
          <div className="list">
            {meetings.map((m) => (
              <div className="list-row" key={m.title}>
                <div className="time-chip">{m.time}</div>
                <div className="list-row-body">
                  <strong>{m.title}</strong>
                  <span>{m.who}</span>
                </div>
                <span className="chip">{m.tag}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <h3>Minhas tarefas</h3>
            <button className="link" onClick={() => onNavigate('calendar')}>
              Ver todas <IconChevronRight size={15} />
            </button>
          </div>
          <div className="list">
            {tasks.map((t) => (
              <div className="list-row" key={t.title}>
                <span className="checkbox" aria-hidden="true" />
                <div className="list-row-body">
                  <strong>{t.title}</strong>
                </div>
                <span className={`pill pill-${t.status === 'EM ANDAMENTO' ? 'blue' : t.status === 'CONCLUÍDA' ? 'green' : 'amber'}`}>
                  {t.status}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <h3>Equipe</h3>
            <button className="link">
              Gerenciar <IconChevronRight size={15} />
            </button>
          </div>
          <div className="team">
            <div className="team-avatars">
              <span className="avatar">M</span>
              <span className="avatar">R</span>
              <span className="avatar">A</span>
              <span className="avatar">P</span>
              <span className="avatar avatar-more">+3</span>
            </div>
            <div className="team-meta">
              <strong>12 colaboradores ativos</strong>
              <span>
                <IconUsers size={15} /> Distribuídos em 4 setores
              </span>
            </div>
          </div>
          <div className="team-setores">
            {['Desenvolvimento', 'Financeiro', 'Atendimento', 'Comercial'].map((s, i) => (
              <span className="chip" key={s}>
                <i className={`dot-${['violet', 'blue', 'green', 'amber'][i]}`} /> {s}
              </span>
            ))}
          </div>
        </section>
      </div>

      <section className="panel modules-panel">
        <div className="panel-head">
          <h3>Módulos</h3>
          <span className="muted">Acesse rapidamente</span>
        </div>
        <div className="modules-grid">
          {modules.map((m) => {
            const Icon = m.icon
            return (
              <button className="module-card" key={m.id} onClick={() => onNavigate(m.id)}>
                <span className="module-icon">
                  <Icon size={22} />
                </span>
                <strong>{m.label}</strong>
                <span>{m.desc}</span>
                <IconChevronRight className="module-arrow" size={18} />
              </button>
            )
          })}
        </div>
      </section>
    </div>
  )
}