import type { ReactNode, SVGProps } from 'react'

export type IconProps = SVGProps<SVGSVGElement> & { size?: number }

function S({ size = 18, children, ...rest }: IconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      {children}
    </svg>
  )
}

export const IconBook = (p: IconProps) => (
  <S {...p}>
    <path d="M12 6.5C10.7 5.2 8.8 4.5 6.5 4.5c-1.5 0-2.6.3-3.5.7V18c.9-.4 2-.7 3.5-.7 2.3 0 4.2.7 5.5 2 1.3-1.3 3.2-2 5.5-2 1.5 0 2.6.3 3.5.7V5.2c-.9-.4-2-.7-3.5-.7-2.3 0-4.2.7-5.5 2" />
    <path d="M12 6.5V20" />
  </S>
)

export const IconGrid = (p: IconProps) => (
  <S {...p}>
    <rect x="3" y="3" width="7" height="7" rx="1.5" />
    <rect x="14" y="3" width="7" height="7" rx="1.5" />
    <rect x="14" y="14" width="7" height="7" rx="1.5" />
    <rect x="3" y="14" width="7" height="7" rx="1.5" />
  </S>
)

export const IconFolder = (p: IconProps) => (
  <S {...p}>
    <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z" />
  </S>
)

export const IconCalendar = (p: IconProps) => (
  <S {...p}>
    <rect x="3" y="4" width="18" height="18" rx="2" />
    <path d="M16 2v4M8 2v4M3 10h18" />
  </S>
)

export const IconLayers = (p: IconProps) => (
  <S {...p}>
    <path d="M12 2l9.59 4.36a1 1 0 0 1 0 1.82L12 12.55l-9.59-4.37a1 1 0 0 1 0-1.82L12 2z" />
    <path d="m22 12.17-10 4.55-10-4.55" />
    <path d="m22 17.5-10 4.55-10-4.55" />
  </S>
)

export const IconBot = (p: IconProps) => (
  <S {...p}>
    <path d="M12 8V4" />
    <path d="M9 3.5 12 6l3-2.5" />
    <rect x="4" y="8" width="16" height="12" rx="2.5" />
    <path d="M2 14v2M22 14v2M8 13.5v2M12 13.5v2M16 13.5v2" />
  </S>
)

export const IconNotebook = (p: IconProps) => (
  <S {...p}>
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <path d="M14 2v4a2 2 0 0 0 2 2h4" />
    <path d="M8 13h8M8 17h8M8 9h2" />
  </S>
)

export const IconSearch = (p: IconProps) => (
  <S {...p}>
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.3-4.3" />
  </S>
)

export const IconUpload = (p: IconProps) => (
  <S {...p}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <path d="m17 8-5-5-5 5" />
    <path d="M12 3v12" />
  </S>
)

export const IconUsers = (p: IconProps) => (
  <S {...p}>
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </S>
)

export const IconPlus = (p: IconProps) => (
  <S {...p}>
    <path d="M12 5v14M5 12h14" />
  </S>
)

export const IconLogout = (p: IconProps) => (
  <S {...p}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <path d="m16 17 5-5-5-5" />
    <path d="M21 12H9" />
  </S>
)

export const IconSend = (p: IconProps) => (
  <S {...p}>
    <path d="m22 2-7 20-4-9-9-4Z" />
    <path d="M22 2 11 13" />
  </S>
)

export const IconEye = (p: IconProps) => (
  <S {...p}>
    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
    <circle cx="12" cy="12" r="3" />
  </S>
)

export const IconEyeOff = (p: IconProps) => (
  <S {...p}>
    <path d="m3 3 18 18" />
    <path d="M10.6 5.1A10.9 10.9 0 0 1 12 5c6.5 0 10 7 10 7a17.4 17.4 0 0 1-2.7 3.9" />
    <path d="M6.6 6.6A17.2 17.2 0 0 0 2 12s3.5 7 10 7a10 10 0 0 0 4.2-.9" />
    <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
  </S>
)

