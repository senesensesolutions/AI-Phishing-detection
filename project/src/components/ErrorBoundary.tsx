import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    errorMessage: string;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, errorMessage: '' };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, errorMessage: error.message };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    }

    handleReload = () => {
        window.location.href = '/';
    };

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    minHeight: '100vh',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(135deg, #0a0a1a 0%, #111827 50%, #0a0a1a 100%)',
                    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
                    padding: '24px',
                }}>
                    <div style={{
                        maxWidth: '420px',
                        width: '100%',
                        textAlign: 'center',
                        background: 'rgba(17, 24, 39, 0.6)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid rgba(75, 85, 99, 0.3)',
                        borderRadius: '16px',
                        padding: '40px 32px',
                        boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
                    }}>
                        {/* Warning icon */}
                        <div style={{
                            width: '56px',
                            height: '56px',
                            margin: '0 auto 20px',
                            borderRadius: '12px',
                            background: 'rgba(239, 68, 68, 0.15)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '24px',
                        }}>
                            ⚠️
                        </div>

                        <h1 style={{
                            color: '#f87171',
                            fontSize: '20px',
                            fontWeight: 600,
                            marginBottom: '8px',
                        }}>
                            Something went wrong
                        </h1>

                        <p style={{
                            color: '#9ca3af',
                            fontSize: '14px',
                            lineHeight: '1.5',
                            marginBottom: '24px',
                        }}>
                            An unexpected error occurred. Please reload the page and try again.
                        </p>

                        {this.state.errorMessage && (
                            <div style={{
                                background: 'rgba(239, 68, 68, 0.08)',
                                border: '1px solid rgba(239, 68, 68, 0.2)',
                                borderRadius: '8px',
                                padding: '10px 14px',
                                marginBottom: '24px',
                                fontSize: '12px',
                                color: '#fca5a5',
                                fontFamily: 'monospace',
                                wordBreak: 'break-word',
                                textAlign: 'left',
                            }}>
                                {this.state.errorMessage}
                            </div>
                        )}

                        <button
                            onClick={this.handleReload}
                            style={{
                                width: '100%',
                                padding: '12px 24px',
                                borderRadius: '10px',
                                border: 'none',
                                background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                                color: '#fff',
                                fontSize: '14px',
                                fontWeight: 600,
                                cursor: 'pointer',
                                transition: 'opacity 0.2s',
                            }}
                            onMouseOver={(e) => (e.currentTarget.style.opacity = '0.9')}
                            onMouseOut={(e) => (e.currentTarget.style.opacity = '1')}
                        >
                            Reload Application
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
