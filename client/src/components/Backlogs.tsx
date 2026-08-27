import { IconAlert, IconPlus, IconTag, IconUsers } from './icons'

type Status = 'PENDENTE' | 'EM ANDAMENTO' | 'CONCLUÍDO'
type Prioridade = 'ALTA' | 'MÉDIA' | 'BAIXA'

interface Item {
  title: string
  desc: string
  tipo: string
  prioridade: Prioridade
  autor: string
  setor: string
}

const items: Record<Status, Item[]> = {
  'PENDENTE': [
    { title: 'Tela de edição de usuário', desc: 'Permitir alterar setor, cargo e perfil de colaboradores.', tipo: 'Feature', prioridade: 'ALTA', autor: 'Marcos', setor: 'Desenvolvimento' },
    { title: 'Corrigir timeout no login', desc: 'Sessões expirando antes do tempo limite em redes lentas.', tipo: 'Bug', prioridade: 'ALTA', autor: 'Rafa', setor: 'Backend' },
    { title: 'Exportar relatório mensal', desc: 'Gerar PDF/CSV do relatório de mensalidades.', tipo: 'Melhoria', prioridade: 'MÉDIA', autor: 'Aline', setor: 'Financeiro' },
  ],
  'EM ANDAMENTO': [
    { title: 'Upload em lote de arquivos', desc: 'Suporte a arrastar múltiplos arquivos na Librarium.', tipo: 'Feature', prioridade: 'ALTA', autor: 'Paula', setor: 'Desenvolvimento' },
    { title: 'Notificações de reunião', desc: 'Lembretes via e-mail 15 min antes do início.', tipo: 'Melhoria', prioridade: 'MÉDIA', autor: 'Leo', setor: 'Backend' },
  ],
  'CONCLUÍDO': [
    { title: 'Login com perfil ADMIN', desc: 'Níveis de acesso por perfil no sistema.', tipo: 'Feature', prioridade: 'ALTA', autor: 'Marcos', setor: 'Desenvolvimento' },
    { title: 'Migração para FastAPI + SQLAlchemy', desc: 'Substituição da camada de persistência antiga.', tipo: 'Infra', prioridade: 'MÉDIA', autor: 'Rafa', setor: 'Backend' },
  ],
}

const columns: { id: Status; dot: string }[] = [
  { id: 'PENDENTE', dot: 'amber' },
  { id: 'EM ANDAMENTO', dot: 'blue' },
  { id: 'CONCLUÍDO', dot: 'green' },
]

function prioClass(p: Prioridade) {
  return p === 'ALTA' ? 'red' : p === 'MÉDIA' ? 'amber' : 'green'
}

export default function Backlogs() {
  return (
    <div className="page backlogs">
      <div className="backlog-head">
        <div className="backlog-filters">
          <button className="filter active">Todas</button>
          <button className="filter">Features</button>
          <button className="filter">Bugs</button>
          <button className="filter">Melhorias</button>
        </div>
        <button className="btn-primary">
          <IconPlus size={16} /> Novo item
        </button>
      </div>

      <div className="kanban">
        {columns.map((col) => (
          <section className="kanban-col" key={col.id}>
            <div className="kanban-head">
              <span className={`kanban-dot dot-${col.dot}`} />
              <strong>{col.id}</strong>
              <b>{items[col.id].length}</b>
            </div>

            <div className="kanban-cards">
              {items[col.id].map((item) => (
                <article className="kanban-card" key={item.title}>
                  <div className="kanban-card-top">
                    <span className="chip">
                      <IconTag size={12} /> {item.tipo}
                    </span>
                    <span className={`chip prio-${prioClass(item.prioridade)}`}>
                      {item.prioridade}
                    </span>
                  </div>
                  <h4>{item.title}</h4>
                  <p>{item.desc}</p>
                  <div className="kanban-card-foot">
                    <span>
                      <IconUsers size={13} /> {item.autor}
                    </span>
                    <span className="muted">{item.setor}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>

      <div className="backlog-foot muted">
        <IconAlert size={15} /> Prioridades ALTAS são resolvidas primeiro. Ordene o quadros pelos filtros acima.
      </div>
    </div>
  )
}