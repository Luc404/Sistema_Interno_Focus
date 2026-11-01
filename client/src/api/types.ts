/**
 * Tipos compartilhados entre a interface e a API.
 * Mantemos os nomes dos campos iguais aos schemas do backend para evitar
 * conversões desnecessárias e deixar o contrato explícito.
 */

export type Perfil = 'ADMIN' | 'MEMBRO'
export type StatusBacklog = 'PENDENTE' | 'EM_ANDAMENTO' | 'CONCLUIDO'
export type PrioridadeBacklog = 'BAIXA' | 'MEDIA' | 'ALTA'
export type TipoBacklog = 'FEATURE' | 'BUG' | 'MELHORIA' | 'INFRA' | 'OUTRO'
export type StatusTarefa = 'PENDENTE' | 'EM_ANDAMENTO' | 'CONCLUIDA'
export type StatusMensalidade = 'PENDENTE' | 'PAGO' | 'ATRASADO'
export type StatusChatbot = 'ACTIVE' | 'ONLINE' | 'IDLE' | 'OFFLINE'
export type PapelMensagem = 'USER' | 'ASSISTANT'
export type TipoNotificacao = 'INFO' | 'ALERTA' | 'SUCESSO' | 'REUNIAO' | 'TAREFA' | 'FINANCEIRO'

/** Envelope padrão das listagens paginadas do backend. */
export interface Page<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

/** Resposta do login/refresh com os dois tokens JWT. */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface Usuario {
  id: number
  nome_completo: string
  email: string
  cargo: string | null
  perfil: Perfil
  ativo: boolean
  data_cadastro: string
  setor_id: number | null
}

export interface UsuarioResumo {
  id: number
  nome_completo: string
  email: string
  perfil: Perfil
}

export interface UsuarioCreatePayload {
  nome_completo: string
  email: string
  senha: string
  cargo?: string | null
  perfil?: Perfil
  setor_id?: number | null
}

export interface UsuarioUpdatePayload {
  nome_completo?: string
  email?: string
  cargo?: string | null
  perfil?: Perfil
  setor_id?: number | null
  ativo?: boolean
}

export interface UsuarioSelfUpdatePayload {
  nome_completo?: string
  cargo?: string | null
}

export interface Setor {
  id: number
  nome: string
  descricao: string | null
  status: 'ATIVO' | 'INATIVO'
  data_criacao: string
}

export interface SetorPayload {
  nome: string
  descricao?: string | null
  status?: 'ATIVO' | 'INATIVO'
}

export interface BacklogItem {
  id: number
  titulo: string
  descricao: string | null
  tipo: TipoBacklog
  prioridade: PrioridadeBacklog
  status: StatusBacklog
  data_criacao: string
  setor_id: number | null
  autor_id: number
}

export interface BacklogPayload {
  titulo: string
  descricao?: string | null
  tipo: TipoBacklog
  prioridade?: PrioridadeBacklog
  status?: StatusBacklog
  setor_id?: number | null
}

export interface Arquivo {
  id: number
  titulo: string
  caminho_arquivo: string
  tipo_mime: string
  categoria: string | null
  categoria_id: number | null
  pasta_id: number | null
  tamanho_bytes: number
  data_upload: string
  usuario_id: number
}

export interface Categoria {
  id: number
  nome: string
  descricao: string | null
  data_criacao: string
}

export interface Pasta {
  id: number
  nome: string
  descricao: string | null
  pasta_pai_id: number | null
  data_criacao: string
}

export interface Link {
  id: number
  titulo: string
  url: string
  descricao: string | null
  categoria: string | null
  data_criacao: string
  usuario_id: number
}

export interface LinkPayload {
  titulo: string
  url: string
  descricao?: string | null
  categoria?: string | null
}

export interface Reuniao {
  id: number
  titulo: string
  descricao: string | null
  data_hora_inicio: string
  data_hora_fim: string
  link_reuniao: string | null
  criador_id: number
  participantes: UsuarioResumo[]
}

export interface ReuniaoPayload {
  titulo: string
  descricao?: string | null
  data_hora_inicio: string
  data_hora_fim: string
  link_reuniao?: string | null
  participantes_ids?: number[]
}

export interface TarefaPessoal {
  id: number
  titulo: string
  descricao: string | null
  data_limite: string | null
  status: StatusTarefa
  usuario_id: number
}

export interface TarefaPayload {
  titulo: string
  descricao?: string | null
  data_limite?: string | null
  status?: StatusTarefa
}

export interface Mensalidade {
  id: number
  nome_cliente: string
  valor: number
  data_vencimento: string
  data_pagamento: string | null
  status_pagamento: StatusMensalidade
  observacao: string | null
}

export interface MensalidadePayload {
  nome_cliente: string
  valor: number
  data_vencimento: string
  status_pagamento?: StatusMensalidade
  observacao?: string | null
}

export interface MensalidadeResumo {
  total: number
  pendentes: number
  pagas: number
  atrasadas: number
  valor_total_pendente: number
  valor_total_recebido: number
}

export interface Chatbot {
  id: number
  nome: string
  descricao: string | null
  versao: string
  status: StatusChatbot
  modelo: string
  data_criacao: string
  criador_id: number
}

export interface ChatbotPayload {
  nome: string
  descricao?: string | null
  versao?: string
  status?: StatusChatbot
  modelo?: string
}

export interface ChatMensagem {
  id: number
  chatbot_id: number
  usuario_id: number
  papel: PapelMensagem
  conteudo: string
  criado_em: string
}

export interface ChatResposta {
  mensagem_usuario: ChatMensagem
  resposta: ChatMensagem
}

export interface Notebook {
  id: number
  grupo: string
  titulo: string
  subtitulo: string | null
  conteudo: string
  tags: string | null
  data_criacao: string
  data_atualizacao: string
  autor_id: number
}

export interface NotebookPayload {
  grupo?: string
  titulo: string
  subtitulo?: string | null
  conteudo: string
  tags?: string | null
}

export interface Notificacao {
  id: number
  titulo: string
  mensagem: string
  tipo: TipoNotificacao
  link: string | null
  lida: boolean
  data_criacao: string
  usuario_id: number
}

export interface NotificacaoPayload {
  usuario_id: number
  titulo: string
  mensagem: string
  tipo?: TipoNotificacao
  link?: string | null
}

export interface ReuniaoResumo {
  id: number
  titulo: string
  data_hora_inicio: string
}

export interface DashboardResumo {
  usuarios_ativos: number
  setores_ativos: number
  arquivos: number
  itens_backlog: number
  itens_backlog_pendentes: number
  mensalidades_pendentes: number
  mensalidades_valor_pendente: number
  tarefas_pendentes: number
  reunioes_hoje: number
  chatbots_ativos: number
  notebooks: number
  notificacoes_nao_lidas: number
  proximas_reunioes: ReuniaoResumo[]
}

export interface ResultadoBusca {
  tipo: string
  id: number
  titulo: string
  descricao: string | null
  extra: string | null
}

export interface RespostaBusca {
  termo: string
  total: number
  resultados: ResultadoBusca[]
}
