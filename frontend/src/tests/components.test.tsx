import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import Skeleton from '../components/Skeleton'

describe('Skeleton', () => {
  it('renders with default props', () => {
    const { container } = render(<Skeleton />)
    const el = container.querySelector('.skeleton')
    expect(el).toBeInTheDocument()
    expect(el).toHaveStyle({ width: '100%', height: '16px', margin: '0px' })
  })

  it('renders with custom dimensions', () => {
    const { container } = render(<Skeleton width="50px" height="2rem" margin="8px" />)
    const el = container.querySelector('.skeleton')
    expect(el).toHaveStyle({ width: '50px', height: '32px', margin: '8px' })
  })
})
