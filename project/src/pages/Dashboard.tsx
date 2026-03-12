import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { InputSection } from '../components/InputSection';
import { ResultsDisplay } from '../components/ResultsDisplay';
import { analyzeMessage } from '../services/api';
import { AnalysisResult } from '../types';
import { LogOut } from 'lucide-react';

export const Dashboard = () => {
    const [messageText, setMessageText] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    // Authentication check
    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            navigate('/signin');
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        navigate('/signin');
    };

    const handleAnalyze = async () => {
        const trimmed = messageText.trim();
        if (!trimmed) return;

        setIsAnalyzing(true);
        setResult(null);
        setError(null);

        try {
            const analysisResult = await analyzeMessage(trimmed);
            setResult(analysisResult);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : 'Failed to connect to the analysis server. Please ensure the backend is running.'
            );
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleClear = () => {
        setMessageText('');
        setResult(null);
        setError(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
            {/* Background effects */}
            <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none"></div>
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="orb orb-1"></div>
                <div className="orb orb-2"></div>
                <div className="orb orb-3"></div>
            </div>

            {/* Navbar */}
            <nav className="glass-nav sticky top-0 z-50 backdrop-blur-xl border-b border-gray-800/50">
                <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-500/50"></div>
                        <h2 className="text-xl font-bold text-white tracking-tight">
                            Threat<span className="text-indigo-400">AI</span> Detector
                        </h2>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-xs text-gray-500 font-mono hidden sm:inline-block">NLP Engine v2.0</span>
                        <button
                            onClick={() => navigate('/insights')}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 hover:text-indigo-200 transition-colors border border-indigo-500/20 text-sm"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                            <span>Insights</span>
                        </button>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors border border-white/10 text-sm"
                        >
                            <LogOut className="w-4 h-4" />
                            <span>Sign Out</span>
                        </button>
                    </div>
                </div>
            </nav>

            {/* Main content */}
            <div className="relative z-10 max-w-4xl mx-auto px-6 py-12">
                <Header />
                <InputSection
                    value={messageText}
                    onChange={setMessageText}
                    onAnalyze={handleAnalyze}
                    onClear={handleClear}
                    isAnalyzing={isAnalyzing}
                    disabled={isAnalyzing}
                />

                {/* Error state */}
                {error && (
                    <div className="glass-card p-6 mb-8 border-red-500/30 animate-fadeIn">
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center flex-shrink-0">
                                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
                                </svg>
                            </div>
                            <div>
                                <h4 className="text-red-400 font-semibold mb-1">Analysis Failed</h4>
                                <p className="text-gray-400 text-sm">{error}</p>
                                <p className="text-gray-500 text-xs mt-2">
                                    Make sure the Flask backend is running on <code className="text-blue-400">http://localhost:5000</code>
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Results */}
                {result && <ResultsDisplay result={result} />}
            </div>

            {/* Footer */}
            <footer className="relative z-10 text-center py-8 text-gray-600 text-xs border-t border-gray-800/30">
                AI Phishing Detection &middot; Powered by NLP &amp; Machine Learning
            </footer>
        </div>
    );
};
