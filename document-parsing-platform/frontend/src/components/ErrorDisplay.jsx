import React from 'react';
import PropTypes from 'prop-types';

export default function ErrorDisplay({ error, onRetry }) {
    ErrorDisplay.propTypes = {
        error: PropTypes.shape({
            message: PropTypes.string
        }),
        onRetry: PropTypes.func
    };

    ErrorDisplay.defaultProps = {
        error: null,
        onRetry: null
    };
  if (!error) return null;

  return (
    <div className="p-4 mb-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm">
      <div className="flex items-start">
        <div className="flex-shrink-0 pt-0.5">
          <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-red-700">
            {error?.message || 'An unexpected error occurred'}
          </p>
          {process.env.NODE_ENV === 'development' && error?.stack && (
            <details className="mt-2">
              <summary className="text-xs text-red-600 cursor-pointer">Show details</summary>
              <pre className="mt-1 p-2 bg-red-100 text-xs text-red-800 overflow-auto rounded">
                {error.stack}
              </pre>
            </details>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <svg className="-ml-0.5 mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}