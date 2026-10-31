import { useState } from 'react'
import type { FormEvent } from 'react'
import { IconBot, IconCheck, IconDots, IconPlus, IconRefresh, IconSend } from './icons'

type BotStatus = 'active' | 'online' | 'idle' | 'offline'

interface Bot {
  name: string
  version: string
  status: BotStatus
  desc: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  meta?: string
}

const bots: Bot[] = [
  { name: 'Focus AI Assistant', version: 'v2.1', status: 'active', desc: 'Assistente geral do sistema' },
  { name: 'Atendimento', version: 'v1.4', status: 'online', desc: 'Respostas a clientes' },
  { name: 'Logística', version: 'v1.0', status: 'idle', desc: 'Rastreio de entregas' },
  { name: 'Supply Chain', version: 'v2.0', status: 'online', desc: 'Gestão de fornecedores' },
  { name: 'IT Support', version: 'v1.2', status: 'offline', desc: 'Suporte interno de TI' },
  { name: 'Relatórios', version: 'v1.6', status: 'online', desc: 'Geração de dashboards' },
]

const initialMessages: ChatMessage[] = [
  {
    role: 'user',
    text: 'Você pode resumir os logs recentes do serviço de autenticação? Tivemos um pico de erros 500 por volta das 2h da manhã.',
  },
  {
    role: 'assistant',
    text:
      'Analisei os logs de auth-service-prod entre 01:30 e 02:30. Resumo:\n\n• Total de erros 500 registrados: 142\n• Causa principal: timeout de conexão com o cache de sessão Redis\n• Impacto secundário: consultas de fallback sobrecarregaram a réplica do banco',
    meta: 'fonte: auth-service-prod.log',
  },
]

function statusLabel(s: BotStatus) {
  switch (s) {
    case 'active':
      return 'Active'
    case 'online':
      return 'Online'
    case 'idle':
      return 'Idle'
    case 'offline':
      return 'Offline'
  }
}

function promptReply(prompt: string): ChatMessage[] {
  const lower = prompt.toLowerCase()
  if (lower.includes('jira') || lower.includes('ticket')) {
    return [
      {
        role: 'assistant',
        text:
          'Perfeito. Criei o ticket INC-4821 no Jira com o relatório completo, anexando o trecho dos logs acima e as indicações de causa do incidente.',
        meta: 'ticket: INC-4821',
      },
    ]
  }
  return [
    {
      role: 'assistant',
      text:
        'Entendido. Vou encaminhar essa solicitação para a equipe de backend e acompanhar até a resolução. Posso gerar um ticket no Jira para rastrear o acompanhamento?',
    },
  ]
}

export default function Chatbots() {
  const [selected, setSelected] = useState(0)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [thinking, setThinking] = useState(false)
  const active = bots[selected]

  function sendText(text: string) {
    const clean = text.trim()
    if (!clean) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text: clean }])
    setThinking(true)
    setTimeout(() => {
      setMessages((m) => [...m, ...promptReply(clean)])
      setThinking(false)
    }, 700)
  }

  function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    sendText(input)
  }

  return (
    <div className="page chatbots-page">
      <aside className="panel bots-panel">
        <div className="bots-head">
          <div>
            <h3>Active Bots</h3>
            <span className="muted">{bots.length} bots configurados</span>
          </div>
          <button className="icon-btn" title="Atualizar">
            <IconRefresh size={16} />
          </button>
        </div>

        <div className="bots-list">
          {bots.map((b, i) => (
            <button
              className={`bot-row${i === selected ? ' active' : ''}`}
              key={b.name}
              onClick={() => setSelected(i)}
            >
              <span className={`bot-avatar ${b.status}`}>
                <IconBot size={19} />
              </span>
              <span className="bot-row-body">
                <strong>{b.name}</strong>
                <span>{b.desc}</span>
              </span>
              <span className={`pill pill-${b.status === 'active' ? 'violet' : b.status === 'online' ? 'green' : b.status === 'idle' ? 'amber' : 'red'}`}>
                {statusLabel(b.status)}
              </span>
            </button>
          ))}
        </div>

        <button className="btn-primary bots-create">
          <IconPlus size={17} /> Create New Bot
        </button>
      </aside>

      <section className="panel chat-panel">
        <header className="chat-head">
          <div className="chat-bot">
            <span className="bot-avatar active">
              <IconBot size={20} />
            </span>
            <div>
              <h3>{active.name}</h3>
              <span>
                <i className="status-dot on" /> {active.version} Active
              </span>
            </div>
          </div>
          <div className="chat-meta">
            <span className="chip">
              session started today at 09:41
            </span>
            <span className="chip model-chip">Model: GPT-4o</span>
            <span className="chip model-chip">Context Window: 128k</span>
            <button className="icon-btn">
              <IconDots size={18} />
            </button>
          </div>
        </header>

        <div className="chat-body">
          {messages.map((m, i) => (
            <div className={`msg ${m.role}`} key={i}>
              <span className={`msg-avatar ${m.role}`}>
                {m.role === 'user' ? <IconBot size={15} /> : <IconBot size={15} />}
              </span>
              <div className="msg-bubble">
                <p>{m.text}</p>
                {m.meta && <span className="msg-meta">{m.meta}</span>}
              </div>
            </div>
          ))}

          <div className="logs-block">
            <div className="logs-head">
              <span className="status-dot on" />
              <strong>auth-service-prod</strong>
              <span className="muted">últimos eventos</span>
            </div>
            <pre>{`[02:04:11] ERROR  RedisTimeoutException  Failed to acquire connection from pool
[02:04:12] WARN   Fallback Postgres initiated  (Load: High)
[02:15:01] INFO   Redis cluster failover completed — connection restored`}</pre>
            <div className="logs-foot">
              <button className="btn-ghost sm">
                <IconCheck size={14} /> Resolvido
              </button>
              <button className="btn-ghost sm">
                Criar ticket no Jira
              </button>
            </div>
          </div>

          {thinking && (
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

        <footer className="composer">
          <form className="composer-box" onSubmit={send}>
            <textarea
              rows={1}
              value={input}
              placeholder="Envie uma mensagem para o assistente…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  sendText(e.currentTarget.value)
                }
              }}
            />
            <button type="submit" className="composer-send" aria-label="Enviar" disabled={!input.trim()}>
              <IconSend size={17} />
            </button>
          </form>
          <div className="composer-hints">
            <span>
              <b>Shift+Enter</b> para nova linha
            </span>
            <span className="muted">A IA pode cometer erros — verifique informações críticas.</span>
          </div>
        </footer>
      </section>
    </div>
  )
}