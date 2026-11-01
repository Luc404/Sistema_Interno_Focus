import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import type {
  BacklogItem,
  BacklogPayload,
  PrioridadeBacklog,
  Setor,
  StatusBacklog,
  TipoBacklog,
  Usuario,
} from '../api/types'
import Modal from './Modal'
import { IconAlert, IconPlus, IconTag, IconTrash, IconUsers } from './icons'

interface BacklogsProps {
  /** Usuário autenticado, usado para ações de edição/exclusão. */
  usuario: Usuario
}

const colunas: { id: StatusBacklog; rotulo: string; dot: string }[] = [
  { id: 'PENDENTE', rotulo: 'PENDENTE', dot: 'amber' },
  { id: 'EM_ANDAMENTO', rotulo: 'EM ANDAMENTO', dot: 'blue' },
  { id: 'CONCLUIDO', rotulo: 'CONCLUÍDO', dot: 'green' },
]

const tipos: { id: TipoBacklog | 'TODOS'; rotulo: string }[] = [
  { id: 'TODOS', rotulo: 'Todas' },
  { id: 'FEATURE', rotulo: 'Features' },
  { id: 'BUG', rotulo: 'Bugs' },
  { id: 'MELHORIA', rotulo: 'Melhorias' },
  { id: 'INFRA', rotulo: 'Infra' },
  { id: 'OUTRO', rotulo: 'Outros' },
]

const prioridades: PrioridadeBacklog[] = ['ALTA', 'MEDIA', 'BAIXA']

/** Converte um erro desconhecido em mensagem legível. */
function mensagemDeErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao
}

/** Rótulo amigável do tipo do item. */
function rotuloTipo(tipo: TipoBacklog): string {
  const encontrado = tipos.find((item) => item.id === tipo)
  return encontrado?.rotulo.replace(/s$/, '') ?? tipo
}

/** Rótulo amigável da prioridade. */
function rotuloPrioridade(prioridade: PrioridadeBacklog): string {
  return prioridade === 'MEDIA' ? 'MÉDIA' : prioridade
}

/** Classe de cor da prioridade. */
function classePrioridade(prioridade: PrioridadeBacklog): string {
  if (prioridade === 'ALTA') return 'red'
  if (prioridade === 'MEDIA') return 'amber'
  return 'green'
}

