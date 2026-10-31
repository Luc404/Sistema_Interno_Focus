import {
  IconCalendar,
  IconChevronRight,
  IconDownload,
  IconFile,
  IconFolder,
  IconLink,
  IconTag,
  IconTrash,
  IconUpload,
  IconUsers,
} from './icons'

const categories = [
  { name: 'Documentos', count: 48, icon: IconFile },
  { name: 'Contratos', count: 12, icon: IconTag },
  { name: 'Mídia', count: 74, icon: IconFolder },
  { name: 'Links úteis', count: 23, icon: IconLink },
  { name: 'Migrations', count: 2, icon: IconFolder },
  { name: 'Modelos', count: 6, icon: IconFolder },
]

const folders = [
  { name: 'Migrations', count: '2 itens' },
  { name: 'Fotos', count: '120 itens' },
  { name: 'Vídeos', count: '15 itens' },
]

const files = [
  { name: 'Brand_Guidelines_v2.pdf', kind: 'pdf', uploader: 'Admin', date: '24 out 2023', size: '12,4 MB' },
  { name: 'Hero_Banner_Dark_Theme.png', kind: 'png', uploader: 'Design', date: '23 out 2023', size: '1,8 MB' },
  { name: '3D_Renders_Source.zip', kind: 'zip', uploader: 'UX Design', date: '20 out 2023', size: '245 MB' },
  { name: 'Manual_Onboarding_2026.pdf', kind: 'pdf', uploader: 'RH', date: '18 out 2023', size: '3,2 MB' },
  { name: 'Layout_Agenda_Anual.svg', kind: 'svg', uploader: 'Design', date: '15 out 2023', size: '412 KB' },
  { name: 'Backup_Database_2023.sql', kind: 'sql', uploader: 'Backend', date: '12 out 2023', size: '18,7 MB' },
]

const fileIcon: Record<string, string> = {
  pdf: 'PDF',
  png: 'PNG',
  zip: 'ZIP',
  svg: 'SVG',
  sql: 'SQL',
}

function kindColor(kind: string) {
  switch (kind) {
    case 'pdf':
      return 'file-pdf'
    case 'png':
      return 'file-image'
    case 'zip':
      return 'file-zip'
    case 'sql':
      return 'file-sql'
    default:
      return 'file-default'
  }
}

export default function Librarium() {
  return (
    <div className="page librarium">
      <div className="tabs">
        <button className="tab active">Files</button>
        <button className="tab">
          <IconUpload size={16} /> Upload File
        </button>
      </div>

      <div className="librarium-grid">
        <aside className="panel librarium-cats">
          <div className="librarium-cat-block">
            <h4>CATEGORIAS</h4>
            <ul>
              {categories.map((c) => {
                const Icon = c.icon
                return (
                  <li key={c.name} className="cat-row">
                    <span>
                      <Icon size={17} />
                      {c.name}
                    </span>
                    {c.count > 0 && <b>{c.count}</b>}
                  </li>
                )
              })}
            </ul>
          </div>

          <div className="librarium-cat-block">
            <h4>FOLDERS</h4>
            <ul>
              {folders.map((f) => (
                <li key={f.name} className="cat-row">
                  <span>
                    <IconFolder size={17} />
                    {f.name}
                  </span>
                  <b>{f.count}</b>
                </li>
              ))}
            </ul>
          </div>

          <div className="storage-card">
            <div className="storage-head">
              <span>Storage Usage</span>
              <strong>245 GB</strong>
            </div>
            <div className="storage-bar">
              <i style={{ width: '38%' }} />
            </div>
            <div className="storage-caption">
              <span>38% utilizado</span>
              <span>de 650 GB</span>
            </div>
          </div>
        </aside>

        <section className="panel file-panel">
          <div className="file-toolbar">
            <div className="file-table-title">
              <h3>ARQUIVOS</h3>
              <span>{files.length} itens</span>
            </div>
            <div className="file-actions">
              <button className="btn-ghost">
                <IconDownload size={16} /> Exportar
              </button>
              <button className="btn-primary">
                <IconUpload size={16} /> Enviar arquivo
              </button>
            </div>
          </div>

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
                {files.map((f) => (
                  <tr key={f.name}>
                    <td>
                      <div className="file-cell">
                        <span className={`file-badge ${kindColor(f.kind)}`}>{fileIcon[f.kind]}</span>
                        <span className="file-name">{f.name}</span>
                      </div>
                    </td>
                    <td>
                      <span className="uploader-cell">
                        <IconUsers size={14} /> {f.uploader}
                      </span>
                    </td>
                    <td>
                      <span className="date-cell">
                        <IconCalendar size={14} /> {f.date}
                      </span>
                    </td>
                    <td className="muted">{f.size}</td>
                    <td>
                      <div className="row-actions">
                        <button className="icon-btn sm" title="Baixar">
                          <IconDownload size={15} />
                        </button>
                        <button className="icon-btn sm danger" title="Excluir">
                          <IconTrash size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="file-foot">
            <span>
              <IconChevronRight size={14} /> Mostrando 1–{files.length} de 182 arquivos
            </span>
            <span className="muted">Fonte: Biblioteca Focus Solutions</span>
          </div>
        </section>
      </div>
    </div>
  )
}