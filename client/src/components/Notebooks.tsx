import { useState } from 'react'
import { IconExternal, IconNotebook, IconPlus, IconSearch, IconTag, IconUsers } from './icons'

interface Doc {
  group: string
  title: string
  subtitle: string
  updated: string
  content: string[]
  code?: string
  tags: string[]
}

const docs: Doc[] = [
  {
    group: 'ENGINEERING DOCS',
    title: 'FastAPI Architecture Guidelines',
    subtitle: 'Standardizing dependency injection',
    updated: '2 days ago',
    tags: ['Backend', 'FastAPI', 'Arquitetura'],
    content: [
      'Para garantir alto desempenho e codebases sustentáveis nas ferramentas internas da Focus Solutions, padronizamos a forma como lidamos com injeção de dependência (DI) nos nossos serviços FastAPI.',
      'Esta abordagem minimiza boilerplate e aproveita as capacidades nativas do FastAPI para integração profunda com a camada de banco de dados.',
    ],
    code: `from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()`,
  },
  {
    group: 'ENGINEERING DOCS',
    title: 'Database Migration SOP',
    subtitle: 'Steps for safe alembic downgrades',
    updated: 'Yesterday',
    tags: ['Banco', 'Alembic', 'SOP'],
    content: [
      'Toda alteração de schema deve ser versionada com Alembic e revisada em ambiente de staging antes de ir para produção.',
      'Linha de desligamento: jamais executar downgrades destrutivos em banco compartilhado sem abrir janela de manutenção e comunicar os times afetados.',
    ],
  },
  {
    group: 'ENGINEERING DOCS',
    title: 'Frontend Token Mapping',
    subtitle: 'Connecting Tailwind & Figma vars',
    updated: '3 days ago',
    tags: ['Frontend', 'Design System'],
    content: [
      'Os tokens de design do projeto Stitch devem ser traduzidos 1:1 para CSS custom properties (var).',
      'A cor primária da marca é o violeta Focus (#863BFF) e o lavanda (#E1E1ED) para superfícies de destaque.',
    ],
    code: `:root {
  --brand: #863bff;
  --brand-deep: #7e14ff;
  --lavender: #e1e1ed;
}`,
  },
  {
    group: 'PERSONAL NOTES',
    title: 'Notas da reunião 26/08',
    subtitle: 'Planning da sprint',
    updated: 'Today',
    tags: ['Pessoal', 'Sprint'],
    content: [
      'Definimos as prioridades da sprint: refatorar o módulo de mensalidades e destravar o upload em lote.',
      'Ação: revisar backlog e separar os itens de infraestrutura para a equipe backend.',
    ],
  },
  {
    group: 'PERSONAL NOTES',
    title: 'Ideias de produto',
    subtitle: 'Backlog de ideias',
    updated: '1 week ago',
    tags: ['Pessoal', 'Produto'],
    content: [
      'Explore usar a IA para gerar atas de reunião automaticamente a partir das gravações.',
      'Melhorar a busca global do sistema interno, unificando arquivos, docs e backlog.',
    ],
  },
]

export default function Notebooks() {
  const [selected, setSelected] = useState(0)
  const [group, setGroup] = useState('all')
  const doc = docs[selected]

  const groups = ['all', ...Array.from(new Set(docs.map((d) => d.group)))]

  const visible = docs
    .map((d, i) => ({ d, i }))
    .filter(({ d }) => group === 'all' || d.group === group)

  return (
    <div className="page notebooks">
      <div className="notebooks-toolbar">
        <div className="tabs">
          {groups.map((g) => (
            <button key={g} className={`tab${group === g ? ' active' : ''}`} onClick={() => setGroup(g)}>
              {g === 'all' ? 'Todos' : g === 'PERSONAL NOTES' ? 'Notas pessoais' : 'Docs de engenharia'}
            </button>
          ))}
        </div>
        <div className="nb-actions">
          <label className="search-bar sm">
            <IconSearch size={16} />
            <input type="text" placeholder="Search notebooks" />
          </label>
          <button className="btn-primary sm">
            <IconPlus size={15} /> New Notebook
          </button>
        </div>
      </div>

      <div className="notebooks-grid">
        <aside className="panel nb-list-panel">
          {visible.length === 0 && (
            <div className="nb-empty muted">Nenhum notebook encontrado neste filtro.</div>
          )}
          {visible.map(({ d, i }) => (
            <button
              className={`nb-row${i === selected ? ' active' : ''}`}
              key={d.title}
              onClick={() => setSelected(i)}
            >
              <span className="nb-doc-icon">
                <IconNotebook size={18} />
              </span>
              <span className="nb-row-body">
                <strong>{d.title}</strong>
                <span>{d.subtitle}</span>
                <em>{d.updated}</em>
              </span>
            </button>
          ))}
        </aside>

        <article className="panel nb-viewer">
          <header className="nb-viewer-head">
            <div>
              <span className="nb-breadcrumb">Engineering docs /</span>
              <h3>{doc.title}</h3>
              <p>{doc.subtitle}</p>
            </div>
            <div className="nb-viewer-actions">
              <button className="btn-ghost">
                <IconUsers size={16} /> Colaboradores
              </button>
              <button className="btn-primary">
                <IconExternal size={15} /> Share
              </button>
            </div>
          </header>

          <div className="nb-tags">
            {doc.tags.map((t) => (
              <span className="chip" key={t}>
                <IconTag size={12} /> {t}
              </span>
            ))}
            <span className="muted">Atualizado {doc.updated}</span>
          </div>

          <div className="nb-content">
            {doc.content.map((p, i) => (
              <p key={i}>{p}</p>
            ))}
            <div className="nb-callout">
              <strong>Database Sessions</strong>
              <p>
                Sempre utilize o generator de sessão para garantir o fechamento correto do connection
                pooling, mesmo em caso de exceção. Não instancie sessões diretamente dentro do route handler.
              </p>
              <button className="btn-ghost sm">
                <IconExternal size={13} /> Ver referência completa
              </button>
            </div>
            {doc.code && (
              <pre className="nb-code">
                <span className="nb-code-copy">Python</span>
                <code>{doc.code}</code>
              </pre>
            )}
          </div>
        </article>
      </div>
    </div>
  )
}