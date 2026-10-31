import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { applyTheme, readStoredTheme, THEMES } from '../theme'
import type { Mode, StoredTheme, ThemeName } from '../theme'
import { IconCheck, IconMoon, IconPalette, IconSun } from './icons'

export default function ThemePicker() {
  const [theme, setTheme] = useState<StoredTheme>(() => readStoredTheme())
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [])

  function select(name: ThemeName) {
    const next = { ...theme, name }
    setTheme(next)
    applyTheme(next)
  }

  function setMode(mode: Mode) {
    const next = { ...theme, mode }
    setTheme(next)
    applyTheme(next)
  }

  return (
    <div className="theme-picker" ref={rootRef}>
      <button className="icon-btn" aria-label="Tema" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
        <IconPalette size={19} />
      </button>
      {open && (
        <div className="theme-picker-pop" role="menu">
          <p className="theme-picker-label">Cor de destaque</p>
          <div className="theme-swatches">
            {THEMES.map((t) => (
              <button
                key={t.id}
                className={`theme-swatch${theme.name === t.id ? ' active' : ''}`}
                style={{ '--swatch': t.brand } as CSSProperties}
                title={t.label}
                aria-label={t.label}
                onClick={() => select(t.id)}
              >
                {theme.name === t.id && <IconCheck size={14} />}
              </button>
            ))}
          </div>
          <div className="theme-picker-divider" />
          <div className="theme-mode-row">
            <span>Modo</span>
            <div className="theme-mode-toggle">
              <button
                type="button"
                className={theme.mode === 'light' ? 'active' : ''}
                onClick={() => setMode('light')}
              >
                <IconSun size={15} />
                Claro
              </button>
              <button
                type="button"
                className={theme.mode === 'dark' ? 'active' : ''}
                onClick={() => setMode('dark')}
              >
                <IconMoon size={15} />
                Escuro
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}