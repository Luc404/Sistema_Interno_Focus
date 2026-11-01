import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import type {
  Mensalidade,
  Reuniao,
  StatusTarefa,
  TarefaPessoal,
  Usuario,
} from '../api/types'
import Modal from './Modal'
import {
  IconCalendar,
  IconCheck,
  IconChevronRight,
  IconClock,
  IconExternal,
  IconMessage,
  IconPlus,
  IconTrash,
  IconUsers,
} from './icons'

interface CalendarViewProps {
  /** Usuário autenticado, usado para permissões de criação/exclusão. */
  usuario: Usuario
}

const diasDaSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

/** Converte um erro desconhecido em mensagem legível. */
function mensagemDeErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao
}

/** Gera a chave local YYYY-MM-DD usada para agrupar eventos por dia. */
function chaveDoDia(data: Date): string {
  const ano = data.getFullYear()
  const mes = String(data.getMonth() + 1).padStart(2, '0')
  const dia = String(data.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}

/** Retorna o primeiro dia do mês de referência. */
function inicioDoMes(referencia: Date): Date {
  return new Date(referencia.getFullYear(), referencia.getMonth(), 1)
}

/** Retorna o último dia do mês de referência. */
function fimDoMes(referencia: Date): Date {
  return new Date(referencia.getFullYear(), referencia.getMonth() + 1, 0, 23, 59, 59)
}

/** Monta as células do calendário, incluindo espaços vazios antes do dia 1. */
function montarCelulas(referencia: Date): (Date | null)[] {
  const primeiro = inicioDoMes(referencia)
  const totalDias = new Date(
    referencia.getFullYear(),
    referencia.getMonth() + 1,
    0,
  ).getDate()
  const deslocamento = primeiro.getDay()
  const celulas: (Date | null)[] = []

  for (let i = 0; i < deslocamento; i += 1) celulas.push(null)
  for (let dia = 1; dia <= totalDias; dia += 1) {
    celulas.push(new Date(referencia.getFullYear(), referencia.getMonth(), dia))
  }
  return celulas
}

/** Formata um dia por extenso curto, ex.: "31 de outubro". */
function formatarDia(data: Date): string {
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long' })
}

/** Formata hora de um ISO, ex.: "09:30". */
function formatarHora(iso: string): string {
  return new Date(iso).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Formata valor monetário. */
function formatarValor(valor: number): string {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

/** Converte uma data para o formato aceito por input datetime-local. */
function paraInputDataHora(data: Date): string {
  const ano = data.getFullYear()
  const mes = String(data.getMonth() + 1).padStart(2, '0')
  const dia = String(data.getDate()).padStart(2, '0')
  const hora = String(data.getHours()).padStart(2, '0')
  const minuto = String(data.getMinutes()).padStart(2, '0')
  return `${ano}-${mes}-${dia}T${hora}:${minuto}`
}

/** Converte uma data para o formato aceito por input date. */
function paraInputData(data: Date): string {
  return chaveDoDia(data)
}

/** Rótulo amigável do status da tarefa. */
function rotuloTarefa(status: StatusTarefa): string {
  switch (status) {
    case 'EM_ANDAMENTO':
      return 'EM ANDAMENTO'
    case 'CONCLUIDA':
      return 'CONCLUÍDA'
    default:
      return 'PENDENTE'
  }
}

export default function CalendarView({ usuario }: CalendarViewProps) {
  const hoje = new Date()
  const [mesReferencia, setMesReferencia] = useState(() => inicioDoMes(hoje))
  const [diaSelecionado, setDiaSelecionado] = useState(() => chaveDoDia(hoje))

  const [reunioes, setReunioes] = useState<Reuniao[]>([])
  const [tarefas, setTarefas] = useState<TarefaPessoal[]>([])
  const [mensalidades, setMensalidades] = useState<Mensalidade[]>([])

  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [versao, setVersao] = useState(0)

  // Formulário de novo evento
  const [modalNovo, setModalNovo] = useState(false)
  const [tipoNovo, setTipoNovo] = useState<'reuniao' | 'tarefa' | 'mensalidade'>(
    'reuniao',
  )
  const [novoTitulo, setNovoTitulo] = useState('')
  const [novaDescricao, setNovaDescricao] = useState('')
  const [novoInicio, setNovoInicio] = useState('')
  const [novoFim, setNovoFim] = useState('')
  const [novoLink, setNovoLink] = useState('')
  const [novaDataLimite, setNovaDataLimite] = useState('')
  const [novoCliente, setNovoCliente] = useState('')
  const [novoValor, setNovoValor] = useState('')
  const [novaObservacao, setNovaObservacao] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [erroFormulario, setErroFormulario] = useState<string | null>(null)

  const ehAdmin = usuario.perfil === 'ADMIN'
  const celulas = montarCelulas(mesReferencia)
  const nomeMes = mesReferencia.toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric',
  })

  // Carrega os dados do mês exibido.
  useEffect(() => {
    let ativo = true
    const inicio = inicioDoMes(mesReferencia)
    const fim = fimDoMes(mesReferencia)

    async function carregar() {
      setCarregando(true)
      setErro(null)

      try {
        const [paginaReunioes, paginaTarefas, paginaMensalidades] = await Promise.all([
          api.reunioes.list({
            data_inicio: inicio.toISOString(),
            data_fim: fim.toISOString(),
            limit: 200,
          }),
          api.tarefas.minhas({ limit: 200 }),
          api.mensalidades.list({
            vencimento_inicio: inicio.toISOString(),
            vencimento_fim: fim.toISOString(),
            limit: 200,
          }),
        ])

        if (ativo) {
          setReunioes(paginaReunioes.items)
          setTarefas(paginaTarefas.items)
          setMensalidades(paginaMensalidades.items)
        }
      } catch (falha) {
        if (ativo) {
          setErro(mensagemDeErro(falha, 'Não foi possível carregar a agenda.'))
        }
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void carregar()
    return () => {
      ativo = false
    }
  }, [mesReferencia, versao])

  const tarefasDoMes = tarefas.filter((tarefa) => {
    if (!tarefa.data_limite) return false
    const data = new Date(tarefa.data_limite)
    return (
      data.getFullYear() === mesReferencia.getFullYear() &&
      data.getMonth() === mesReferencia.getMonth()
    )
  })

  // Agrupa todos os eventos por dia para desenhar os indicadores no calendário.
  const eventosPorDia = new Map<
    string,
    { reunioes: number; tarefas: number; mensalidades: number }
  >()

  function adicionarEvento(chave: string, tipo: 'reunioes' | 'tarefas' | 'mensalidades') {
    const atual = eventosPorDia.get(chave) ?? {
      reunioes: 0,
      tarefas: 0,
      mensalidades: 0,
    }
    atual[tipo] += 1
    eventosPorDia.set(chave, atual)
  }

  reunioes.forEach((reuniao) =>
    adicionarEvento(chaveDoDia(new Date(reuniao.data_hora_inicio)), 'reunioes'),
  )
  tarefasDoMes.forEach((tarefa) => {
    if (tarefa.data_limite) {
      adicionarEvento(chaveDoDia(new Date(tarefa.data_limite)), 'tarefas')
    }
  })
  mensalidades.forEach((mensalidade) =>
    adicionarEvento(chaveDoDia(new Date(mensalidade.data_vencimento)), 'mensalidades'),
  )

  const reunioesDoDia = reunioes
    .filter((reuniao) => chaveDoDia(new Date(reuniao.data_hora_inicio)) === diaSelecionado)
    .sort(
      (a, b) =>
        new Date(a.data_hora_inicio).getTime() - new Date(b.data_hora_inicio).getTime(),
    )

  const tarefasDoDia = tarefasDoMes.filter(
    (tarefa) => tarefa.data_limite && chaveDoDia(new Date(tarefa.data_limite)) === diaSelecionado,
  )

  const mensalidadesDoDia = mensalidades.filter(
    (mensalidade) =>
      chaveDoDia(new Date(mensalidade.data_vencimento)) === diaSelecionado,
  )

  const dataSelecionada = new Date(`${diaSelecionado}T12:00:00`)

  /** Navega para o mês anterior/próximo mantendo um dia válido selecionado. */
  function mudarMes(delta: number) {
    const novoMes = new Date(
      mesReferencia.getFullYear(),
      mesReferencia.getMonth() + delta,
      1,
    )
    setMesReferencia(novoMes)
    setDiaSelecionado(paraInputData(novoMes))
  }

  /** Volta para o mês atual e seleciona o dia de hoje. */
  function irParaHoje() {
    const agora = new Date()
    setMesReferencia(inicioDoMes(agora))
    setDiaSelecionado(chaveDoDia(agora))
  }

  /** Abre o modal de criação com valores iniciais baseados no dia selecionado. */
  function abrirNovo() {
    const base = new Date(`${diaSelecionado}T09:00:00`)
    const fim = new Date(base.getTime() + 60 * 60 * 1000)

    setTipoNovo('reuniao')
    setNovoTitulo('')
    setNovaDescricao('')
    setNovoInicio(paraInputDataHora(base))
    setNovoFim(paraInputDataHora(fim))
    setNovoLink('')
    setNovaDataLimite(diaSelecionado)
    setNovoCliente('')
    setNovoValor('')
    setNovaObservacao('')
    setErroFormulario(null)
    setModalNovo(true)
  }

  /** Cria o evento conforme o tipo selecionado no formulário. */
  async function criarEvento(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setSalvando(true)
    setErroFormulario(null)

    try {
      if (tipoNovo === 'reuniao') {
        const titulo = novoTitulo.trim()
        if (!titulo || !novoInicio || !novoFim) {
          setErroFormulario('Informe título, início e fim da reunião.')
          return
        }

        await api.reunioes.create({
          titulo,
          descricao: novaDescricao.trim() || null,
          data_hora_inicio: novoInicio,
          data_hora_fim: novoFim,
          link_reuniao: novoLink.trim() || null,
        })
      } else if (tipoNovo === 'tarefa') {
        const titulo = novoTitulo.trim()
        if (!titulo) {
          setErroFormulario('Informe o título da tarefa.')
          return
        }

        await api.tarefas.create({
          titulo,
          descricao: novaDescricao.trim() || null,
          data_limite: novaDataLimite ? `${novaDataLimite}T23:59:00` : null,
        })
      } else {
        const cliente = novoCliente.trim()
        const valor = Number(novoValor)

        if (!cliente || !valor || !novaDataLimite) {
          setErroFormulario('Informe cliente, valor e vencimento.')
          return
        }

        await api.mensalidades.create({
          nome_cliente: cliente,
          valor,
          data_vencimento: `${novaDataLimite}T12:00:00`,
          observacao: novaObservacao.trim() || null,
        })
      }

      setModalNovo(false)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErroFormulario(mensagemDeErro(falha, 'Não foi possível criar o evento.'))
    } finally {
      setSalvando(false)
    }
  }

  /** Alterna a conclusão de uma tarefa pessoal. */
  async function alternarTarefa(tarefa: TarefaPessoal) {
    const novoStatus: StatusTarefa =
      tarefa.status === 'CONCLUIDA' ? 'PENDENTE' : 'CONCLUIDA'

    try {
      await api.tarefas.status(tarefa.id, novoStatus)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível atualizar a tarefa.'))
    }
  }

  /** Marca uma mensalidade como paga (somente administradores). */
  async function pagarMensalidade(mensalidade: Mensalidade) {
    if (!ehAdmin) return

    try {
      await api.mensalidades.pagar(mensalidade.id)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível registrar o pagamento.'))
    }
  }

  /** Exclui uma reunião do usuário (ou qualquer uma, se administrador). */
  async function excluirReuniao(reuniao: Reuniao) {
    if (!window.confirm(`Excluir a reunião "${reuniao.titulo}"?`)) return

    try {
      await api.reunioes.remove(reuniao.id)
      setVersao((valor) => valor + 1)
    } catch (falha) {
      setErro(mensagemDeErro(falha, 'Não foi possível excluir a reunião.'))
    }
  }

  return (
    <div className="page agenda">
      <div className="agenda-grid">
        <section className="panel calendar-panel">
          <div className="calendar-head">
            <h3>{nomeMes}</h3>
            <div className="calendar-nav">
              <button className="btn-ghost sm" onClick={() => mudarMes(-1)}>
                <IconChevronRight size={15} style={{ transform: 'rotate(180deg)' }} />
              </button>
              <button className="btn-ghost sm" onClick={irParaHoje}>
                <IconCalendar size={15} /> Hoje
              </button>
              <button className="btn-ghost sm" onClick={() => mudarMes(1)}>
                <IconChevronRight size={15} />
              </button>
              <button className="btn-primary sm" onClick={abrirNovo}>
                <IconPlus size={15} /> Novo
              </button>
            </div>
          </div>

          <div className="calendar-week">
            {diasDaSemana.map((dia) => (
              <span key={dia}>{dia}</span>
            ))}
          </div>

          <div className="calendar-grid">
            {celulas.map((data, indice) => {
              if (!data) return <div className="day empty" key={`vazio-${indice}`} />

              const chave = chaveDoDia(data)
              const eventos = eventosPorDia.get(chave)
              const ehHoje = chave === chaveDoDia(new Date())
              const selecionado = chave === diaSelecionado

              return (
                <div
                  className={`day${ehHoje ? ' today' : ''}${eventos ? ' has-events' : ''}${
                    selecionado ? ' selected' : ''
                  }`}
                  key={chave}
                  onClick={() => setDiaSelecionado(chave)}
                >
                  <span className="day-num">{data.getDate()}</span>
                  {eventos && (
                    <span className="day-dots">
                      {eventos.reunioes > 0 && <i className="dot-green" />}
                      {eventos.tarefas > 0 && <i className="dot-violet" />}
                      {eventos.mensalidades > 0 && <i className="dot-amber" />}
                    </span>
                  )}
                </div>
              )
            })}
          </div>

          <div className="calendar-legend">
            <span>
              <i className="dot-green" /> Reuniões
            </span>
            <span>
              <i className="dot-violet" /> Tarefas
            </span>
            <span>
              <i className="dot-amber" /> Mensalidades
            </span>
          </div>
        </section>

        <div className="agenda-side">
          {erro && <div className="form-error">{erro}</div>}

          <section className="panel">
            <div className="panel-head">
              <h3>Reuniões</h3>
              <span className="chip">{formatarDia(dataSelecionada)}</span>
            </div>
            <div className="list">
              {carregando && <div className="empty-inline">Carregando...</div>}
              {!carregando && reunioesDoDia.length === 0 && (
                <div className="empty-inline">Nenhuma reunião neste dia.</div>
              )}
              {!carregando &&
                reunioesDoDia.map((reuniao) => (
                  <div className="list-row" key={reuniao.id}>
                    <div className="time-chip">
                      {formatarHora(reuniao.data_hora_inicio)}
                    </div>
                    <div className="list-row-body">
                      <strong>{reuniao.titulo}</strong>
                      <span>
                        <IconUsers size={13} /> {reuniao.participantes.length} participante(s)
                      </span>
                    </div>
                    {reuniao.link_reuniao && (
                      <a
                        className="icon-btn sm"
                        href={reuniao.link_reuniao}
                        target="_blank"
                        rel="noreferrer"
                        title="Abrir link da reunião"
                      >
                        <IconExternal size={15} />
                      </a>
                    )}
                    {(ehAdmin || reuniao.criador_id === usuario.id) && (
                      <button
                        className="icon-btn sm danger"
                        title="Excluir reunião"
                        onClick={() => excluirReuniao(reuniao)}
                      >
                        <IconTrash size={15} />
                      </button>
                    )}
                  </div>
                ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-head">
              <h3>Tarefas pessoais</h3>
              <span className="muted">
                <IconPlus size={14} /> nova
              </span>
            </div>
            <div className="list">
              {!carregando && tarefasDoDia.length === 0 && (
                <div className="empty-inline">Nenhuma tarefa para este dia.</div>
              )}
              {tarefasDoDia.map((tarefa) => (
                <div className="list-row" key={tarefa.id}>
                  <button
                    className={`checkbox${tarefa.status === 'CONCLUIDA' ? ' checked' : ''}`}
                    onClick={() => alternarTarefa(tarefa)}
                    aria-label={
                      tarefa.status === 'CONCLUIDA'
                        ? 'Reabrir tarefa'
                        : 'Concluir tarefa'
                    }
                  >
                    {tarefa.status === 'CONCLUIDA' && <IconCheck size={12} />}
                  </button>
                  <div className="list-row-body">
                    <strong className={tarefa.status === 'CONCLUIDA' ? 'strike' : ''}>
                      {tarefa.titulo}
                    </strong>
                    <span>
                      <IconClock size={13} /> vence {formatarDia(new Date(`${diaSelecionado}T12:00:00`))}
                    </span>
                  </div>
                  <span
                    className={`pill pill-${
                      tarefa.status === 'CONCLUIDA'
                        ? 'green'
                        : tarefa.status === 'EM_ANDAMENTO'
                          ? 'blue'
                          : 'amber'
                    }`}
                  >
                    {rotuloTarefa(tarefa.status)}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-head">
              <h3>Mensalidades clientes</h3>
              <span className="muted">
                <IconMessage size={14} /> {ehAdmin ? 'cobrar' : 'somente leitura'}
              </span>
            </div>
            <div className="list">
              {!carregando && mensalidadesDoDia.length === 0 && (
                <div className="empty-inline">Nenhuma mensalidade neste dia.</div>
              )}
              {mensalidadesDoDia.map((mensalidade) => (
                <div className="list-row" key={mensalidade.id}>
                  <div className="list-row-body">
                    <strong>{mensalidade.nome_cliente}</strong>
                    <span>vence {formatarDia(new Date(mensalidade.data_vencimento))}</span>
                  </div>
                  <div className="bill-value">
                    <b>{formatarValor(mensalidade.valor)}</b>
                    <span
                      className={`pill pill-${
                        mensalidade.status_pagamento === 'PAGO'
                          ? 'green'
                          : mensalidade.status_pagamento === 'ATRASADO'
                            ? 'red'
                            : 'amber'
                      }`}
                    >
                      {mensalidade.status_pagamento === 'PAGO' ? 'PAGA' : mensalidade.status_pagamento}
                    </span>
                  </div>
                  {ehAdmin && mensalidade.status_pagamento !== 'PAGO' && (
                    <button
                      className="icon-btn sm"
                      title="Registrar pagamento"
                      onClick={() => pagarMensalidade(mensalidade)}
                    >
                      <IconCheck size={15} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      {modalNovo && (
        <Modal titulo="Novo evento" onClose={() => setModalNovo(false)}>
          <form className="form-grid" onSubmit={criarEvento}>
            <label className="field">
              <span>Tipo</span>
              <select
                value={tipoNovo}
                onChange={(evento) =>
                  setTipoNovo(
                    evento.target.value as 'reuniao' | 'tarefa' | 'mensalidade',
                  )
                }
              >
                <option value="reuniao">Reunião</option>
                <option value="tarefa">Tarefa pessoal</option>
                {ehAdmin && <option value="mensalidade">Mensalidade de cliente</option>}
              </select>
            </label>

            {tipoNovo === 'mensalidade' ? (
              <>
                <label className="field">
                  <span>Cliente</span>
                  <input
                    type="text"
                    value={novoCliente}
                    onChange={(evento) => setNovoCliente(evento.target.value)}
                    placeholder="Nome do cliente"
                  />
                </label>

                <div className="form-row">
                  <label className="field">
                    <span>Valor (R$)</span>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={novoValor}
                      onChange={(evento) => setNovoValor(evento.target.value)}
                      placeholder="0,00"
                    />
                  </label>

                  <label className="field">
                    <span>Vencimento</span>
                    <input
                      type="date"
                      value={novaDataLimite}
                      onChange={(evento) => setNovaDataLimite(evento.target.value)}
                    />
                  </label>
                </div>

                <label className="field">
                  <span>Observação</span>
                  <textarea
                    rows={2}
                    value={novaObservacao}
                    onChange={(evento) => setNovaObservacao(evento.target.value)}
                    placeholder="Opcional"
                  />
                </label>
              </>
            ) : (
              <>
                <label className="field">
                  <span>Título</span>
                  <input
                    type="text"
                    value={novoTitulo}
                    onChange={(evento) => setNovoTitulo(evento.target.value)}
                    placeholder={
                      tipoNovo === 'reuniao' ? 'Ex.: Planejamento semanal' : 'Ex.: Revisar relatório'
                    }
                  />
                </label>

                <label className="field">
                  <span>Descrição</span>
                  <textarea
                    rows={2}
                    value={novaDescricao}
                    onChange={(evento) => setNovaDescricao(evento.target.value)}
                    placeholder="Opcional"
                  />
                </label>

                {tipoNovo === 'reuniao' ? (
                  <>
                    <div className="form-row">
                      <label className="field">
                        <span>Início</span>
                        <input
                          type="datetime-local"
                          value={novoInicio}
                          onChange={(evento) => setNovoInicio(evento.target.value)}
                        />
                      </label>

                      <label className="field">
                        <span>Fim</span>
                        <input
                          type="datetime-local"
                          value={novoFim}
                          onChange={(evento) => setNovoFim(evento.target.value)}
                        />
                      </label>
                    </div>

                    <label className="field">
                      <span>Link da reunião</span>
                      <input
                        type="text"
                        value={novoLink}
                        onChange={(evento) => setNovoLink(evento.target.value)}
                        placeholder="https://..."
                      />
                    </label>
                  </>
                ) : (
                  <label className="field">
                    <span>Data limite</span>
                    <input
                      type="date"
                      value={novaDataLimite}
                      onChange={(evento) => setNovaDataLimite(evento.target.value)}
                    />
                  </label>
                )}
              </>
            )}

            {erroFormulario && <div className="form-error">{erroFormulario}</div>}

            <div className="form-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setModalNovo(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="btn-primary" disabled={salvando}>
                {salvando ? 'Salvando...' : 'Criar'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
