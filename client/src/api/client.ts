/**
 * Cliente HTTP central da aplicação.
 *
 * Responsabilidades:
 * - montar a URL base da API;
 * - anexar o token JWT em todas as requisições autenticadas;
 * - renovar o access token automaticamente usando o refresh token;
 * - padronizar erros da API em uma única classe (ApiError);
 * - expor métodos tipados por recurso para os componentes.
 */
import type {
  Arquivo,
  BacklogItem,
  BacklogPayload,
  Categoria,
  Chatbot,
  ChatbotPayload,
  ChatMensagem,
  ChatResposta,
  DashboardResumo,
  Link,
  LinkPayload,
  Mensalidade,
  MensalidadePayload,
  MensalidadeResumo,
  Notebook,
  NotebookPayload,
  Notificacao,
  Page,
  Pasta,
  Reuniao,
  ReuniaoPayload,
  RespostaBusca,
  Setor,
  SetorPayload,
  TarefaPessoal,
  TarefaPayload,
  TokenResponse,
  Usuario,
  UsuarioCreatePayload,
} from './types'

/** URL da API. Pode ser trocada por variável de ambiente no build. */
const API_URL = (
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api'
).replace(/\/$/, '')

/** Chaves usadas no localStorage para persistir a sessão entre recarregamentos. */
const ACCESS_TOKEN_KEY = 'focus-access-token'
const REFRESH_TOKEN_KEY = 'focus-refresh-token'

/** Erro padronizado para que a interface consiga exibir mensagens amigáveis. */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** Recupera o access token salvo, se existir. */
export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

/** Recupera o refresh token salvo, se existir. */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/** Salva os dois tokens após login ou renovação. */
export function saveTokens(tokens: TokenResponse): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token)
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
}

/** Remove a sessão local. */
export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

/** Extrai a mensagem mais útil possível de um corpo de erro da API. */
function extrairDetalhe(payload: unknown, fallback: string): string {
  if (typeof payload === 'string' && payload.trim()) return payload
  if (payload && typeof payload === 'object') {
    const detail = (payload as { detail?: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (item && typeof item === 'object' && 'msg' in item) {
            return String((item as { msg: unknown }).msg)
          }
          return String(item)
        })
        .join('; ')
    }
  }
  return fallback
}

/** Monta query strings ignorando valores vazios. */
function queryString(params?: Record<string, string | number | boolean | null | undefined>): string {
  if (!params) return ''
  const search = new URLSearchParams()
  Object.entries(params).forEach(([chave, valor]) => {
    if (valor !== undefined && valor !== null && valor !== '') {
      search.append(chave, String(valor))
    }
  })
  const texto = search.toString()
  return texto ? `?${texto}` : ''
}

/** Evita disparar várias renovações simultâneas quando o token expira. */
let renovacaoEmAndamento: Promise<boolean> | null = null

/** Tenta renovar o access token com o refresh token salvo. */
async function renovarToken(): Promise<boolean> {
  if (renovacaoEmAndamento) return renovacaoEmAndamento

  renovacaoEmAndamento = (async () => {
    const refreshToken = getRefreshToken()
    if (!refreshToken) return false

    try {
      const resposta = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!resposta.ok) {
        clearTokens()
        return false
      }

      const tokens = (await resposta.json()) as TokenResponse
      saveTokens(tokens)
      return true
    } catch {
      clearTokens()
      return false
    } finally {
      renovacaoEmAndamento = null
    }
  })()

  return renovacaoEmAndamento
}

/**
 * Executa uma requisição já com autenticação e renovação automática.
 * O retry acontece apenas uma vez para evitar loops infinitos.
 */
