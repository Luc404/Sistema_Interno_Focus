import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { IconX } from './icons'

interface ModalProps {
  /** Título exibido no cabeçalho do modal. */
  titulo: string
  /** Fecha o modal ao clicar no X, no backdrop ou pressionar Escape. */
  onClose: () => void
  children: ReactNode
}

/**
 * Modal genérico usado pelos formulários de criação/edição.
 * O clique no backdrop só fecha quando o alvo é o próprio backdrop, evitando
 * fechar o formulário ao clicar dentro do card.
 */
export default function Modal({ titulo, onClose, children }: ModalProps) {
  // Permite fechar o modal com Escape, mantendo o padrão de acessibilidade.
  useEffect(() => {
    function aoPressionar(evento: KeyboardEvent) {
      if (evento.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', aoPressionar)
    return () => document.removeEventListener('keydown', aoPressionar)
  }, [onClose])

  return (
    <div
      className="modal-backdrop"
      onMouseDown={(evento) => {
        if (evento.target === evento.currentTarget) onClose()
      }}
    >
      <div className="modal-card" role="dialog" aria-modal="true" aria-label={titulo}>
        <header className="modal-head">
          <h3>{titulo}</h3>
          <button className="icon-btn sm" aria-label="Fechar" onClick={onClose}>
            <IconX size={15} />
          </button>
        </header>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  )
}
