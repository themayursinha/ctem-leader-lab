import { Component, type ReactNode } from 'react'
import { ShieldAlert } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch() {}

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <ShieldAlert size={32} />
          <h2>Something went wrong</h2>
          <p>An unexpected error occurred. Try refreshing the page.</p>
          <button className="tool-button" onClick={() => window.location.reload()}>
            Reload page
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