async function executarFetch(
  path: string,
  options: RequestInit = {},
  tentarRenovar = true,
): Promise<Response> {
  const headers = new Headers(options.headers)
  const token = getAccessToken()
  const body = options.body

  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (body && !(body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const resposta = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (
    resposta.status === 401 &&
    tentarRenovar &&
    getRefreshToken() &&
    !path.startsWith('/auth/login') &&
    !path.startsWith('/auth/refresh') &&
    !path.startsWith('/auth/registrar')
  ) {
    const renovado = await renovarToken()
    if (renovado) return executarFetch(path, options, false)
  }

  return resposta
}

/** Faz uma requisição e devolve o JSON tipado, lançando ApiError em falhas. */
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const resposta = await executarFetch(path, options)
  const texto = await resposta.text()

  let payload: unknown = null
  if (texto) {
    try {
      payload = JSON.parse(texto)
    } catch {
      payload = texto
    }
  }

  if (!resposta.ok) {
    throw new ApiError(
      resposta.status,
      extrairDetalhe(payload, `Falha na requisição (${resposta.status})`),
    )
  }

  return payload as T
}

/** Faz uma requisição binária (download de arquivo). */
async function requestBlob(path: string): Promise<Blob> {
  const resposta = await executarFetch(path)
  if (!resposta.ok) {
    throw new ApiError(resposta.status, 'Não foi possível baixar o arquivo')
  }
  return resposta.blob()
}

/**
 * Fachada tipada da API.
 * Os componentes importam apenas `api` e não precisam montar URLs manualmente.
 */
export const api = {
  auth: {
    login: (email: string, senha: string) =>
      request<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, senha }),
      }),

    registrar: (dados: UsuarioCreatePayload) =>
      request<Usuario>('/auth/registrar', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),

    me: () => request<Usuario>('/auth/me'),

    alterarSenha: (senha_atual: string, nova_senha: string) =>
      request<{ mensagem: string }>('/auth/alterar-senha', {
        method: 'POST',
        body: JSON.stringify({ senha_atual, nova_senha }),
      }),
  },

  usuarios: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Usuario>>(`/usuarios/${queryString(params)}`),
    create: (dados: UsuarioCreatePayload) =>
      request<Usuario>('/usuarios/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
  },

  setores: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Setor>>(`/setores/${queryString(params)}`),
    create: (dados: SetorPayload) =>
      request<Setor>('/setores/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
  },

  dashboard: {
    resumo: () => request<DashboardResumo>('/dashboard/resumo'),
  },

  busca: (termo: string) =>
    request<RespostaBusca>(`/busca/${queryString({ q: termo })}`),

  arquivos: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Arquivo>>(`/arquivos/${queryString(params)}`),

    upload: (arquivo: File, titulo: string, categoriaId?: number, pastaId?: number) => {
      const form = new FormData()
      form.append('arquivo', arquivo)
      form.append('titulo', titulo)
      if (categoriaId) form.append('categoria_id', String(categoriaId))
      if (pastaId) form.append('pasta_id', String(pastaId))
      return request<Arquivo>('/arquivos/upload', { method: 'POST', body: form })
    },

    download: (id: number) => requestBlob(`/arquivos/${id}/download`),

    update: (id: number, dados: { titulo?: string; categoria_id?: number | null; pasta_id?: number | null }) =>
      request<Arquivo>(`/arquivos/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
      }),

    remove: (id: number) =>
      request<{ mensagem: string }>(`/arquivos/${id}`, { method: 'DELETE' }),
  },

  categorias: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Categoria>>(`/categorias/${queryString(params)}`),
    create: (dados: { nome: string; descricao?: string | null }) =>
      request<Categoria>('/categorias/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
  },

  pastas: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Pasta>>(`/pastas/${queryString(params)}`),
    create: (dados: { nome: string; descricao?: string | null; pasta_pai_id?: number | null }) =>
      request<Pasta>('/pastas/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
  },

  links: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Link>>(`/links/${queryString(params)}`),
    create: (dados: LinkPayload) =>
      request<Link>('/links/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/links/${id}`, { method: 'DELETE' }),
  },

  backlog: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<BacklogItem>>(`/backlog/${queryString(params)}`),
    create: (dados: BacklogPayload) =>
      request<BacklogItem>('/backlog/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    update: (id: number, dados: Partial<BacklogPayload>) =>
      request<BacklogItem>(`/backlog/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
      }),
    status: (id: number, status: BacklogItem['status']) =>
      request<BacklogItem>(`/backlog/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/backlog/${id}`, { method: 'DELETE' }),
  },

  reunioes: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Reuniao>>(`/reunioes/${queryString(params)}`),
    create: (dados: ReuniaoPayload) =>
      request<Reuniao>('/reunioes/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    update: (id: number, dados: Partial<ReuniaoPayload>) =>
      request<Reuniao>(`/reunioes/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
      }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/reunioes/${id}`, { method: 'DELETE' }),
  },

  tarefas: {
    minhas: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<TarefaPessoal>>(`/tarefas-pessoais/minhas${queryString(params)}`),
    create: (dados: TarefaPayload) =>
      request<TarefaPessoal>('/tarefas-pessoais/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    status: (id: number, status: TarefaPessoal['status']) =>
      request<TarefaPessoal>(`/tarefas-pessoais/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/tarefas-pessoais/${id}`, { method: 'DELETE' }),
  },

  mensalidades: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Mensalidade>>(`/mensalidades/${queryString(params)}`),
    create: (dados: MensalidadePayload) =>
      request<Mensalidade>('/mensalidades/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    pagar: (id: number, data_pagamento?: string | null) =>
      request<Mensalidade>(`/mensalidades/${id}/pagar`, {
        method: 'PATCH',
        body: JSON.stringify({ data_pagamento: data_pagamento ?? null }),
      }),
    resumo: () => request<MensalidadeResumo>('/mensalidades/resumo'),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/mensalidades/${id}`, { method: 'DELETE' }),
  },

  chatbots: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Chatbot>>(`/chatbots/${queryString(params)}`),
    create: (dados: ChatbotPayload) =>
      request<Chatbot>('/chatbots/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    update: (id: number, dados: Partial<ChatbotPayload>) =>
      request<Chatbot>(`/chatbots/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
      }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/chatbots/${id}`, { method: 'DELETE' }),
    mensagens: (id: number, params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<ChatMensagem>>(`/chatbots/${id}/mensagens${queryString(params)}`),
    enviar: (id: number, conteudo: string) =>
      request<ChatResposta>(`/chatbots/${id}/mensagens`, {
        method: 'POST',
        body: JSON.stringify({ conteudo }),
      }),
  },

  notebooks: {
    list: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Notebook>>(`/notebooks/${queryString(params)}`),
    create: (dados: NotebookPayload) =>
      request<Notebook>('/notebooks/', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    update: (id: number, dados: Partial<NotebookPayload>) =>
      request<Notebook>(`/notebooks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
      }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/notebooks/${id}`, { method: 'DELETE' }),
  },

  notificacoes: {
    minhas: (params?: Record<string, string | number | boolean | null | undefined>) =>
      request<Page<Notificacao>>(`/notificacoes/minhas${queryString(params)}`),
    ler: (id: number) =>
      request<Notificacao>(`/notificacoes/${id}/ler`, { method: 'PATCH' }),
    lerTodas: () =>
      request<{ mensagem: string }>('/notificacoes/ler-todas', { method: 'PATCH' }),
    remove: (id: number) =>
      request<{ mensagem: string }>(`/notificacoes/${id}`, { method: 'DELETE' }),
  },
}
