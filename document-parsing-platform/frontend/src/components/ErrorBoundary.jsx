import React from 'react';
import PropTypes from 'prop-types';

export default class ErrorBoundary extends React.Component {
    static propTypes = {
        children: PropTypes.node.isRequired,
        onErrorReset: PropTypes.func
    };

    static defaultProps = {
        onErrorReset: () => window.location.reload()
    };
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
            return (
                <div className="p-6 max-w-md mx-auto bg-red-50 border-l-4 border-red-500 rounded shadow">
                    <div className="flex items-start">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-lg font-medium text-red-800">Something went wrong</h3>
                            {process.env.NODE_ENV === 'development' && (
                                <div className="mt-2 text-sm text-red-700">
                                    <details>
                                        <summary>Error details</summary>
                                        <pre className="mt-2 overflow-auto text-xs">{this.state.error?.stack}</pre>
                                    </details>
                                </div>
                            )}
                            <div className="mt-4 flex space-x-3">
                                <button
                                    type="button"
                                    onClick={() => {
                                        this.setState({ hasError: false });
                                        this.props.onErrorReset();
                                    }}
                                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    Reload Page
                                </button>
                                <button
                                    type="button"
                                    onClick={() => this.setState({ hasError: false })}
                                    className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    Dismiss
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            );
    }

    return this.props.children;
  }
}