export const IconClock = (p: IconProps) => (
  <S {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </S>
)

export const IconLink = (p: IconProps) => (
  <S {...p}>
    <path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7" />
    <path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7" />
  </S>
)

export const IconTag = (p: IconProps) => (
  <S {...p}>
    <path d="M12.6 2.6a2 2 0 0 0-1.4-.6H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .59 1.41l8.6 8.6a2 2 0 0 0 2.82 0l7.19-7.19a2 2 0 0 0 0-2.82Z" />
    <circle cx="7.5" cy="7.5" r="1.5" />
  </S>
)

export const IconChevronRight = (p: IconProps) => (
  <S {...p}>
    <path d="m9 6 6 6-6 6" />
  </S>
)

export const IconMessage = (p: IconProps) => (
  <S {...p}>
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </S>
)

export const IconFile = (p: IconProps) => (
  <S {...p}>
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <path d="M14 2v4a2 2 0 0 0 2 2h4" />
  </S>
)

export const IconAlert = (p: IconProps) => (
  <S {...p}>
    <path d="m21.7 16.3-7.4-12.8a2.5 2.5 0 0 0-4.4 0L2.5 16.3a2.5 2.5 0 0 0 2.2 3.7h14.8a2.5 2.5 0 0 0 2.2-3.7Z" />
    <path d="M12 9v4" />
    <path d="M12 17h.01" />
  </S>
)

export const IconX = (p: IconProps) => (
  <S {...p}>
    <path d="M18 6 6 18M6 6l12 12" />
  </S>
)

export const IconChart = (p: IconProps) => (
  <S {...p}>
    <path d="M3 3v18h18" />
    <path d="M7 16v-4M12 16V8M17 16v-7" />
  </S>
)

export const IconCheck = (p: IconProps) => (
  <S {...p}>
    <path d="m5 13 4 4L19 7" />
  </S>
)

export const IconExternal = (p: IconProps) => (
  <S {...p}>
    <path d="M15 3h6v6" />
    <path d="M10 14 21 3" />
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
  </S>
)

export const IconDownload = (p: IconProps) => (
  <S {...p}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <path d="m7 10 5 5 5-5" />
    <path d="M12 15V3" />
  </S>
)

export const IconBell = (p: IconProps) => (
  <S {...p}>
    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
    <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
  </S>
)

export const IconRefresh = (p: IconProps) => (
  <S {...p}>
    <path d="M21 12a9 9 0 1 1-2.64-6.36" />
    <path d="M21 3v6h-6" />
  </S>
)

export const IconDots = (p: IconProps) => (
  <S {...p} fill="currentColor" stroke="none">
    <circle cx="12" cy="12" r="1.6" />
    <circle cx="19" cy="12" r="1.6" />
    <circle cx="5" cy="12" r="1.6" />
  </S>
)

export const IconTrash = (p: IconProps) => (
  <S {...p}>
    <path d="M3 6h18" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <path d="M10 11v6M14 11v6" />
  </S>
)

export const IconEdit = (p: IconProps) => (
  <S {...p}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
  </S>
)

export const IconPalette = (p: IconProps) => (
  <S {...p}>
    <path d="M12 2a10 10 0 1 0 0 20c1.4 0 2-.9 2-1.9 0-.6-.3-1.1-.6-1.5-.3-.4-.6-.9-.6-1.5 0-1.2 1-2.1 2.3-2.1h1.9C20.6 15 22 13.5 22 11.6 22 6.3 17.5 2 12 2Z" />
    <circle cx="7.5" cy="10.5" r="1.3" fill="currentColor" stroke="none" />
    <circle cx="12" cy="7.5" r="1.3" fill="currentColor" stroke="none" />
    <circle cx="16.5" cy="10.5" r="1.3" fill="currentColor" stroke="none" />
  </S>
)

export const IconSun = (p: IconProps) => (
  <S {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
  </S>
)

export const IconMoon = (p: IconProps) => (
  <S {...p}>
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
  </S>
)