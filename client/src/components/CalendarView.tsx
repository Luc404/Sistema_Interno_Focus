import { IconCalendar, IconCheck, IconClock, IconMessage, IconPlus, IconUsers } from './icons'

const weekDays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

const meetings = [
  { day: 27, time: '09:30', title: 'Daily — Desenvolvimento', tag: 'Reunião' },
  { day: 27, time: '14:30', title: 'Planejamento de sprint', tag: 'Reunião' },
  { day: 28, time: '10:00', title: 'Review mensalidades', tag: 'Reunião' },
  { day: 29, time: '16:00', title: '1:1 com Financeiro', tag: 'Reunião' },
]

const tasks = [
  { day: 27, title: 'Revisar migração de banco', status: 'EM ANDAMENTO', done: false },
  { day: 28, title: 'Relatório de vendas de agosto', status: 'PENDENTE', done: false },
  { day: 30, title: 'Atualizar contratos 2026', status: 'EM ANDAMENTO', done: false },
]

const bills = [
  { day: 28, name: 'Cliente — Alpha Corp', value: 'R$ 4.500,00', status: 'PENDENTE' },
  { day: 28, name: 'Cliente — Beta Ltda', value: 'R$ 2.800,00', status: 'PENDENTE' },
  { day: 2, name: 'Cliente — Gama SA', value: 'R$ 6.200,00', status: 'PAGA' },
]

function buildMonth() {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const first = new Date(year, month, 1)
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const startOffset = first.getDay()
  const cells: (number | null)[] = []
  for (let i = 0; i < startOffset; i += 1) cells.push(null)
  for (let d = 1; d <= daysInMonth; d += 1) cells.push(d)
  return { year, month, cells, today: now.getDate() }
}

export default function CalendarView() {
  const { year, month, cells, today } = buildMonth()
  const monthName = new Date(year, month, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })

  const eventDays = new Set([27, 28, 29])

  return (
    <div className="page agenda">
      <div className="agenda-grid">
        <section className="panel calendar-panel">
          <div className="calendar-head">
            <h3>{monthName}</h3>
            <div className="calendar-nav">
              <button className="icon-btn">
                <IconCalendar size={16} />
              </button>
              <button className="btn-primary sm">
                <IconPlus size={15} /> Novo
              </button>
            </div>
          </div>

          <div className="calendar-week">
            {weekDays.map((d) => (
              <span key={d}>{d}</span>
            ))}
          </div>

          <div className="calendar-grid">
            {cells.map((d, i) => (
              <div
                className={`day${d === today ? ' today' : ''}${d !== null && eventDays.has(d) ? ' has-events' : ''}`}
                key={i}
              >
                {d !== null && (
                  <>
                    <span className="day-num">{d}</span>
                    {eventDays.has(d) && <i className="day-events" />}
                  </>
                )}
              </div>
            ))}
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
          <section className="panel">
            <div className="panel-head">
              <h3>Reuniões</h3>
              <span className="chip">Hoje</span>
            </div>
            <div className="list">
              {meetings.map((m) => (
                <div className="list-row" key={m.title}>
                  <div className="time-chip">{m.time}</div>
                  <div className="list-row-body">
                    <strong>{m.title}</strong>
                    <span>dia {m.day} · {m.tag}</span>
                  </div>
                  <IconUsers className="muted" size={16} />
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
              {tasks.map((t) => (
                <div className="list-row" key={t.title}>
                  <span className={`checkbox${t.done ? ' checked' : ''}`}>
                    {t.done && <IconCheck size={12} />}
                  </span>
                  <div className="list-row-body">
                    <strong className={t.done ? 'strike' : ''}>{t.title}</strong>
                    <span>
                      <IconClock size={13} /> vence dia {t.day}
                    </span>
                  </div>
                  <span className={`pill pill-${t.status === 'EM ANDAMENTO' ? 'blue' : 'amber'}`}>{t.status}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-head">
              <h3>Mensalidades clientes</h3>
              <span className="muted">
                <IconMessage size={14} /> cobrar
              </span>
            </div>
            <div className="list">
              {bills.map((b) => (
                <div className="list-row" key={b.name}>
                  <div className="list-row-body">
                    <strong>{b.name}</strong>
                    <span>vence dia {b.day}</span>
                  </div>
                  <div className="bill-value">
                    <b>{b.value}</b>
                    <span className={`pill pill-${b.status === 'PAGA' ? 'green' : 'red'}`}>{b.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}