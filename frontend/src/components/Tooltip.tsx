import type { ReactNode } from 'react'

interface TooltipProps {
  label: string
  children: ReactNode
}

const Tooltip = ({ label, children }: TooltipProps) => (
  <span className="tooltip-wrapper" data-tooltip={label}>
    {children}
  </span>
)

export default Tooltip
