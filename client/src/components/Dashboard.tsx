import { useEffect, useState } from 'react'
import type { ComponentType } from 'react'
import { api, ApiError } from '../api/client'
import type {
  DashboardResumo,
  Setor,
  TarefaPessoal,
  Usuario,
} from '../api/types'
import {
  IconBot,
  IconCalendar,
  IconChart,
  IconChevronRight,
  IconFile,
  IconFolder,
  IconLayers,
  IconNotebook,
  IconRefresh,
  IconUsers,
} from './icons'
import type { Section } from './Shell'

interface DashboardProps {
  /** Usuário autenticado, usado na saudação e no painel de equipe. */
  usuario: Usuario
  onNavigate: (s: Section) => void
}

/** Módulos exibidos no atalho inferior do painel. */
const modules: { id: Section; label: string; desc: string; icon: ComponentType<{ size?: number }> }[] = [
  { id: 'files', label: 'Arquivos', desc: 'Biblioteca de arquivos e links úteis', icon: IconFolder },
  { id: 'calendar', label: 'Agenda', desc: 'Reuniões, tarefas pessoais e mensalidades', icon: IconCalendar },
  { id: 'backlogs', label: 'Backlog', desc: 'Demandas, melhorias e correções do time', icon: IconLayers },
  { id: 'chatbots', label: 'Chatbots', desc: 'Assistentes de IA e automações ativas', icon: IconBot },
  { id: 'notebooks', label: 'Notebooks', desc: 'Documentação e boas práticas internas', icon: IconNotebook },
]

/** Converte um status técnico em texto amigável para a interface. */
function labelStatusTarefa(status: TarefaPessoal['status']): string {
  if (status === 'EM_ANDAMENTO') return 'EM ANDAMENTO'
  if (status === 'CONCLUIDA') return 'CONCLUÍDA'
  return 'PENDENTE'
}

/** Retorna a classe visual do pill conforme o status da tarefa. */
function pillTarefa(status: TarefaPessoal['status']): string {
  if (status === 'EM_ANDAMENTO') return 'pill-blue'
  if (status === 'CONCLUIDA') return 'pill-green'
  return 'pill-amber'
}

/** Formata apenas o horário de uma data ISO. */
function hora(iso: string): string {
  return new Date(iso).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Formata dia e mês abreviado de uma data ISO. */
function diaMes(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
  })
}

