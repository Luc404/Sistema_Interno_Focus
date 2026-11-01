import { useEffect, useRef, useState } from 'react'
import type { ComponentType, FormEvent } from 'react'
import { api } from '../api/client'
import type { Notificacao, ResultadoBusca, Usuario } from '../api/types'
import {
  IconBell,
  IconBook,
  IconBot,
  IconCalendar,
  IconCheck,
  IconFolder,
  IconGrid,
  IconLayers,
  IconLogout,
  IconNotebook,
  IconRefresh,
  IconSearch,
  IconTrash,
  IconX,
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

/** Itens fixos da navegação lateral. */
const nav: { id: Section; label: string; icon: ComponentType<{ size?: number }> }[] = [
  { id: 'home', label: 'Início', icon: IconGrid },
  { id: 'files', label: 'Arquivos', icon: IconFolder },
  { id: 'calendar', label: 'Agenda', icon: IconCalendar },
  { id: 'backlogs', label: 'Backlog', icon: IconLayers },
  { id: 'chatbots', label: 'Chatbots', icon: IconBot },
  { id: 'notebooks', label: 'Notebooks', icon: IconNotebook },
]

/** Título, subtítulo e placeholder de busca de cada seção. */
const meta: Record<Section, { title: string; subtitle: string; placeholder: string }> = {
  home: {
    title: 'Painel',
    subtitle: 'Visão geral do sistema interno',
    placeholder: 'Pesquisar em todo o sistema',
  },
  files: {
    title: 'Librarium',
    subtitle: 'Biblioteca de arquivos e links',
    placeholder: 'Pesquisar arquivos e links',
  },
  calendar: {
    title: 'Agenda',
    subtitle: 'Reuniões, tarefas e mensalidades',
    placeholder: 'Pesquisar compromissos',
  },
  backlogs: {
    title: 'Backlog',
    subtitle: 'Demandas, melhorias e correções',
    placeholder: 'Pesquisar itens do backlog',
  },
  chatbots: {
    title: 'Assistente IA',
    subtitle: 'Bots ativos do Focus',
    placeholder: 'Pesquisar bots',
  },
  notebooks: {
    title: 'Notebooks',
    subtitle: 'Documentação interna',
    placeholder: 'Pesquisar notebooks',
  },
}

/** Converte o tipo retornado pela busca global para a seção correspondente. */
function secaoDoResultado(tipo: string): Section | null {
  switch (tipo) {
    case 'arquivo':
    case 'link':
      return 'files'
    case 'backlog':
      return 'backlogs'
    case 'reuniao':
    case 'tarefa':
    case 'mensalidade':
      return 'calendar'
    case 'notebook':
      return 'notebooks'
    default:
      return null
  }
}

/** Converte o link de uma notificação em uma seção interna. */
function secaoDoLink(link: string | null): Section | null {
  if (!link) return null
  if (link.includes('agenda') || link.includes('reuniao')) return 'calendar'
  if (link.includes('backlog')) return 'backlogs'
  if (link.includes('arquivo') || link.includes('biblioteca')) return 'files'
  if (link.includes('notebook')) return 'notebooks'
  if (link.includes('chat')) return 'chatbots'
  return null
}

/** Formata a data de uma notificação de forma curta. */
function dataCurta(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function Shell({ usuario, onLogout }: ShellProps) {
  const [section, setSection] = useState<Section>('home')

  // Busca global
  const [termo, setTermo] = useState('')
  const [resultados, setResultados] = useState<ResultadoBusca[]>([])
  const [buscando, setBuscando] = useState(false)
  const [buscaAberta, setBuscaAberta] = useState(false)
  const [erroBusca, setErroBusca] = useState<string | null>(null)

  // Notificações
  const [notificacoes, setNotificacoes] = useState<Notificacao[]>([])
  const [notificacoesAbertas, setNotificacoesAbertas] = useState(false)
  const [carregandoNotificacoes, setCarregandoNotificacoes] = useState(false)

  const buscaRef = useRef<HTMLDivElement>(null)
  const notificacoesRef = useRef<HTMLDivElement>(null)

  const inicial = usuario.nome_completo.charAt(0).toUpperCase()
  const naoLidas = notificacoes.filter((item) => !item.lida).length

  // Fecha os popovers ao clicar fora ou pressionar Escape.
  useEffect(() => {
    function aoClicar(evento: MouseEvent) {
      const alvo = evento.target as Node
      if (buscaRef.current && !buscaRef.current.contains(alvo)) setBuscaAberta(false)
      if (notificacoesRef.current && !notificacoesRef.current.contains(alvo)) {
        setNotificacoesAbertas(false)
      }
    }

    function aoPressionar(evento: KeyboardEvent) {
      if (evento.key === 'Escape') {
        setBuscaAberta(false)
        setNotificacoesAbertas(false)
      }
    }

    document.addEventListener('mousedown', aoClicar)
    document.addEventListener('keydown', aoPressionar)
    return () => {
      document.removeEventListener('mousedown', aoClicar)
      document.removeEventListener('keydown', aoPressionar)
    }
  }, [])

  // Carrega as notificações do usuário ao montar o shell.
  useEffect(() => {
    let ativo = true

    async function carregar() {
      setCarregandoNotificacoes(true)
      try {
        const pagina = await api.notificacoes.minhas({ limit: 10 })
        if (ativo) setNotificacoes(pagina.items)
      } catch {
        // Falha silenciosa: o sino simplesmente fica sem itens.
      } finally {
        if (ativo) setCarregandoNotificacoes(false)
      }
    }

    void carregar()
    return () => {
      ativo = false
    }
  }, [])

  // Busca com debounce para não disparar uma requisição a cada tecla.
  useEffect(() => {
    const limpo = termo.trim()
    if (!limpo) {
      setResultados([])
      setBuscaAberta(false)
      setErroBusca(null)
      return
    }

    let cancelado = false
    const timer = window.setTimeout(async () => {
      setBuscando(true)
      setErroBusca(null)
      setBuscaAberta(true)

      try {
        const resposta = await api.busca(limpo)
        if (!cancelado) setResultados(resposta.resultados)
      } catch {
        if (!cancelado) {
          setResultados([])
          setErroBusca('Não foi possível realizar a busca.')
        }
      } finally {
        if (!cancelado) setBuscando(false)
      }
    }, 350)

    return () => {
      cancelado = true
      window.clearTimeout(timer)
    }
  }, [termo])

  /** Impede o recarregamento da página ao submeter a busca. */
  function submeterBusca(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setBuscaAberta(true)
  }

  /** Navega para a seção correspondente ao resultado da busca. */
  function abrirResultado(resultado: ResultadoBusca) {
    const destino = secaoDoResultado(resultado.tipo)
    if (destino) setSection(destino)
    setBuscaAberta(false)
    setTermo('')
    setResultados([])
  }

  /** Marca uma notificação como lida e navega para o link, se houver. */
  async function abrirNotificacao(notificacao: Notificacao) {
    if (!notificacao.lida) {
      try {
        await api.notificacoes.ler(notificacao.id)
        setNotificacoes((itens) =>
          itens.map((item) =>
            item.id === notificacao.id ? { ...item, lida: true } : item,
          ),
        )
      } catch {
        // Mesmo se falhar, permitimos a navegação.
      }
    }

    const destino = secaoDoLink(notificacao.link)
    if (destino) setSection(destino)
    setNotificacoesAbertas(false)
  }

  /** Marca todas as notificações como lidas. */
  async function marcarTodasComoLidas() {
    try {
      await api.notificacoes.lerTodas()
      setNotificacoes((itens) => itens.map((item) => ({ ...item, lida: true })))
    } catch {
      // Mantém o estado atual em caso de falha.
    }
  }

  /** Remove uma notificação da lista. */
  async function excluirNotificacao(id: number) {
    try {
      await api.notificacoes.remove(id)
      setNotificacoes((itens) => itens.filter((item) => item.id !== id))
    } catch {
      // Mantém o item se a exclusão falhar.
    }
  }

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
            const Icone = item.icon
            return (
              <button
                key={item.id}
                className={`nav-item${section === item.id ? ' active' : ''}`}
                onClick={() => setSection(item.id)}
              >
                <Icone size={19} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="sidebar-foot">
          <div className="sidebar-user">
            <span className="avatar">{inicial}</span>
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
            <div className="search-wrapper" ref={buscaRef}>
              <form className="search-bar" onSubmit={submeterBusca}>
                <IconSearch size={17} />
                <input
                  type="search"
                  placeholder={meta[section].placeholder}
                  value={termo}
                  onChange={(evento) => setTermo(evento.target.value)}
                  onFocus={() => {
                    if (termo.trim()) setBuscaAberta(true)
                  }}
                  aria-label="Busca global"
                />
                <kbd>Ctrl K</kbd>
              </form>

              {buscaAberta && (
                <div className="search-results" role="listbox">
                  {buscando && (
                    <div className="search-status">
                      <span className="spinner" /> Buscando...
                    </div>
                  )}
                  {!buscando && erroBusca && (
                    <div className="search-status">{erroBusca}</div>
                  )}
                  {!buscando && !erroBusca && resultados.length === 0 && (
                    <div className="search-status">Nenhum resultado encontrado.</div>
                  )}
                  {!buscando &&
                    resultados.map((resultado) => (
                      <button
                        className="search-result"
                        key={`${resultado.tipo}-${resultado.id}`}
                        onClick={() => abrirResultado(resultado)}
                        role="option"
                      >
                        <span className="search-result-type">{resultado.tipo}</span>
                        <span className="search-result-body">
                          <strong>{resultado.titulo}</strong>
                          {resultado.descricao && <span>{resultado.descricao}</span>}
                        </span>
                      </button>
                    ))}
                </div>
              )}
            </div>

            <div className="notifications-wrapper" ref={notificacoesRef}>
              <button
                className="icon-btn"
                aria-label="Notificações"
                aria-expanded={notificacoesAbertas}
                onClick={() => setNotificacoesAbertas((valor) => !valor)}
              >
                <IconBell size={19} />
                {naoLidas > 0 && <i className="icon-btn-dot" />}
              </button>

              {notificacoesAbertas && (
                <div className="notifications-pop">
                  <div className="notifications-head">
                    <div>
                      <strong>Notificações</strong>
                      <span className="muted">{naoLidas} não lida(s)</span>
                    </div>
                    {naoLidas > 0 && (
                      <button className="link" onClick={marcarTodasComoLidas}>
                        <IconCheck size={14} /> Marcar todas
                      </button>
                    )}
                  </div>

                  <div className="notifications-list">
                    {carregandoNotificacoes && (
                      <div className="search-status">
                        <span className="spinner" /> Carregando...
                      </div>
                    )}
                    {!carregandoNotificacoes && notificacoes.length === 0 && (
                      <div className="search-status">Nenhuma notificação.</div>
                    )}
                    {!carregandoNotificacoes &&
                      notificacoes.map((notificacao) => (
                        <div
                          className={`notification-item${notificacao.lida ? '' : ' unread'}`}
                          key={notificacao.id}
                        >
                          <button
                            className="notification-body"
                            onClick={() => abrirNotificacao(notificacao)}
                          >
                            <strong>{notificacao.titulo}</strong>
                            <span>{notificacao.mensagem}</span>
                            <em>{dataCurta(notificacao.data_criacao)}</em>
                          </button>
                          <button
                            className="icon-btn sm danger"
                            aria-label="Excluir notificação"
                            onClick={() => excluirNotificacao(notificacao.id)}
                          >
                            <IconTrash size={14} />
                          </button>
                        </div>
                      ))}
                  </div>

                  <div className="notifications-foot">
                    <button
                      className="link"
                      onClick={() => {
                        setNotificacoesAbertas(false)
                        setSection('home')
                      }}
                    >
                      <IconRefresh size={14} /> Atualizar painel
                    </button>
                    <button
                      className="icon-btn sm"
                      aria-label="Fechar notificações"
                      onClick={() => setNotificacoesAbertas(false)}
                    >
                      <IconX size={14} />
                    </button>
                  </div>
                </div>
              )}
            </div>

            <ThemePicker />
            <span className="avatar">{inicial}</span>
          </div>
        </header>

        <main className="content">
          {section === 'home' && (
            <Dashboard usuario={usuario} onNavigate={setSection} />
          )}
          {section === 'files' && <Librarium usuario={usuario} />}
          {section === 'calendar' && <CalendarView />}
          {section === 'backlogs' && <Backlogs />}
          {section === 'chatbots' && <Chatbots />}
          {section === 'notebooks' && <Notebooks />}
        </main>
      </div>
    </div>
  )
}