export default function Backlogs({ usuario }: BacklogsProps) {
  const [itens, setItens] = useState<BacklogItem[]>([])
  const [setores, setSetores] = useState<Setor[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [versao, setVersao] = useState(0)

  // Filtros
  const [filtroTipo, setFiltroTipo] = useState<TipoBacklog | 'TODOS'>('TODOS')
  const [filtroPrioridade, setFiltroPrioridade] = useState<PrioridadeBacklog | 'TODAS'>(
    'TODAS',
  )
  const [buscaInput, setBuscaInput] = useState('')
  const [busca, setBusca] = useState('')

  // Arrastar e soltar entre colunas
  const [arrastando, setArrastando] = useState<BacklogItem | null>(null)

  // Formulário de criação/edição
  const [modalItem, setModalItem] = useState(false)
  const [editando, setEditando] = useState<BacklogItem | null>(null)
  const [titulo, setTitulo] = useState('')
  const [descricao, setDescricao] = useState('')
  const [tipo, setTipo] = useState<TipoBacklog>('FEATURE')
  const [prioridade, setPrioridade] = useState<PrioridadeBacklog>('MEDIA')
  const [status, setStatus] = useState<StatusBacklog>('PENDENTE')
  const [setorId, setSetorId] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [erroFormulario, setErroFormulario] = useState<string | null>(null)

  const ehAdmin = usuario.perfil === 'ADMIN'

  // Carrega itens e setores. Os filtros são aplicados localmente para manter
  // as três colunas do kanban sempre sincronizadas.
  useEffect(() => {
    let ativo = true

    async function carregar() {
      setCarregando(true)
      setErro(null)

      try {
        const [paginaItens, paginaSetores] = await Promise.all([
          api.backlog.list({ limit: 500 }),
          api.setores.list({ limit: 200 }),
        ])

        if (ativo) {
          setItens(paginaItens.items)
          setSetores(paginaSetores.items)
        }
      } catch (falha) {
        if (ativo) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar o backlog.'))
        }
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void carregar()
    return () => {
      ativo = false
    }
  }, [versao])

  const itensFiltrados = itens.filter((item) => {
    const combinaTipo = filtroTipo === 'TODOS' || item.tipo === filtroTipo
    const combinaPrioridade =
      filtroPrioridade === 'TODAS' || item.prioridade === filtroPrioridade
    const termo = busca.toLowerCase()
    const combinaBusca =
      !termo ||
      item.titulo.toLowerCase().includes(termo) ||
      (item.descricao ?? '').toLowerCase().includes(termo)

    return combinaTipo && combinaPrioridade && combinaBusca
  })

  /** Aplica a busca digitada. */
  function submeterBusca(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setBusca(buscaInput.trim())
  }

  /** Verifica se o usuário pode editar/excluir um item. */
  function podeGerenciar(item: BacklogItem): boolean {
    return ehAdmin || item.autor_id === usuario.id
  }

  /** Retorna o nome do setor a partir do id. */
  function nomeSetor(id: number | null): string {
    if (!id) return 'Sem setor'
    return setores.find((setor) => setor.id === id)?.nome ?? `Setor #${id}`
  }

  /** Abre o formulário para um novo item. */
  function abrirNovo() {
    setEditando(null)
    setTitulo('')
    setDescricao('')
    setTipo('FEATURE')
    setPrioridade('MEDIA')
    setStatus('PENDENTE')
    setSetorId('')
    setErroFormulario(null)
    setModalItem(true)
  }

  /** Abre o formulário preenchido para edição. */
  function abrirEdicao(item: BacklogItem) {
    if (!podeGerenciar(item)) return

    setEditando(item)
    setTitulo(item.titulo)
    setDescricao(item.descricao ?? '')
    setTipo(item.tipo)
    setPrioridade(item.prioridade)
    setStatus(item.status)
    setSetorId(item.setor_id ? String(item.setor_id) : '')
    setErroFormulario(null)
    setModalItem(true)
  }

  /** Cria ou atualiza o item do backlog. */
  async function salvarItem(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const tituloLimpo = titulo.trim()

    if (!tituloLimpo) {
      setErroFormulario('Informe o título do item.')
      return
    }

    const payload: BacklogPayload = {
      titulo: tituloLimpo,
      descricao: descricao.trim() || null,
      tipo,
      prioridade,
      status,
      setor_id: setorId ? Number(setorId) : null,
    }

    setSalvando(true)
    setErroFormulario(null)

    try {
      if (editando) {
        await api.backlog.update(editando.id, payload)
      } else {
        await api.backlog.create(payload)
      }

      setModalItem(false)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErroFormulario(mensagemDeErro(falha, 'Não foi possível salvar o item.'))
    } finally {
      setSalvando(false)
    }
  }

  /** Move um item para outra coluna. */
  async function mudarStatus(item: BacklogItem, novoStatus: StatusBacklog) {
    if (item.status === novoStatus) return

    try {
      await api.backlog.status(item.id, novoStatus)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível mover o item.'))
    }
  }

  /** Exclui um item após confirmação. */
  async function excluirItem(item: BacklogItem) {
    if (!window.confirm(`Excluir o item "${item.titulo}"?`)) return

    try {
      await api.backlog.remove(item.id)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir o item.'))
    }
  }

  return (
    <div className="page backlogs">
      <div className="backlog-head">
        <div className="backlog-filters">
          {tipos.map((opcao) => (
            <button
              key={opcao.id}
              className={`filter${filtroTipo === opcao.id ? ' active' : ''}`}
              onClick={() => setFiltroTipo(opcao.id)}
            >
              {opcao.rotulo}
            </button>
          ))}
        </div>

        <div className="backlog-actions">
          <form className="search-bar sm" onSubmit={submeterBusca}>
            <IconTag size={15} />
            <input
              type="search"
              placeholder="Buscar no backlog"
              value={buscaInput}
              onChange={(evento) => setBuscaInput(evento.target.value)}
              aria-label="Buscar no backlog"
            />
          </form>

          <select
            className="filter-select"
            value={filtroPrioridade}
            onChange={(evento) =>
              setFiltroPrioridade(evento.target.value as PrioridadeBacklog | 'TODAS')
            }
            aria-label="Filtrar por prioridade"
          >
            <option value="TODAS">Todas as prioridades</option>
            {prioridades.map((opcao) => (
              <option key={opcao} value={opcao}>
                {rotuloPrioridade(opcao)}
              </option>
            ))}
          </select>

          <button className="btn-primary" onClick={abrirNovo}>
            <IconPlus size={16} /> Novo item
          </button>
        </div>
      </div>

      {erro && <div className="form-error">{erro}</div>}

      <div className="kanban">
        {colunas.map((coluna) => {
          const itensDaColuna = itensFiltrados.filter((item) => item.status === coluna.id)

          return (
            <section
              className="kanban-col"
              key={coluna.id}
              onDragOver={(evento) => evento.preventDefault()}
              onDrop={() => {
                if (arrastando) {
                  void mudarStatus(arrastando, coluna.id)
                  setArrastando(null)
                }
              }}
            >
              <div className="kanban-head">
                <span className={`kanban-dot dot-${coluna.dot}`} />
                <strong>{coluna.rotulo}</strong>
                <b>{itensDaColuna.length}</b>
              </div>

              <div className="kanban-cards">
                {carregando && <div className="empty-inline">Carregando...</div>}

                {!carregando &&
                  itensDaColuna.map((item) => (
                    <article
                      className={`kanban-card${arrastando?.id === item.id ? ' dragging' : ''}`}
                      key={item.id}
                      draggable
                      onDragStart={() => setArrastando(item)}
                      onDragEnd={() => setArrastando(null)}
                    >
                      <div className="kanban-card-top">
                        <span className="chip">
                          <IconTag size={12} /> {rotuloTipo(item.tipo)}
                        </span>
                        <span className={`chip prio-${classePrioridade(item.prioridade)}`}>
                          {rotuloPrioridade(item.prioridade)}
                        </span>
                      </div>

                      <h4
                        className="kanban-card-title"
                        onClick={() => abrirEdicao(item)}
                        title={podeGerenciar(item) ? 'Editar item' : item.titulo}
                      >
                        {item.titulo}
                      </h4>
                      <p>{item.descricao || 'Sem descrição.'}</p>

                      <div className="kanban-card-foot">
                        <span>
                          <IconUsers size={13} />{' '}
                          {item.autor_id === usuario.id ? 'Você' : `Usuário #${item.autor_id}`}
                        </span>
                        <span className="muted">{nomeSetor(item.setor_id)}</span>
                      </div>

                      <div className="kanban-card-actions">
                        <select
                          className="kanban-status"
                          value={item.status}
                          onChange={(evento) =>
                            mudarStatus(item, evento.target.value as StatusBacklog)
                          }
                          aria-label="Mover item de status"
                        >
                          {colunas.map((opcao) => (
                            <option key={opcao.id} value={opcao.id}>
                              {opcao.rotulo}
                            </option>
                          ))}
                        </select>

                        {podeGerenciar(item) && (
                          <button
                            className="icon-btn sm danger"
                            title="Excluir item"
                            onClick={() => excluirItem(item)}
                          >
                            <IconTrash size={14} />
                          </button>
                        )}
                      </div>
                    </article>
                  ))}

                {!carregando && itensDaColuna.length === 0 && (
                  <div className="empty-inline">Nenhum item nesta coluna.</div>
                )}
              </div>
            </section>
          )
        })}
      </div>

      <div className="backlog-foot muted">
        <IconAlert size={15} /> Arraste os cartões entre as colunas ou use o seletor de
        status. Prioridades ALTAS devem ser resolvidas primeiro.
      </div>

      {modalItem && (
        <Modal
          titulo={editando ? 'Editar item do backlog' : 'Novo item do backlog'}
          onClose={() => setModalItem(false)}
        >
          <form className="form-grid" onSubmit={salvarItem}>
            <label className="field">
              <span>Título</span>
              <input
                type="text"
                value={titulo}
                onChange={(evento) => setTitulo(evento.target.value)}
                placeholder="Ex.: Corrigir timeout no login"
              />
            </label>

            <label className="field">
              <span>Descrição</span>
              <textarea
                rows={3}
                value={descricao}
                onChange={(evento) => setDescricao(evento.target.value)}
                placeholder="Contexto, critérios de aceite, links..."
              />
            </label>

            <div className="form-row">
              <label className="field">
                <span>Tipo</span>
                <select
                  value={tipo}
                  onChange={(evento) => setTipo(evento.target.value as TipoBacklog)}
                >
                  <option value="FEATURE">Feature</option>
                  <option value="BUG">Bug</option>
                  <option value="MELHORIA">Melhoria</option>
                  <option value="INFRA">Infra</option>
                  <option value="OUTRO">Outro</option>
                </select>
              </label>

              <label className="field">
                <span>Prioridade</span>
                <select
                  value={prioridade}
                  onChange={(evento) =>
                    setPrioridade(evento.target.value as PrioridadeBacklog)
                  }
                >
                  {prioridades.map((opcao) => (
                    <option key={opcao} value={opcao}>
                      {rotuloPrioridade(opcao)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="form-row">
              <label className="field">
                <span>Status</span>
                <select
                  value={status}
                  onChange={(evento) => setStatus(evento.target.value as StatusBacklog)}
                >
                  {colunas.map((opcao) => (
                    <option key={opcao.id} value={opcao.id}>
                      {opcao.rotulo}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Setor</span>
                <select
                  value={setorId}
                  onChange={(evento) => setSetorId(evento.target.value)}
                >
                  <option value="">Sem setor</option>
                  {setores.map((setor) => (
                    <option key={setor.id} value={setor.id}>
                      {setor.nome}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {erroFormulario && <div className="form-error">{erroFormulario}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalItem(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvando}>
                {salvando ? 'Salvando...' : editando ? 'Salvar alterações' : 'Criar item'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
