import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import type { Arquivo, Categoria, Link, Pasta, Usuario } from '../api/types'
import Modal from './Modal'
import {
  IconCalendar,
  IconChevronRight,
  IconDownload,
  IconFile,
  IconFolder,
  IconLink,
  IconPlus,
  IconTag,
  IconTrash,
  IconUpload,
  IconUsers,
} from './icons'

interface LibrariumProps {
  /** Usuário autenticado, usado para exibir ações permitidas. */
  usuario: Usuario
}

/** Converte um erro desconhecido em uma mensagem legível. */
function mensagemDeErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao
}

/** Extrai uma extensão curta a partir do título ou do MIME type. */
function extensaoDoArquivo(arquivo: Arquivo): string {
  const partes = arquivo.titulo.split('.')
  if (partes.length > 1) {
    const extensao = partes.pop()?.toLowerCase()
    if (extensao && extensao.length <= 5) return extensao
  }

  const mime = arquivo.tipo_mime.toLowerCase()
  if (mime.includes('pdf')) return 'pdf'
  if (mime.includes('png')) return 'png'
  if (mime.includes('jpeg') || mime.includes('jpg')) return 'jpg'
  if (mime.includes('svg')) return 'svg'
  if (mime.includes('zip')) return 'zip'
  if (mime.includes('sql')) return 'sql'
  return 'file'
}

/** Classe de cor do badge conforme o tipo do arquivo. */
function classeDoTipo(tipo: string): string {
  switch (tipo) {
    case 'pdf':
      return 'file-pdf'
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'svg':
      return 'file-image'
    case 'zip':
      return 'file-zip'
    case 'sql':
      return 'file-sql'
    default:
      return 'file-default'
  }
}

/** Formata bytes em uma unidade amigável. */
function formatarTamanho(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  const unidades = ['KB', 'MB', 'GB', 'TB']
  let valor = bytes / 1024
  let indice = 0

  while (valor >= 1024 && indice < unidades.length - 1) {
    valor /= 1024
    indice += 1
  }

  return `${valor.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} ${unidades[indice]}`
}

