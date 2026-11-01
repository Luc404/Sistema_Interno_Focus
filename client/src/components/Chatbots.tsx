import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import type { ChatMensagem, Chatbot, StatusChatbot, Usuario } from '../api/types'
import Modal from './Modal'
import {
  IconBot,
  IconDots,
  IconPlus,
  IconRefresh,
  IconSend,
  IconTrash,
} from './icons'

interface ChatbotsProps {
  /** Usuário autenticado, usado no avatar das mensagens e permissões. */
  usuario: Usuario
}

/** Converte um erro desconhecido em mensagem legível. */
function mensagemDeErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao
}

/** Rótulo amigável do status do bot. */
function rotuloStatus(status: StatusChatbot): string {
  switch (status) {
    case 'ACTIVE':
      return 'Ativo'
    case 'ONLINE':
      return 'Online'
    case 'IDLE':
      return 'Ocioso'
    default:
      return 'Offline'
  }
}

/** Classe da pill de acordo com o status. */
function classeStatus(status: StatusChatbot): string {
  switch (status) {
    case 'ACTIVE':
      return 'violet'
    case 'ONLINE':
      return 'green'
    case 'IDLE':
      return 'amber'
    default:
      return 'red'
  }
}

/** Formata a data de criação de um bot. */
function formatarData(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export default function Chatbots({ usuario }: ChatbotsProps) {
  const [bots, setBots] = useState<Chatbot[]>([])
  const [selecionadoId, setSelecionadoId] = useState<number | null>(null)
  const [mensagens, setMensagens] = useState<ChatMensagem[]>([])
  const [carregandoBots, setCarregandoBots] = useState(true)
  const [carregandoMensagens, setCarregandoMensagens] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [versao, setVersao] = useState(0)

  const [input, setInput] = useState('')
  const [pensando, setPensando] = useState(false)
  const corpoRef = useRef<HTMLDivElement>(null)
  const idTemporarioRef = useRef(-1)

  // Formulário de criação/edição de bot
  const [modalBot, setModalBot] = useState(false)
  const [editando, setEditando] = useState<Chatbot | null>(null)
  const [nome, setNome] = useState('')
  const [descricao, setDescricao] = useState('')
  const [versaoBot, setVersaoBot] = useState('v1.0')
  const [modelo, setModelo] = useState('gpt-4o')
  const [status, setStatus] = useState<StatusChatbot>('OFFLINE')
  const [salvando, setSalvando] = useState(false)
  const [erroFormulario, setErroFormulario] = useState<string | null>(null)

  const ehAdmin = usuario.perfil === 'ADMIN'
  const selecionado = bots.find((bot) => bot.id === selecionadoId) ?? null

  // Carrega a lista de bots.
  useEffect(() => {
    let ativo = true

    async function carregarBots() {
      setCarregandoBots(true)
      setErro(null)

      try {
        const pagina = await api.chatbots.list({ limit: 200 })
        if (!ativo) return

        setBots(pagina.items)
        setSelecionadoId((atual) => {
          if (atual && pagina.items.some((bot) => bot.id === atual)) return atual
          return pagina.items[0]?.id ?? null
        })
      } catch (falha) {
        if (ativo) setErro(mensagemDeErro(falha, 'Não foi possível carregar os chatbots.'))
      } finally {
        if (ativo) setCarregandoBots(false)
      }
    }

    void carregarBots()
    return () => {
      ativo = false
    }
  }, [versao])

  // Carrega o histórico do bot selecionado.
  useEffect(() => {
    if (!selecionadoId) return

    let ativo = true

    async function carregarMensagens() {
      setCarregandoMensagens(true)

      try {
        const pagina = await api.chatbots.mensagens(selecionadoId as number, {
          limit: 200,
        })
        if (ativo) setMensagens(pagina.items)
      } catch (falha) {
        if (ativo) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar as mensagens.'))
        }
      } finally {
        if (ativo) setCarregandoMensagens(false)
      }
    }

    void carregarMensagens()
    return () => {
      ativo = false
    }
  }, [selecionadoId])

  // Mantém a conversa rolada para a última mensagem.
  useEffect(() => {
    if (corpoRef.current) {
      corpoRef.current.scrollTop = corpoRef.current.scrollHeight
    }
  }, [mensagens, pensando])

  /** Envia a mensagem digitada para o bot selecionado. */
  async function enviar(texto: string) {
    const limpo = texto.trim()
    if (!limpo || !selecionado || pensando) return

    const idTemporario = idTemporarioRef.current
    idTemporarioRef.current -= 1
    const mensagemTemporaria: ChatMensagem = {
      id: idTemporario,
      chatbot_id: selecionado.id,
      usuario_id: usuario.id,
      papel: 'USER',
      conteudo: limpo,
      criado_em: new Date().toISOString(),
    }

    setInput('')
    setMensagens((atuais) => [...atuais, mensagemTemporaria])
    setPensando(true)
    setErro(null)

    try {
      const resposta = await api.chatbots.enviar(selecionado.id, limpo)
      setMensagens((atuais) => [
        ...atuais.filter((mensagem) => mensagem.id !== idTemporario),
        resposta.mensagem_usuario,
        resposta.resposta,
      ])
    } catch (falha) {
      setMensagens((atuais) =>
        atuais.filter((mensagem) => mensagem.id !== idTemporario),
      )
      setErro(mensagemDeErro(falha, 'Não foi possível enviar a mensagem.'))
    } finally {
      setPensando(false)
    }
  }

  /** Submete o composer. */
  function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    void enviar(input)
  }

  /** Abre o modal de criação de bot. */
  function abrirNovoBot() {
    setEditando(null)
    setNome('')
    setDescricao('')
    setVersaoBot('v1.0')
    setModelo('gpt-4o')
    setStatus('OFFLINE')
    setErroFormulario(null)
    setModalBot(true)
  }

  /** Abre o modal de edição do bot selecionado. */
  function abrirEdicaoBot(bot: Chatbot) {
    if (!ehAdmin) return

    setEditando(bot)
    setNome(bot.nome)
    setDescricao(bot.descricao ?? '')
    setVersaoBot(bot.versao)
    setModelo(bot.modelo)
    setStatus(bot.status)
    setErroFormulario(null)
    setModalBot(true)
  }

  /** Cria ou atualiza um bot. */
  async function salvarBot(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const nomeLimpo = nome.trim()

    if (!nomeLimpo) {
      setErroFormulario('Informe o nome do bot.')
      return
    }

    const payload = {
      nome: nomeLimpo,
      descricao: descricao.trim() || null,
      versao: versaoBot.trim() || 'v1.0',
      modelo: modelo.trim() || 'gpt-4o',
      status,
    }

    setSalvando(true)
    setErroFormulario(null)

    try {
      if (editando) {
        await api.chatbots.update(editando.id, payload)
      } else {
        const criado = await api.chatbots.create(payload)
        setSelecionadoId(criado.id)
      }

      setModalBot(false)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErroFormulario(mensagemDeErro(falha, 'Não foi possível salvar o bot.'))
    } finally {
      setSalvando(false)
    }
  }

  /** Exclui o bot selecionado. */
  async function excluirBot() {
    if (!selecionado || !ehAdmin) return
    if (!window.confirm(`Excluir o chatbot "${selecionado.nome}"?`)) return

    try {
      await api.chatbots.remove(selecionado.id)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir o bot.'))
    }
  }

  return (
    <div className="page chatbots-page">
      <aside className="panel bots-panel">
        <div className="bots-head">
          <div>
            <h3>Chatbots</h3>
            <span className="muted">{bots.length} bot(s) configurado(s)</span>
          </div>
          <button
            className="icon-btn"
            title="Atualizar"
            onClick={() => setVersao((valor) => valor + 1)}
          >
            <IconRefresh size={16} />
          </button>
        </div>

        <div className="bots-list">
          {carregandoBots && <div className="empty-inline">Carregando bots...</div>}
          {!carregandoBots && bots.length === 0 && (
            <div className="empty-inline">Nenhum bot cadastrado.</div>
          )}
          {!carregandoBots &&
            bots.map((bot) => (
              <button
                className={`bot-row${bot.id === selecionadoId ? ' active' : ''}`}
                key={bot.id}
                onClick={() => setSelecionadoId(bot.id)}
              >
                <span className={`bot-avatar ${bot.status.toLowerCase()}`}>
                  <IconBot size={19} />
                </span>
                <span className="bot-row-body">
                  <strong>{bot.nome}</strong>
                  <span>{bot.descricao || 'Sem descrição'}</span>
                </span>
                <span className={`pill pill-${classeStatus(bot.status)}`}>
                  {rotuloStatus(bot.status)}
                </span>
              </button>
            ))}
        </div>

        {ehAdmin && (
          <button className="btn-primary bots-create" onClick={abrirNovoBot}>
            <IconPlus size={17} /> Criar novo bot
          </button>
        )}
      </aside>

      <section className="panel chat-panel">
        {!selecionado ? (
          <div className="empty-state">
            <IconBot size={34} />
            <strong>Nenhum chatbot selecionado</strong>
            <span>
              {ehAdmin
                ? 'Crie um bot para começar a conversar.'
                : 'Aguarde um administrador configurar um bot.'}
            </span>
          </div>
        ) : (
          <>
            <header className="chat-head">
              <div className="chat-bot">
                <span className={`bot-avatar ${selecionado.status.toLowerCase()}`}>
                  <IconBot size={20} />
                </span>
                <div>
                  <h3>{selecionado.nome}</h3>
                  <span>
                    <i
                      className={`status-dot${selecionado.status === 'OFFLINE' ? '' : ' on'}`}
                    />{' '}
                    {selecionado.versao} · {rotuloStatus(selecionado.status)}
                  </span>
                </div>
              </div>

              <div className="chat-meta">
                <span className="chip">Modelo: {selecionado.modelo}</span>
                <span className="chip model-chip">
                  Criado em {formatarData(selecionado.data_criacao)}
                </span>
                {ehAdmin && (
                  <>
                    <button
                      className="icon-btn"
                      title="Editar bot"
                      onClick={() => abrirEdicaoBot(selecionado)}
                    >
                      <IconDots size={18} />
                    </button>
                    <button
                      className="icon-btn danger"
                      title="Excluir bot"
                      onClick={excluirBot}
                    >
                      <IconTrash size={16} />
                    </button>
                  </>
                )}
              </div>
            </header>

            <div className="chat-body" ref={corpoRef}>
              {carregandoMensagens && (
                <div className="empty-inline">Carregando mensagens...</div>
              )}

              {!carregandoMensagens && mensagens.length === 0 && (
                <div className="empty-state">
                  <IconBot size={30} />
                  <strong>Comece uma conversa</strong>
                  <span>Envie uma mensagem para {selecionado.nome}.</span>
                </div>
              )}

              {!carregandoMensagens &&
                mensagens.map((mensagem) => {
                  const ehUsuario = mensagem.papel === 'USER'
                  return (
                    <div
                      className={`msg ${ehUsuario ? 'user' : 'assistant'}`}
                      key={mensagem.id}
                    >
                      <span className={`msg-avatar ${ehUsuario ? 'user' : 'assistant'}`}>
                        {ehUsuario ? (
                          <b>{usuario.nome_completo.charAt(0).toUpperCase()}</b>
                        ) : (
                          <IconBot size={15} />
                        )}
                      </span>
                      <div className="msg-bubble">
                        <p>{mensagem.conteudo}</p>
                        <span className="msg-meta">
                          {new Date(mensagem.criado_em).toLocaleTimeString('pt-BR', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                    </div>
                  )
                })}

              {pensando && (
                <div className="msg assistant">
                  <span className="msg-avatar assistant">
                    <IconBot size={15} />
                  </span>
                  <div className="msg-bubble typing">
                    <i />
                    <i />
                    <i />
                  </div>
                </div>
              )}
            </div>

            {erro && <div className="form-error">{erro}</div>}

            <footer className="composer">
              <form className="composer-box" onSubmit={enviarFormulario}>
                <textarea
                  rows={1}
                  value={input}
                  placeholder={`Envie uma mensagem para ${selecionado.nome}...`}
                  onChange={(evento) => setInput(evento.target.value)}
                  onKeyDown={(evento) => {
                    if (evento.key === 'Enter' && !evento.shiftKey) {
                      evento.preventDefault()
                      void enviar(evento.currentTarget.value)
                    }
                  }}
                />
                <button
                  type="submit"
                  className="composer-send"
                  aria-label="Enviar"
                  disabled={!input.trim() || pensando}
                >
                  <IconSend size={17} />
                </button>
              </form>
              <div className="composer-hints">
                <span>
                  <b>Shift+Enter</b> para nova linha
                </span>
                <span className="muted">
                  A IA pode cometer erros — verifique informações críticas.
                </span>
              </div>
            </footer>
          </>
        )}
      </section>

      {modalBot && (
        <Modal
          titulo={editando ? 'Editar chatbot' : 'Novo chatbot'}
          onClose={() => setModalBot(false)}
        >
          <form className="form-grid" onSubmit={salvarBot}>
            <label className="field">
              <span>Nome</span>
              <input
                type="text"
                value={nome}
                onChange={(evento) => setNome(evento.target.value)}
                placeholder="Ex.: Assistente Financeiro"
              />
            </label>

            <label className="field">
              <span>Descrição</span>
              <textarea
                rows={2}
                value={descricao}
                onChange={(evento) => setDescricao(evento.target.value)}
                placeholder="Opcional"
              />
            </label>

            <div className="form-row">
              <label className="field">
                <span>Versão</span>
                <input
                  type="text"
                  value={versaoBot}
                  onChange={(evento) => setVersaoBot(evento.target.value)}
                  placeholder="v1.0"
                />
              </label>

              <label className="field">
                <span>Modelo</span>
                <input
                  type="text"
                  value={modelo}
                  onChange={(evento) => setModelo(evento.target.value)}
                  placeholder="gpt-4o"
                />
              </label>
            </div>

            <label className="field">
              <span>Status</span>
              <select
                value={status}
                onChange={(evento) => setStatus(evento.target.value as StatusChatbot)}
              >
                <option value="ACTIVE">Ativo</option>
                <option value="ONLINE">Online</option>
                <option value="IDLE">Ocioso</option>
                <option value="OFFLINE">Offline</option>
              </select>
            </label>

            {erroFormulario && <div className="form-error">{erroFormulario}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalBot(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvando}>
                {salvando ? 'Salvando...' : editando ? 'Salvar alterações' : 'Criar bot'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