export default function Dashboard({ usuario, onNavigate }: DashboardProps) {
  const [resumo, setResumo] = useState<DashboardResumo | null>(null)
  const [tarefas, setTarefas] = useState<TarefaPessoal[]>([])
  const [setores, setSetores] = useState<Setor[]>([])
  const [erro, setErro] = useState<string | null>(null)
  const [carregando, setCarregando] = useState(true)

  // Carrega em paralelo os indicadores, as tarefas do usuário e os setores.
  useEffect(() => {
    let ativo = true

    async function carregar() {
      setCarregando(true)
      setErro(null)

      try {
        const [dadosResumo, paginaTarefas, paginaSetores] = await Promise.all([
          api.dashboard.resumo(),
          api.tarefas.minhas({ limit: 5 }),
          api.setores.list({ limit: 6, status: 'ATIVO' }),
        ])

        if (!ativo) return
        setResumo(dadosResumo)
        setTarefas(paginaTarefas.items)
        setSetores(paginaSetores.items)
      } catch (error) {
        if (!ativo) return
        setErro(
          error instanceof ApiError
            ? error.message
            : 'Não foi possível carregar o painel.',
        )
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void carregar()
    return () => {
      ativo = false
    }
  }, [])

  const primeiroNome = usuario.nome_completo.split(' ')[0]

  const stats = [
    {
      icon: IconCalendar,
      label: 'Reuniões hoje',
      value: resumo?.reunioes_hoje ?? 0,
      tone: 'violet',
    },
    {
      icon: IconChart,
      label: 'Mensalidades pendentes',
      value: resumo?.mensalidades_pendentes ?? 0,
      tone: 'amber',
    },
    {
      icon: IconFile,
      label: 'Arquivos na biblioteca',
      value: resumo?.arquivos ?? 0,
      tone: 'blue',
    },
    {
      icon: IconLayers,
      label: 'Itens no backlog',
      value: resumo?.itens_backlog ?? 0,
      tone: 'green',
    },
  ]

  if (carregando) {
    return (
      <div className="page home-page">
        <div className="empty-state">
          <span className="spinner" />
          Carregando painel...
        </div>
      </div>
    )
  }

  if (erro) {
    return (
      <div className="page home-page">
        <div className="empty-state">
          <p className="form-error" role="alert">
            {erro}
          </p>
          <button className="btn-ghost" onClick={() => window.location.reload()}>
            <IconRefresh size={16} /> Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="page home-page">
      <div className="home-hero">
        <div>
          <span className="eyebrow">Sistema Interno</span>
          <h2>Olá, {primeiroNome}. 👋</h2>
          <p>Veja o que está acontecendo hoje na Focus Solutions.</p>
        </div>
        <div className="home-hero-badge">
          <span className="status-dot on" />
          Todos os sistemas operando
        </div>
      </div>

      <section className="stats-grid">
        {stats.map((stat) => {
          const Icone = stat.icon
          return (
            <div className="stat-card" key={stat.label}>
              <div className={`stat-icon tone-${stat.tone}`}>
                <Icone size={20} />
              </div>
              <div>
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
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
            {resumo?.proximas_reunioes.length === 0 && (
              <div className="empty-inline">Nenhuma reunião agendada.</div>
            )}
            {resumo?.proximas_reunioes.map((reuniao) => (
              <div className="list-row" key={reuniao.id}>
                <div className="time-chip">{hora(reuniao.data_hora_inicio)}</div>
                <div className="list-row-body">
                  <strong>{reuniao.titulo}</strong>
                  <span>{diaMes(reuniao.data_hora_inicio)} · Reunião</span>
                </div>
                <span className="chip">Reunião</span>
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
            {tarefas.length === 0 && (
              <div className="empty-inline">Nenhuma tarefa cadastrada.</div>
            )}
            {tarefas.map((tarefa) => (
              <div className="list-row" key={tarefa.id}>
                <span
                  className={`checkbox${tarefa.status === 'CONCLUIDA' ? ' checked' : ''}`}
                  aria-hidden="true"
                />
                <div className="list-row-body">
                  <strong className={tarefa.status === 'CONCLUIDA' ? 'strike' : ''}>
                    {tarefa.titulo}
                  </strong>
                </div>
                <span className={`pill ${pillTarefa(tarefa.status)}`}>
                  {labelStatusTarefa(tarefa.status)}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <h3>Equipe</h3>
            <button className="link" onClick={() => onNavigate('calendar')}>
              Gerenciar <IconChevronRight size={15} />
            </button>
          </div>
          <div className="team">
            <div className="team-avatars">
              {setores.slice(0, 4).map((setor) => (
                <span className="avatar" key={setor.id}>
                  {setor.nome.charAt(0).toUpperCase()}
                </span>
              ))}
              {setores.length > 4 && (
                <span className="avatar avatar-more">+{setores.length - 4}</span>
              )}
            </div>
            <div className="team-meta">
              <strong>{resumo?.usuarios_ativos ?? 0} colaboradores ativos</strong>
              <span>
                <IconUsers size={15} /> Distribuídos em {resumo?.setores_ativos ?? 0} setores
              </span>
            </div>
          </div>
          <div className="team-setores">
            {setores.length === 0 && (
              <span className="muted">Nenhum setor ativo cadastrado.</span>
            )}
            {setores.map((setor, indice) => (
              <span className="chip" key={setor.id}>
                <i className={`dot-${['violet', 'blue', 'green', 'amber'][indice % 4]}`} />{' '}
                {setor.nome}
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
          {modules.map((modulo) => {
            const Icone = modulo.icon
            return (
              <button
                className="module-card"
                key={modulo.id}
                onClick={() => onNavigate(modulo.id)}
              >
                <span className="module-icon">
                  <Icone size={22} />
                </span>
                <strong>{modulo.label}</strong>
                <span>{modulo.desc}</span>
                <IconChevronRight className="module-arrow" size={18} />
              </button>
            )
          })}
        </div>
      </section>
    </div>
  )
}