/** Formata datas ISO em formato curto brasileiro. */
function formatarData(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

/** Normaliza uma URL digitada pelo usuário. */
function normalizarUrl(valor: string): string {
  const url = valor.trim()
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return `https://${url}`
}

export default function Librarium({ usuario }: LibrariumProps) {
  const [aba, setAba] = useState<'arquivos' | 'links'>('arquivos')

  // Dados da biblioteca
  const [arquivos, setArquivos] = useState<Arquivo[]>([])
  const [totalArquivos, setTotalArquivos] = useState(0)
  const [links, setLinks] = useState<Link[]>([])
  const [categorias, setCategorias] = useState<Categoria[]>([])
  const [pastas, setPastas] = useState<Pasta[]>([])

  // Filtros
  const [filtroCategoria, setFiltroCategoria] = useState<number | null>(null)
  const [filtroPasta, setFiltroPasta] = useState<number | null>(null)
  const [filtroCategoriaLink, setFiltroCategoriaLink] = useState<string | null>(null)
  const [buscaInput, setBuscaInput] = useState('')
  const [busca, setBusca] = useState('')

  // Estados de carregamento
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [versao, setVersao] = useState(0)

  // Formulário de upload
  const [modalUpload, setModalUpload] = useState(false)
  const [arquivoUpload, setArquivoUpload] = useState<File | null>(null)
  const [tituloUpload, setTituloUpload] = useState('')
  const [categoriaUpload, setCategoriaUpload] = useState('')
  const [pastaUpload, setPastaUpload] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [erroUpload, setErroUpload] = useState<string | null>(null)

  // Formulário de link
  const [modalLink, setModalLink] = useState(false)
  const [tituloLink, setTituloLink] = useState('')
  const [urlLink, setUrlLink] = useState('')
  const [descricaoLink, setDescricaoLink] = useState('')
  const [categoriaLink, setCategoriaLink] = useState('')
  const [salvandoLink, setSalvandoLink] = useState(false)
  const [erroLink, setErroLink] = useState<string | null>(null)

  // Formulário de categoria
  const [modalCategoria, setModalCategoria] = useState(false)
  const [nomeCategoria, setNomeCategoria] = useState('')
  const [descricaoCategoria, setDescricaoCategoria] = useState('')
  const [salvandoCategoria, setSalvandoCategoria] = useState(false)
  const [erroCategoria, setErroCategoria] = useState<string | null>(null)

  // Formulário de pasta
  const [modalPasta, setModalPasta] = useState(false)
  const [nomePasta, setNomePasta] = useState('')
  const [descricaoPasta, setDescricaoPasta] = useState('')
  const [salvandoPasta, setSalvandoPasta] = useState(false)
  const [erroPasta, setErroPasta] = useState<string | null>(null)

  const ehAdmin = usuario.perfil === 'ADMIN'
  const mostrarContagens = !busca && filtroCategoria === null && filtroPasta === null

  // Carrega categorias e pastas uma única vez.
  useEffect(() => {
    let ativo = true

    async function carregarMetadados() {
      try {
        const [paginaCategorias, paginaPastas] = await Promise.all([
          api.categorias.list({ limit: 200 }),
          api.pastas.list({ limit: 200 }),
        ])
        if (ativo) {
          setCategorias(paginaCategorias.items)
          setPastas(paginaPastas.items)
        }
      } catch (falha) {
        if (ativo) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar as categorias.'))
        }
      }
    }

    void carregarMetadados()
    return () => {
      ativo = false
    }
  }, [])

  // Recarrega a listagem sempre que a aba, a busca ou os filtros mudam.
  useEffect(() => {
    let ativo = true

    async function carregarListas() {
      setCarregando(true)
      setErro(null)

      try {
        if (aba === 'arquivos') {
          const pagina = await api.arquivos.list({
            busca: busca || undefined,
            categoria_id: filtroCategoria ?? undefined,
            pasta_id: filtroPasta ?? undefined,
            limit: 200,
          })
          if (ativo) {
            setArquivos(pagina.items)
            setTotalArquivos(pagina.total)
          }
        } else {
          const pagina = await api.links.list({
            busca: busca || undefined,
            limit: 200,
          })
          if (ativo) setLinks(pagina.items)
        }
      } catch (falha) {
        if (ativo) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar a biblioteca.'))
        }
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void carregarListas()
    return () => {
      ativo = false
    }
  }, [aba, busca, filtroCategoria, filtroPasta, versao])

  // Categorias de links são textos livres; derivamos a lista dos próprios links.
  const categoriasLink = Array.from(
    links.reduce((mapa, link) => {
      const nome = link.categoria?.trim()
      if (nome) mapa.set(nome, (mapa.get(nome) ?? 0) + 1)
      return mapa
    }, new Map<string, number>()),
  ).map(([nome, total]) => ({ nome, total }))

  const linksVisiveis = filtroCategoriaLink
    ? links.filter((link) => link.categoria === filtroCategoriaLink)
    : links

  const tamanhoTotal = arquivos.reduce((total, arquivo) => total + arquivo.tamanho_bytes, 0)

  /** Alterna a aba e limpa filtros para evitar combinações inválidas. */
  function mudarAba(novaAba: 'arquivos' | 'links') {
    setAba(novaAba)
    setFiltroCategoria(null)
    setFiltroPasta(null)
    setFiltroCategoriaLink(null)
    setBuscaInput('')
    setBusca('')
  }

  /** Aplica a busca digitada na barra local. */
  function submeterBusca(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setBusca(buscaInput.trim())
  }

  /** Atualiza a listagem após uma mutação. */
  function recarregar() {
    setVersao((valor) => valor + 1)
  }

  /** Verifica se o usuário pode excluir um registro. */
  function podeExcluir(donoId: number): boolean {
    return ehAdmin || donoId === usuario.id
  }

  /** Abre o modal de upload com os campos limpos. */
  function abrirUpload() {
    setArquivoUpload(null)
    setTituloUpload('')
    setCategoriaUpload('')
    setPastaUpload('')
    setErroUpload(null)
    setModalUpload(true)
  }

  /** Envia o arquivo selecionado para o backend. */
  async function enviarArquivo(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!arquivoUpload) {
      setErroUpload('Selecione um arquivo para enviar.')
      return
    }

    const titulo = tituloUpload.trim() || arquivoUpload.name
    setEnviando(true)
    setErroUpload(null)

    try {
      await api.arquivos.upload(
        arquivoUpload,
        titulo,
        categoriaUpload ? Number(categoriaUpload) : undefined,
        pastaUpload ? Number(pastaUpload) : undefined,
      )
      setModalUpload(false)
      recarregar()
    } catch (falha) {
      setErroUpload(mensagemDeErro(falha, 'Não foi possível enviar o arquivo.'))
    } finally {
      setEnviando(false)
    }
  }

  /** Baixa o arquivo via blob e dispara o download no navegador. */
  async function baixarArquivo(arquivo: Arquivo) {
    try {
      const blob = await api.arquivos.download(arquivo.id)
      const url = URL.createObjectURL(blob)
      const ancora = document.createElement('a')
      ancora.href = url
      ancora.download = arquivo.titulo
      document.body.appendChild(ancora)
      ancora.click()
      ancora.remove()
      URL.revokeObjectURL(url)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível baixar o arquivo.'))
    }
  }

  /** Exclui um arquivo após confirmação. */
  async function excluirArquivo(arquivo: Arquivo) {
    if (!window.confirm(`Excluir o arquivo "${arquivo.titulo}"?`)) return
    try {
      await api.arquivos.remove(arquivo.id)
      recarregar()
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir o arquivo.'))
    }
  }

  /** Abre o modal de criação de link com os campos limpos. */
  function abrirLink() {
    setTituloLink('')
    setUrlLink('')
    setDescricaoLink('')
    setCategoriaLink('')
    setErroLink(null)
    setModalLink(true)
  }

  /** Cria um link útil. */
  async function criarLink(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const titulo = tituloLink.trim()
    const url = normalizarUrl(urlLink)

    if (!titulo || !url) {
      setErroLink('Informe o título e a URL do link.')
      return
    }

    setSalvandoLink(true)
    setErroLink(null)

    try {
      await api.links.create({
        titulo,
        url,
        descricao: descricaoLink.trim() || null,
        categoria: categoriaLink.trim() || null,
      })
      setModalLink(false)
      recarregar()
    } catch (falha) {
      setErroLink(mensagemDeErro(falha, 'Não foi possível criar o link.'))
    } finally {
      setSalvandoLink(false)
    }
  }

  /** Exclui um link após confirmação. */
  async function excluirLink(link: Link) {
    if (!window.confirm(`Excluir o link "${link.titulo}"?`)) return
    try {
      await api.links.remove(link.id)
      recarregar()
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir o link.'))
    }
  }

  /** Cria uma nova categoria (somente administradores). */
  async function criarCategoria(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const nome = nomeCategoria.trim()
    if (!nome) {
      setErroCategoria('Informe o nome da categoria.')
      return
    }

    setSalvandoCategoria(true)
    setErroCategoria(null)

    try {
      const categoria = await api.categorias.create({
        nome,
        descricao: descricaoCategoria.trim() || null,
      })
      setCategorias((itens) => [...itens, categoria])
      setModalCategoria(false)
      setNomeCategoria('')
      setDescricaoCategoria('')
    } catch (falha) {
      setErroCategoria(mensagemDeErro(falha, 'Não foi possível criar a categoria.'))
    } finally {
      setSalvandoCategoria(false)
    }
  }

  /** Cria uma nova pasta (somente administradores). */
  async function criarPasta(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const nome = nomePasta.trim()
    if (!nome) {
      setErroPasta('Informe o nome da pasta.')
      return
    }

    setSalvandoPasta(true)
    setErroPasta(null)

    try {
      const pasta = await api.pastas.create({
        nome,
        descricao: descricaoPasta.trim() || null,
      })
      setPastas((itens) => [...itens, pasta])
      setModalPasta(false)
      setNomePasta('')
      setDescricaoPasta('')
    } catch (falha) {
      setErroPasta(mensagemDeErro(falha, 'Não foi possível criar a pasta.'))
    } finally {
      setSalvandoPasta(false)
    }
  }

  return (
    <div className="page librarium">
      <div className="librarium-top">
        <div className="tabs">
          <button
            className={`tab${aba === 'arquivos' ? ' active' : ''}`}
            onClick={() => mudarAba('arquivos')}
          >
            Arquivos
          </button>
          <button
            className={`tab${aba === 'links' ? ' active' : ''}`}
            onClick={() => mudarAba('links')}
          >
            Links úteis
          </button>
        </div>

        <div className="librarium-top-actions">
          <form className="search-bar sm" onSubmit={submeterBusca}>
            <IconFile size={15} />
            <input
              type="search"
              placeholder={aba === 'arquivos' ? 'Buscar arquivos' : 'Buscar links'}
              value={buscaInput}
              onChange={(evento) => setBuscaInput(evento.target.value)}
              aria-label="Buscar na biblioteca"
            />
          </form>

          {aba === 'arquivos' ? (
            <button className="btn-primary" onClick={abrirUpload}>
              <IconUpload size={16} /> Enviar arquivo
            </button>
          ) : (
            <button className="btn-primary" onClick={abrirLink}>
              <IconPlus size={16} /> Novo link
            </button>
          )}
        </div>
      </div>

      <div className="librarium-grid">
        <aside className="panel librarium-cats">
          {aba === 'arquivos' ? (
            <>
              <div className="librarium-cat-block">
                <h4>
                  CATEGORIAS
                  {ehAdmin && (
                    <button
                      className="cat-add"
                      onClick={() => {
                        setNomeCategoria('')
                        setDescricaoCategoria('')
                        setErroCategoria(null)
                        setModalCategoria(true)
                      }}
                      title="Nova categoria"
                    >
                      <IconPlus size={14} />
                    </button>
                  )}
                </h4>
                <ul>
                  <li
                    className={`cat-row${filtroCategoria === null ? ' active' : ''}`}
                    onClick={() => setFiltroCategoria(null)}
                  >
                    <span>
                      <IconFile size={17} /> Todos os arquivos
                    </span>
                    {mostrarContagens && <b>{totalArquivos}</b>}
                  </li>
                  {categorias.map((categoria) => {
                    const total = arquivos.filter(
                      (arquivo) => arquivo.categoria_id === categoria.id,
                    ).length
                    return (
                      <li
                        key={categoria.id}
                        className={`cat-row${filtroCategoria === categoria.id ? ' active' : ''}`}
                        onClick={() =>
                          setFiltroCategoria((atual) =>
                            atual === categoria.id ? null : categoria.id,
                          )
                        }
                      >
                        <span>
                          <IconTag size={17} /> {categoria.nome}
                        </span>
                        {mostrarContagens && total > 0 && <b>{total}</b>}
                      </li>
                    )
                  })}
                </ul>
              </div>

              <div className="librarium-cat-block">
                <h4>
                  PASTAS
                  {ehAdmin && (
                    <button
                      className="cat-add"
                      onClick={() => {
                        setNomePasta('')
                        setDescricaoPasta('')
                        setErroPasta(null)
                        setModalPasta(true)
                      }}
                      title="Nova pasta"
                    >
                      <IconPlus size={14} />
                    </button>
                  )}
                </h4>
                <ul>
                  <li
                    className={`cat-row${filtroPasta === null ? ' active' : ''}`}
                    onClick={() => setFiltroPasta(null)}
                  >
                    <span>
                      <IconFolder size={17} /> Todas as pastas
                    </span>
                  </li>
                  {pastas.map((pasta) => {
                    const total = arquivos.filter(
                      (arquivo) => arquivo.pasta_id === pasta.id,
                    ).length
                    return (
                      <li
                        key={pasta.id}
                        className={`cat-row${filtroPasta === pasta.id ? ' active' : ''}`}
                        onClick={() =>
                          setFiltroPasta((atual) =>
                            atual === pasta.id ? null : pasta.id,
                          )
                        }
                      >
                        <span>
                          <IconFolder size={17} /> {pasta.nome}
                        </span>
                        {mostrarContagens && total > 0 && <b>{total}</b>}
                      </li>
                    )
                  })}
                </ul>
              </div>

              <div className="storage-card">
                <div className="storage-head">
                  <span>Biblioteca</span>
                  <strong>{formatarTamanho(tamanhoTotal)}</strong>
                </div>
                <div className="storage-bar">
                  <i style={{ width: `${Math.min(100, (tamanhoTotal / (1024 ** 3)) * 100)}%` }} />
                </div>
                <div className="storage-caption">
                  <span>{totalArquivos} arquivo(s)</span>
                  <span>{categorias.length} categoria(s)</span>
                </div>
              </div>
            </>
          ) : (
            <div className="librarium-cat-block">
              <h4>CATEGORIAS DE LINKS</h4>
              <ul>
                <li
                  className={`cat-row${filtroCategoriaLink === null ? ' active' : ''}`}
                  onClick={() => setFiltroCategoriaLink(null)}
                >
                  <span>
                    <IconLink size={17} /> Todos os links
                  </span>
                  <b>{links.length}</b>
                </li>
                {categoriasLink.map((categoria) => (
                  <li
                    key={categoria.nome}
                    className={`cat-row${
                      filtroCategoriaLink === categoria.nome ? ' active' : ''
                    }`}
                    onClick={() =>
                      setFiltroCategoriaLink((atual) =>
                        atual === categoria.nome ? null : categoria.nome,
                      )
                    }
                  >
                    <span>
                      <IconTag size={17} /> {categoria.nome}
                    </span>
                    <b>{categoria.total}</b>
                  </li>
                ))}
              </ul>

              <div className="storage-card">
                <div className="storage-head">
                  <span>Links salvos</span>
                  <strong>{links.length}</strong>
                </div>
                <div className="storage-caption">
                  <span>{categoriasLink.length} categoria(s)</span>
                  <span>Fonte: equipe Focus</span>
                </div>
              </div>
            </div>
          )}
        </aside>

        <section className="panel file-panel">
          {aba === 'arquivos' ? (
            <>
              <div className="file-toolbar">
                <div className="file-table-title">
                  <h3>ARQUIVOS</h3>
                  <span>
                    {carregando ? 'Carregando...' : `${totalArquivos} item(ns)`}
                  </span>
                </div>
                <div className="file-actions">
                  <button className="btn-ghost" onClick={recarregar}>
                    <IconChevronRight size={16} /> Atualizar
                  </button>
                </div>
              </div>

              {erro && <div className="form-error">{erro}</div>}

              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Nome</th>
                      <th>Enviado por</th>
                      <th>Data</th>
                      <th>Tamanho</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {!carregando &&
                      arquivos.map((arquivo) => {
                        const tipo = extensaoDoArquivo(arquivo)
                        return (
                          <tr key={arquivo.id}>
                            <td>
                              <div className="file-cell">
                                <span className={`file-badge ${classeDoTipo(tipo)}`}>
                                  {tipo.toUpperCase()}
                                </span>
                                <span className="file-name">{arquivo.titulo}</span>
                              </div>
                            </td>
                            <td>
                              <span className="uploader-cell">
                                <IconUsers size={14} />{' '}
                                {arquivo.usuario_id === usuario.id
                                  ? 'Você'
                                  : `Usuário #${arquivo.usuario_id}`}
                              </span>
                            </td>
                            <td>
                              <span className="date-cell">
                                <IconCalendar size={14} /> {formatarData(arquivo.data_upload)}
                              </span>
                            </td>
                            <td className="muted">{formatarTamanho(arquivo.tamanho_bytes)}</td>
                            <td>
                              <div className="row-actions">
                                <button
                                  className="icon-btn sm"
                                  title="Baixar"
                                  onClick={() => baixarArquivo(arquivo)}
                                >
                                  <IconDownload size={15} />
                                </button>
                                {podeExcluir(arquivo.usuario_id) && (
                                  <button
                                    className="icon-btn sm danger"
                                    title="Excluir"
                                    onClick={() => excluirArquivo(arquivo)}
                                  >
                                    <IconTrash size={15} />
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                  </tbody>
                </table>

                {!carregando && arquivos.length === 0 && (
                  <div className="empty-inline">
                    Nenhum arquivo encontrado. Envie o primeiro arquivo da biblioteca.
                  </div>
                )}
              </div>

              <div className="file-foot">
                <span>
                  <IconChevronRight size={14} /> Mostrando {arquivos.length} de{' '}
                  {totalArquivos} arquivo(s)
                </span>
                <span className="muted">Fonte: Biblioteca Focus Solutions</span>
              </div>
            </>
          ) : (
            <>
              <div className="file-toolbar">
                <div className="file-table-title">
                  <h3>LINKS ÚTEIS</h3>
                  <span>{carregando ? 'Carregando...' : `${linksVisiveis.length} item(ns)`}</span>
                </div>
                <div className="file-actions">
                  <button className="btn-ghost" onClick={recarregar}>
                    <IconChevronRight size={16} /> Atualizar
                  </button>
                </div>
              </div>

              {erro && <div className="form-error">{erro}</div>}

              <div className="link-list">
                {!carregando &&
                  linksVisiveis.map((link) => (
                    <article className="link-card" key={link.id}>
                      <span className="link-card-icon">
                        <IconLink size={18} />
                      </span>
                      <div className="link-card-body">
                        <a href={link.url} target="_blank" rel="noreferrer">
                          {link.titulo}
                        </a>
                        <span>{link.descricao || link.url}</span>
                        <em>
                          {link.categoria || 'Sem categoria'} · {formatarData(link.data_criacao)}
                        </em>
                      </div>
                      {podeExcluir(link.usuario_id) && (
                        <button
                          className="icon-btn sm danger"
                          title="Excluir link"
                          onClick={() => excluirLink(link)}
                        >
                          <IconTrash size={15} />
                        </button>
                      )}
                    </article>
                  ))}

                {!carregando && linksVisiveis.length === 0 && (
                  <div className="empty-inline">
                    Nenhum link encontrado. Cadastre um link útil para a equipe.
                  </div>
                )}
              </div>

              <div className="file-foot">
                <span>
                  <IconChevronRight size={14} /> {linksVisiveis.length} link(s) exibido(s)
                </span>
                <span className="muted">Fonte: Biblioteca Focus Solutions</span>
              </div>
            </>
          )}
        </section>
      </div>

      {modalUpload && (
        <Modal titulo="Enviar arquivo" onClose={() => setModalUpload(false)}>
          <form className="form-grid" onSubmit={enviarArquivo}>
            <label className="field">
              <span>Título</span>
              <input
                type="text"
                value={tituloUpload}
                onChange={(evento) => setTituloUpload(evento.target.value)}
                placeholder="Nome exibido na biblioteca"
              />
            </label>

            <label className="field">
              <span>Arquivo</span>
              <input
                type="file"
                onChange={(evento) => setArquivoUpload(evento.target.files?.[0] ?? null)}
              />
            </label>

            <div className="form-row">
              <label className="field">
                <span>Categoria</span>
                <select
                  value={categoriaUpload}
                  onChange={(evento) => setCategoriaUpload(evento.target.value)}
                >
                  <option value="">Sem categoria</option>
                  {categorias.map((categoria) => (
                    <option key={categoria.id} value={categoria.id}>
                      {categoria.nome}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>Pasta</span>
                <select
                  value={pastaUpload}
                  onChange={(evento) => setPastaUpload(evento.target.value)}
                >
                  <option value="">Sem pasta</option>
                  {pastas.map((pasta) => (
                    <option key={pasta.id} value={pasta.id}>
                      {pasta.nome}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {erroUpload && <div className="form-error">{erroUpload}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalUpload(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={enviando}>
                {enviando ? 'Enviando...' : 'Enviar'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {modalLink && (
        <Modal titulo="Novo link útil" onClose={() => setModalLink(false)}>
          <form className="form-grid" onSubmit={criarLink}>
            <label className="field">
              <span>Título</span>
              <input
                type="text"
                value={tituloLink}
                onChange={(evento) => setTituloLink(evento.target.value)}
                placeholder="Ex.: Documentação da API"
              />
            </label>

            <label className="field">
              <span>URL</span>
              <input
                type="text"
                value={urlLink}
                onChange={(evento) => setUrlLink(evento.target.value)}
                placeholder="https://..."
              />
            </label>

            <label className="field">
              <span>Descrição</span>
              <textarea
                rows={3}
                value={descricaoLink}
                onChange={(evento) => setDescricaoLink(evento.target.value)}
                placeholder="Opcional"
              />
            </label>

            <label className="field">
              <span>Categoria</span>
              <input
                type="text"
                value={categoriaLink}
                onChange={(evento) => setCategoriaLink(evento.target.value)}
                placeholder="Ex.: Desenvolvimento"
              />
            </label>

            {erroLink && <div className="form-error">{erroLink}</div>}

            <div className="form-actions">
              <button type="button" className="btn-ghost" onClick={() => setModalLink(false)}>
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvandoLink}>
                {salvandoLink ? 'Salvando...' : 'Salvar link'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {modalCategoria && (
        <Modal titulo="Nova categoria" onClose={() => setModalCategoria(false)}>
          <form className="form-grid" onSubmit={criarCategoria}>
            <label className="field">
              <span>Nome</span>
              <input
                type="text"
                value={nomeCategoria}
                onChange={(evento) => setNomeCategoria(evento.target.value)}
                placeholder="Ex.: Contratos"
              />
            </label>

            <label className="field">
              <span>Descrição</span>
              <textarea
                rows={3}
                value={descricaoCategoria}
                onChange={(evento) => setDescricaoCategoria(evento.target.value)}
                placeholder="Opcional"
              />
            </label>

            {erroCategoria && <div className="form-error">{erroCategoria}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalCategoria(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvandoCategoria}>
                {salvandoCategoria ? 'Salvando...' : 'Criar categoria'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {modalPasta && (
        <Modal titulo="Nova pasta" onClose={() => setModalPasta(false)}>
          <form className="form-grid" onSubmit={criarPasta}>
            <label className="field">
              <span>Nome</span>
              <input
                type="text"
                value={nomePasta}
                onChange={(evento) => setNomePasta(evento.target.value)}
                placeholder="Ex.: Projetos 2026"
              />
            </label>

            <label className="field">
              <span>Descrição</span>
              <textarea
                rows={3}
                value={descricaoPasta}
                onChange={(evento) => setDescricaoPasta(evento.target.value)}
                placeholder="Opcional"
              />
            </label>

            {erroPasta && <div className="form-error">{erroPasta}</div>}

            <div className="form-actions">
              <button type="button" className="btn-ghost" onClick={() => setModalPasta(false)}>
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvandoPasta}>
                {salvandoPasta ? 'Salvando...' : 'Criar pasta'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
