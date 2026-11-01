import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import type { Notebook, NotebookPayload, Usuario } from '../api/types'
import Modal from './Modal'
import {
  IconExternal,
  IconNotebook,
  IconPlus,
  IconSearch,
  IconTag,
  IconTrash,
  IconUsers,
} from './icons'

interface NotebooksProps {
  /** Usuário autenticado, usado no controle de edição/exclusão. */
  usuario: Usuario
}

/** Converte um erro desconhecido em mensagem legível. */
function mensagemDeErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao
}

/** Traduz os grupos padrão para rótulos mais amigáveis. */
function rotuloGrupo(grupo: string): string {
  if (grupo === 'PERSONAL NOTES') return 'Notas pessoais'
  if (grupo === 'ENGINEERING DOCS') return 'Docs de engenharia'
  return grupo
}

/** Formata a data de atualização do notebook. */
function formatarData(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Separa a string de tags em uma lista limpa. */
function separarTags(tags: string | null): string[] {
  if (!tags) return []
  return tags
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

export default function Notebooks({ usuario }: NotebooksProps) {
  const [notebooks, setNotebooks] = useState<Notebook[]>([])
  const [selecionadoId, setSelecionadoId] = useState<number | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [versao, setVersao] = useState(0)

  const [grupoFiltro, setGrupoFiltro] = useState('TODOS')
  const [buscaInput, setBuscaInput] = useState('')
  const [busca, setBusca] = useState('')

  // Formulário de criação/edição
  const [modalNotebook, setModalNotebook] = useState(false)
  const [editando, setEditando] = useState<Notebook | null>(null)
  const [grupo, setGrupo] = useState('PERSONAL NOTES')
  const [titulo, setTitulo] = useState('')
  const [subtitulo, setSubtitulo] = useState('')
  const [tags, setTags] = useState('')
  const [conteudo, setConteudo] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [erroFormulario, setErroFormulario] = useState<string | null>(null)

  const ehAdmin = usuario.perfil === 'ADMIN'

  // Carrega todos os notebooks; a busca e o filtro de grupo são locais.
  useEffect(() => {
    let ativo = true

    async function carregar() {
      setCarregando(true)
      setErro(null)

      try {
        const pagina = await api.notebooks.list({ limit: 500 })
        if (!ativo) return

        setNotebooks(pagina.items)
        setSelecionadoId((atual) => {
          if (atual && pagina.items.some((notebook) => notebook.id === atual)) {
            return atual
          }
          return pagina.items[0]?.id ?? null
        })
      } catch (falha) {
        if (ativo) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar os notebooks.'))
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

  const grupos = Array.from(new Set(notebooks.map((notebook) => notebook.grupo)))

  const visiveis = notebooks.filter((notebook) => {
    const combinaGrupo = grupoFiltro === 'TODOS' || notebook.grupo === grupoFiltro
    const termo = busca.toLowerCase()
    const combinaBusca =
      !termo ||
      notebook.titulo.toLowerCase().includes(termo) ||
      (notebook.subtitulo ?? '').toLowerCase().includes(termo) ||
      (notebook.tags ?? '').toLowerCase().includes(termo) ||
      notebook.conteudo.toLowerCase().includes(termo)

    return combinaGrupo && combinaBusca
  })

  const selecionado =
    notebooks.find((notebook) => notebook.id === selecionadoId) ?? null

  // Se o filtro esconder o notebook selecionado, seleciona o primeiro visível.
  useEffect(() => {
    if (visiveis.length === 0) return
    if (!visiveis.some((notebook) => notebook.id === selecionadoId)) {
      setSelecionadoId(visiveis[0].id)
    }
  }, [grupoFiltro, busca, notebooks, selecionadoId, visiveis])

  /** Verifica se o usuário pode editar/excluir o notebook. */
  function podeGerenciar(notebook: Notebook): boolean {
    return ehAdmin || notebook.autor_id === usuario.id
  }

  /** Aplica a busca digitada. */
  function submeterBusca(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setBusca(buscaInput.trim())
  }

  /** Abre o formulário de criação. */
  function abrirNovo() {
    setEditando(null)
    setGrupo('PERSONAL NOTES')
    setTitulo('')
    setSubtitulo('')
    setTags('')
    setConteudo('')
    setErroFormulario(null)
    setModalNotebook(true)
  }

  /** Abre o formulário preenchido para edição. */
  function abrirEdicao(notebook: Notebook) {
    if (!podeGerenciar(notebook)) return

    setEditando(notebook)
    setGrupo(notebook.grupo)
    setTitulo(notebook.titulo)
    setSubtitulo(notebook.subtitulo ?? '')
    setTags(notebook.tags ?? '')
    setConteudo(notebook.conteudo)
    setErroFormulario(null)
    setModalNotebook(true)
  }

  /** Cria ou atualiza o notebook. */
  async function salvarNotebook(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const tituloLimpo = titulo.trim()
    const conteudoLimpo = conteudo.trim()

    if (!tituloLimpo || !conteudoLimpo) {
      setErroFormulario('Informe o título e o conteúdo do notebook.')
      return
    }

    const payload: NotebookPayload = {
      grupo: grupo.trim() || 'PERSONAL NOTES',
      titulo: tituloLimpo,
      subtitulo: subtitulo.trim() || null,
      conteudo: conteudoLimpo,
      tags: tags.trim() || null,
    }

    setSalvando(true)
    setErroFormulario(null)

    try {
      if (editando) {
        await api.notebooks.update(editando.id, payload)
      } else {
        const criado = await api.notebooks.create(payload)
        setSelecionadoId(criado.id)
      }

      setModalNotebook(false)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErroFormulario(mensagemDeErro(falha, 'Não foi possível salvar o notebook.'))
    } finally {
      setSalvando(false)
    }
  }

  /** Exclui o notebook selecionado. */
  async function excluirNotebook(notebook: Notebook) {
    if (!window.confirm(`Excluir o notebook "${notebook.titulo}"?`)) return

    try {
      await api.notebooks.remove(notebook.id)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir o notebook.'))
    }
  }

  return (
    <div className="page notebooks">
      <div className="notebooks-toolbar">
        <div className="tabs">
          <button
            className={`tab${grupoFiltro === 'TODOS' ? ' active' : ''}`}
            onClick={() => setGrupoFiltro('TODOS')}
          >
            Todos
          </button>
          {grupos.map((nomeGrupo) => (
            <button
              key={nomeGrupo}
              className={`tab${grupoFiltro === nomeGrupo ? ' active' : ''}`}
              onClick={() => setGrupoFiltro(nomeGrupo)}
            >
              {rotuloGrupo(nomeGrupo)}
            </button>
          ))}
        </div>

        <div className="nb-actions">
          <form className="search-bar sm" onSubmit={submeterBusca}>
            <IconSearch size={16} />
            <input
              type="search"
              placeholder="Buscar notebooks"
              value={buscaInput}
              onChange={(evento) => setBuscaInput(evento.target.value)}
              aria-label="Buscar notebooks"
            />
          </form>
          <button className="btn-primary sm" onClick={abrirNovo}>
            <IconPlus size={15} /> Novo notebook
          </button>
        </div>
      </div>

      {erro && <div className="form-error">{erro}</div>}

      <div className="notebooks-grid">
        <aside className="panel nb-list-panel">
          {carregando && <div className="nb-empty muted">Carregando notebooks...</div>}
          {!carregando && visiveis.length === 0 && (
            <div className="nb-empty muted">
              Nenhum notebook encontrado neste filtro.
            </div>
          )}
          {!carregando &&
            visiveis.map((notebook) => (
              <button
                className={`nb-row${notebook.id === selecionadoId ? ' active' : ''}`}
                key={notebook.id}
                onClick={() => setSelecionadoId(notebook.id)}
              >
                <span className="nb-doc-icon">
                  <IconNotebook size={18} />
                </span>
                <span className="nb-row-body">
                  <strong>{notebook.titulo}</strong>
                  <span>{notebook.subtitulo || rotuloGrupo(notebook.grupo)}</span>
                  <em>Atualizado {formatarData(notebook.data_atualizacao)}</em>
                </span>
              </button>
            ))}
        </aside>

        <article className="panel nb-viewer">
          {!selecionado ? (
            <div className="empty-state">
              <IconNotebook size={34} />
              <strong>Nenhum notebook selecionado</strong>
              <span>Crie um notebook para documentar o conhecimento da equipe.</span>
            </div>
          ) : (
            <>
              <header className="nb-viewer-head">
                <div>
                  <span className="nb-breadcrumb">
                    {rotuloGrupo(selecionado.grupo)} /
                  </span>
                  <h3>{selecionado.titulo}</h3>
                  <p>{selecionado.subtitulo || 'Sem subtítulo'}</p>
                </div>
                <div className="nb-viewer-actions">
                  <span className="chip">
                    <IconUsers size={13} />{' '}
                    {selecionado.autor_id === usuario.id
                      ? 'Seu notebook'
                      : `Autor #${selecionado.autor_id}`}
                  </span>
                  {podeGerenciar(selecionado) && (
                    <>
                      <button
                        className="btn-ghost"
                        onClick={() => abrirEdicao(selecionado)}
                      >
                        <IconExternal size={15} /> Editar
                      </button>
                      <button
                        className="icon-btn danger"
                        title="Excluir notebook"
                        onClick={() => excluirNotebook(selecionado)}
                      >
                        <IconTrash size={16} />
                      </button>
                    </>
                  )}
                </div>
              </header>

              <div className="nb-tags">
                {separarTags(selecionado.tags).map((tag) => (
                  <span className="chip" key={tag}>
                    <IconTag size={12} /> {tag}
                  </span>
                ))}
                <span className="muted">
                  Atualizado {formatarData(selecionado.data_atualizacao)}
                </span>
              </div>

              <div className="nb-content">
                {selecionado.conteudo.split(/\n{2,}/).map((paragrafo, indice) => (
                  <p key={indice}>{paragrafo}</p>
                ))}
              </div>
            </>
          )}
        </article>
      </div>

      {modalNotebook && (
        <Modal
          titulo={editando ? 'Editar notebook' : 'Novo notebook'}
          onClose={() => setModalNotebook(false)}
        >
          <form className="form-grid" onSubmit={salvarNotebook}>
            <div className="form-row">
              <label className="field">
                <span>Grupo</span>
                <input
                  type="text"
                  list="grupos-notebook"
                  value={grupo}
                  onChange={(evento) => setGrupo(evento.target.value)}
                  placeholder="PERSONAL NOTES"
                />
                <datalist id="grupos-notebook">
                  {grupos.map((nomeGrupo) => (
                    <option key={nomeGrupo} value={nomeGrupo} />
                  ))}
                </datalist>
              </label>

              <label className="field">
                <span>Tags</span>
                <input
                  type="text"
                  value={tags}
                  onChange={(evento) => setTags(evento.target.value)}
                  placeholder="Backend, FastAPI"
                />
              </label>
            </div>

            <label className="field">
              <span>Título</span>
              <input
                type="text"
                value={titulo}
                onChange={(evento) => setTitulo(evento.target.value)}
                placeholder="Ex.: Guia de deploy"
              />
            </label>

            <label className="field">
              <span>Subtítulo</span>
              <input
                type="text"
                value={subtitulo}
                onChange={(evento) => setSubtitulo(evento.target.value)}
                placeholder="Opcional"
              />
            </label>

            <label className="field">
              <span>Conteúdo</span>
              <textarea
                rows={10}
                value={conteudo}
                onChange={(evento) => setConteudo(evento.target.value)}
                placeholder="Escreva o conteúdo do notebook..."
              />
            </label>

            {erroFormulario && <div className="form-error">{erroFormulario}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalNotebook(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvando}>
                {salvando
                  ? 'Salvando...'
                  : editando
                    ? 'Salvar alterações'
                    : 'Criar notebook'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
