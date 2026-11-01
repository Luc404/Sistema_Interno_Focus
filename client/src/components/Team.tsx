import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import type { Perfil, Setor, Usuario } from '../api/types'
import Modal from './Modal'
import {
  IconCheck,
  IconEdit,
  IconPlus,
  IconSearch,
  IconTrash,
  IconUsers,
  IconX,
} from './icons'

interface TeamProps {
  /** Usuário autenticado; somente administradores gerenciam a equipe. */
  usuario: Usuario
}

/** Converte um erro desconhecido em mensagem legível. */
function mensagemDeErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao
}

/** Formata a data de cadastro/criação. */
function formatarData(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export default function Team({ usuario }: TeamProps) {
  const [aba, setAba] = useState<'usuarios' | 'setores'>('usuarios')
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [setores, setSetores] = useState<Setor[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [versao, setVersao] = useState(0)

  const [buscaInput, setBuscaInput] = useState('')
  const [busca, setBusca] = useState('')

  // Formulário de usuário
  const [modalUsuario, setModalUsuario] = useState(false)
  const [editandoUsuario, setEditandoUsuario] = useState<Usuario | null>(null)
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [cargo, setCargo] = useState('')
  const [perfil, setPerfil] = useState<Perfil>('MEMBRO')
  const [setorId, setSetorId] = useState('')
  const [ativo, setAtivo] = useState(true)
  const [salvandoUsuario, setSalvandoUsuario] = useState(false)
  const [erroUsuario, setErroUsuario] = useState<string | null>(null)

  // Formulário de setor
  const [modalSetor, setModalSetor] = useState(false)
  const [editandoSetor, setEditandoSetor] = useState<Setor | null>(null)
  const [nomeSetor, setNomeSetor] = useState('')
  const [descricaoSetor, setDescricaoSetor] = useState('')
  const [statusSetor, setStatusSetor] = useState<'ATIVO' | 'INATIVO'>('ATIVO')
  const [salvandoSetor, setSalvandoSetor] = useState(false)
  const [erroSetor, setErroSetor] = useState<string | null>(null)

  const ehAdmin = usuario.perfil === 'ADMIN'

  // Carrega usuários e setores. A listagem de usuários exige perfil ADMIN.
  useEffect(() => {
    let ativoEfeito = true

    async function carregar() {
      if (!ehAdmin) {
        setErro('Apenas administradores podem gerenciar a equipe.')
        setCarregando(false)
        return
      }

      setCarregando(true)
      setErro(null)

      try {
        const [paginaUsuarios, paginaSetores] = await Promise.all([
          api.usuarios.list({ limit: 500 }),
          api.setores.list({ limit: 500 }),
        ])

        if (ativoEfeito) {
          setUsuarios(paginaUsuarios.items)
          setSetores(paginaSetores.items)
        }
      } catch (falha) {
        if (ativoEfeito) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar a equipe.'))
        }
      } finally {
        if (ativoEfeito) setCarregando(false)
      }
    }

    void carregar()
    return () => {
      ativoEfeito = false
    }
  }, [ehAdmin, versao])

  const termo = busca.toLowerCase()

  const usuariosVisiveis = usuarios.filter((item) => {
    if (!termo) return true
    return [item.nome_completo, item.email, item.cargo ?? '']
      .join(' ')
      .toLowerCase()
      .includes(termo)
  })

  const setoresVisiveis = setores.filter((item) => {
    if (!termo) return true
    return [item.nome, item.descricao ?? ''].join(' ').toLowerCase().includes(termo)
  })

  /** Retorna o nome do setor a partir do id. */
  function nomeDoSetor(id: number | null): string {
    if (!id) return 'Sem setor'
    return setores.find((setor) => setor.id === id)?.nome ?? `Setor #${id}`
  }

  /** Aplica a busca digitada. */
  function submeterBusca(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setBusca(buscaInput.trim())
  }

  /** Abre o modal de criação de usuário. */
  function abrirNovoUsuario() {
    setEditandoUsuario(null)
    setNome('')
    setEmail('')
    setSenha('')
    setCargo('')
    setPerfil('MEMBRO')
    setSetorId('')
    setAtivo(true)
    setErroUsuario(null)
    setModalUsuario(true)
  }

  /** Abre o modal de edição de usuário. */
  function abrirEdicaoUsuario(item: Usuario) {
    setEditandoUsuario(item)
    setNome(item.nome_completo)
    setEmail(item.email)
    setSenha('')
    setCargo(item.cargo ?? '')
    setPerfil(item.perfil)
    setSetorId(item.setor_id ? String(item.setor_id) : '')
    setAtivo(item.ativo)
    setErroUsuario(null)
    setModalUsuario(true)
  }

  /** Cria ou atualiza um usuário. */
  async function salvarUsuario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const nomeLimpo = nome.trim()
    const emailLimpo = email.trim()

    if (!nomeLimpo || !emailLimpo) {
      setErroUsuario('Informe nome e e-mail.')
      return
    }

    if (!editandoUsuario) {
      if (senha.length < 8 || !/[a-zA-Z]/.test(senha) || !/\d/.test(senha)) {
        setErroUsuario('A senha deve ter ao menos 8 caracteres, com letras e números.')
        return
      }
    }

    const dadosBase = {
      nome_completo: nomeLimpo,
      email: emailLimpo,
      cargo: cargo.trim() || null,
      perfil,
      setor_id: setorId ? Number(setorId) : null,
    }

    setSalvandoUsuario(true)
    setErroUsuario(null)

    try {
      if (editandoUsuario) {
        await api.usuarios.update(editandoUsuario.id, { ...dadosBase, ativo })
      } else {
        await api.usuarios.create({ ...dadosBase, senha })
      }

      setModalUsuario(false)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErroUsuario(mensagemDeErro(falha, 'Não foi possível salvar o usuário.'))
    } finally {
      setSalvandoUsuario(false)
    }
  }

  /** Ativa ou desativa um usuário. */
  async function alternarUsuario(item: Usuario) {
    try {
      if (item.ativo) {
        await api.usuarios.desativar(item.id)
      } else {
        await api.usuarios.ativar(item.id)
      }
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível alterar o status do usuário.'))
    }
  }

  /** Abre o modal de criação de setor. */
  function abrirNovoSetor() {
    setEditandoSetor(null)
    setNomeSetor('')
    setDescricaoSetor('')
    setStatusSetor('ATIVO')
    setErroSetor(null)
    setModalSetor(true)
  }

  /** Abre o modal de edição de setor. */
  function abrirEdicaoSetor(setor: Setor) {
    setEditandoSetor(setor)
    setNomeSetor(setor.nome)
    setDescricaoSetor(setor.descricao ?? '')
    setStatusSetor(setor.status)
    setErroSetor(null)
    setModalSetor(true)
  }

  /** Cria ou atualiza um setor. */
  async function salvarSetor(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const nomeLimpo = nomeSetor.trim()

    if (!nomeLimpo) {
      setErroSetor('Informe o nome do setor.')
      return
    }

    const payload = {
      nome: nomeLimpo,
      descricao: descricaoSetor.trim() || null,
      status: statusSetor,
    }

    setSalvandoSetor(true)
    setErroSetor(null)

    try {
      if (editandoSetor) {
        await api.setores.update(editandoSetor.id, payload)
      } else {
        await api.setores.create(payload)
      }

      setModalSetor(false)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErroSetor(mensagemDeErro(falha, 'Não foi possível salvar o setor.'))
    } finally {
      setSalvandoSetor(false)
    }
  }

  /** Exclui um setor após confirmação. */
  async function excluirSetor(setor: Setor) {
    if (!window.confirm(`Excluir o setor "${setor.nome}"?`)) return

    try {
      await api.setores.remove(setor.id)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir o setor.'))
    }
  }

  return (
    <div className="page team-page">
      <div className="team-toolbar">
        <div className="tabs">
          <button
            className={`tab${aba === 'usuarios' ? ' active' : ''}`}
            onClick={() => {
              setAba('usuarios')
              setBusca('')
              setBuscaInput('')
            }}
          >
            Usuários
          </button>
          <button
            className={`tab${aba === 'setores' ? ' active' : ''}`}
            onClick={() => {
              setAba('setores')
              setBusca('')
              setBuscaInput('')
            }}
          >
            Setores
          </button>
        </div>

        <div className="nb-actions">
          <form className="search-bar sm" onSubmit={submeterBusca}>
            <IconSearch size={16} />
            <input
              type="search"
              placeholder={aba === 'usuarios' ? 'Buscar usuários' : 'Buscar setores'}
              value={buscaInput}
              onChange={(evento) => setBuscaInput(evento.target.value)}
              aria-label="Buscar na equipe"
            />
          </form>

          {ehAdmin && (
            <button
              className="btn-primary sm"
              onClick={aba === 'usuarios' ? abrirNovoUsuario : abrirNovoSetor}
            >
              <IconPlus size={15} />
              {aba === 'usuarios' ? 'Novo usuário' : 'Novo setor'}
            </button>
          )}
        </div>
      </div>

      {erro && <div className="form-error">{erro}</div>}

      {aba === 'usuarios' ? (
        <section className="panel">
          <div className="panel-head">
            <h3>Usuários</h3>
            <span className="muted">
              <IconUsers size={14} /> {usuariosVisiveis.length} de {usuarios.length}
            </span>
          </div>

          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>Setor</th>
                  <th>Perfil</th>
                  <th>Status</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {carregando && (
                  <tr>
                    <td colSpan={6} className="muted">
                      Carregando usuários...
                    </td>
                  </tr>
                )}

                {!carregando &&
                  usuariosVisiveis.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <strong>{item.nome_completo}</strong>
                        {item.cargo && <span className="cell-sub">{item.cargo}</span>}
                      </td>
                      <td className="muted">{item.email}</td>
                      <td>{nomeDoSetor(item.setor_id)}</td>
                      <td>
                        <span className="chip">
                          {item.perfil === 'ADMIN' ? 'Administrador' : 'Membro'}
                        </span>
                      </td>
                      <td>
                        <span className={`pill pill-${item.ativo ? 'green' : 'red'}`}>
                          {item.ativo ? 'Ativo' : 'Inativo'}
                        </span>
                      </td>
                      <td>
                        <div className="row-actions">
                          <button
                            className="icon-btn sm"
                            title="Editar usuário"
                            onClick={() => abrirEdicaoUsuario(item)}
                          >
                            <IconEdit size={15} />
                          </button>
                          {item.id !== usuario.id && (
                            <button
                              className="icon-btn sm"
                              title={item.ativo ? 'Desativar usuário' : 'Ativar usuário'}
                              onClick={() => alternarUsuario(item)}
                            >
                              {item.ativo ? <IconX size={15} /> : <IconCheck size={15} />}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}

                {!carregando && usuariosVisiveis.length === 0 && (
                  <tr>
                    <td colSpan={6} className="muted">
                      Nenhum usuário encontrado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <section className="panel">
          <div className="panel-head">
            <h3>Setores</h3>
            <span className="muted">
              <IconUsers size={14} /> {setoresVisiveis.length} de {setores.length}
            </span>
          </div>

          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Descrição</th>
                  <th>Status</th>
                  <th>Criado em</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {carregando && (
                  <tr>
                    <td colSpan={5} className="muted">
                      Carregando setores...
                    </td>
                  </tr>
                )}

                {!carregando &&
                  setoresVisiveis.map((setor) => (
                    <tr key={setor.id}>
                      <td>
                        <strong>{setor.nome}</strong>
                      </td>
                      <td className="muted">{setor.descricao || 'Sem descrição'}</td>
                      <td>
                        <span
                          className={`pill pill-${setor.status === 'ATIVO' ? 'green' : 'red'}`}
                        >
                          {setor.status === 'ATIVO' ? 'Ativo' : 'Inativo'}
                        </span>
                      </td>
                      <td className="muted">{formatarData(setor.data_criacao)}</td>
                      <td>
                        <div className="row-actions">
                          <button
                            className="icon-btn sm"
                            title="Editar setor"
                            onClick={() => abrirEdicaoSetor(setor)}
                          >
                            <IconEdit size={15} />
                          </button>
                          <button
                            className="icon-btn sm danger"
                            title="Excluir setor"
                            onClick={() => excluirSetor(setor)}
                          >
                            <IconTrash size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                {!carregando && setoresVisiveis.length === 0 && (
                  <tr>
                    <td colSpan={5} className="muted">
                      Nenhum setor encontrado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {modalUsuario && (
        <Modal
          titulo={editandoUsuario ? 'Editar usuário' : 'Novo usuário'}
          onClose={() => setModalUsuario(false)}
        >
          <form className="form-grid" onSubmit={salvarUsuario}>
            <label className="field">
              <span>Nome completo</span>
              <input
                type="text"
                value={nome}
                onChange={(evento) => setNome(evento.target.value)}
                placeholder="Nome do colaborador"
              />
            </label>

            <label className="field">
              <span>E-mail</span>
              <input
                type="email"
                value={email}
                onChange={(evento) => setEmail(evento.target.value)}
                placeholder="colaborador@focus.com"
              />
            </label>

            {!editandoUsuario && (
              <label className="field">
                <span>Senha inicial</span>
                <input
                  type="password"
                  value={senha}
                  onChange={(evento) => setSenha(evento.target.value)}
                  placeholder="Mínimo 8 caracteres, com letras e números"
                />
              </label>
            )}

            <div className="form-row">
              <label className="field">
                <span>Cargo</span>
                <input
                  type="text"
                  value={cargo}
                  onChange={(evento) => setCargo(evento.target.value)}
                  placeholder="Opcional"
                />
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

            <div className="form-row">
              <label className="field">
                <span>Perfil</span>
                <select
                  value={perfil}
                  onChange={(evento) => setPerfil(evento.target.value as Perfil)}
                >
                  <option value="MEMBRO">Membro</option>
                  <option value="ADMIN">Administrador</option>
                </select>
              </label>

              {editandoUsuario && (
                <label className="field">
                  <span>Status</span>
                  <select
                    value={ativo ? 'ATIVO' : 'INATIVO'}
                    onChange={(evento) => setAtivo(evento.target.value === 'ATIVO')}
                  >
                    <option value="ATIVO">Ativo</option>
                    <option value="INATIVO">Inativo</option>
                  </select>
                </label>
              )}
            </div>

            {erroUsuario && <div className="form-error">{erroUsuario}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalUsuario(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvandoUsuario}>
                {salvandoUsuario
                  ? 'Salvando...'
                  : editandoUsuario
                    ? 'Salvar alterações'
                    : 'Criar usuário'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {modalSetor && (
        <Modal
          titulo={editandoSetor ? 'Editar setor' : 'Novo setor'}
          onClose={() => setModalSetor(false)}
        >
          <form className="form-grid" onSubmit={salvarSetor}>
            <label className="field">
              <span>Nome</span>
              <input
                type="text"
                value={nomeSetor}
                onChange={(evento) => setNomeSetor(evento.target.value)}
                placeholder="Ex.: Desenvolvimento"
              />
            </label>

            <label className="field">
              <span>Descrição</span>
              <textarea
                rows={3}
                value={descricaoSetor}
                onChange={(evento) => setDescricaoSetor(evento.target.value)}
                placeholder="Opcional"
              />
            </label>

            <label className="field">
              <span>Status</span>
              <select
                value={statusSetor}
                onChange={(evento) =>
                  setStatusSetor(evento.target.value as 'ATIVO' | 'INATIVO')
                }
              >
                <option value="ATIVO">Ativo</option>
                <option value="INATIVO">Inativo</option>
              </select>
            </label>

            {erroSetor && <div className="form-error">{erroSetor}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalSetor(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvandoSetor}>
                {salvandoSetor
                  ? 'Salvando...'
                  : editandoSetor
                    ? 'Salvar alterações'
                    : 'Criar setor'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
