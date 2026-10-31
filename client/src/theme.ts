export type ThemeName = 'violet' | 'blue' | 'green' | 'amber' | 'rose' | 'cyan'
export type Mode = 'dark' | 'light'

export interface ThemeOption {
  id: ThemeName
  label: string
  brand: string
  brandDeep: string
}

export interface StoredTheme {
  name: ThemeName
  mode: Mode
}

export const THEME_STORAGE_KEY = 'focus-theme'

export const THEMES: ThemeOption[] = [
  { id: 'violet', label: 'Violeta', brand: '#863bff', brandDeep: '#7e14ff' },
  { id: 'blue', label: 'Azul', brand: '#3b82f6', brandDeep: '#1d4ed8' },
  { id: 'green', label: 'Verde', brand: '#10b981', brandDeep: '#047857' },
  { id: 'amber', label: 'Âmbar', brand: '#f59e0b', brandDeep: '#d97706' },
  { id: 'rose', label: 'Rosa', brand: '#ec4899', brandDeep: '#db2777' },
  { id: 'cyan', label: 'Ciano', brand: '#06b6d4', brandDeep: '#0891b2' },
]

const DEFAULT_THEME: StoredTheme = { name: 'violet', mode: 'dark' }

function isThemeName(value: unknown): value is ThemeName {
  return typeof value === 'string' && THEMES.some((t) => t.id === value)
}

export function readStoredTheme(): StoredTheme {
  try {
    const raw = localStorage.getItem(THEME_STORAGE_KEY)
    if (!raw) return DEFAULT_THEME
    const parsed: unknown = JSON.parse(raw)
    if (typeof parsed !== 'object' || parsed === null) return DEFAULT_THEME
    const name = isThemeName((parsed as { name?: unknown }).name)
      ? (parsed as { name: ThemeName }).name
      : DEFAULT_THEME.name
    const mode: Mode = (parsed as { mode?: unknown }).mode === 'light' ? 'light' : 'dark'
    return { name, mode }
  } catch {
    return DEFAULT_THEME
  }
}

export function applyTheme(theme: StoredTheme): void {
  document.documentElement.dataset.theme = theme.name
  document.documentElement.dataset.mode = theme.mode
  try {
    localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(theme))
  } catch {
    // storage indisponível
  }
}