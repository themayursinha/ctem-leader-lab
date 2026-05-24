import { Component } from 'react';
import { ShieldAlert } from 'lucide-react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch() {
    // Error logged silently — component shows fallback UI
  }

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
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
