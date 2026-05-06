import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="component-error">
          {this.props.fallback || 'Não foi possível renderizar este componente.'}
        </div>
      );
    }

    return this.props.children;
  }
}
