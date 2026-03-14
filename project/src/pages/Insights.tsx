/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, ArrowLeft, BarChart3, Database, Upload, Activity, Target, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { getMetrics, getDatasetInfo, uploadDataset } from '../services/api';

export const Insights = () => {
    const [metrics, setMetrics] = useState<any>(null);
    const [datasetInfo, setDatasetInfo] = useState<any>(null);
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            navigate('/signin');
        }
        fetchData();
    }, [navigate]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [metricsData, datasetData] = await Promise.all([
                getMetrics(),
                getDatasetInfo()
            ]);
            setMetrics(metricsData);
            setDatasetInfo(datasetData);
            setError(null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch insights data');
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        navigate('/signin');
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        try {
            await uploadDataset(file);
            setFile(null);
            await fetchData(); // Refresh data
        } catch (err: any) {
            setError(err.message || 'Failed to upload dataset');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
            {/* Background effects */}
            <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none"></div>

            {/* Navbar */}
            <nav className="glass-nav sticky top-0 z-50 backdrop-blur-xl border-b border-gray-800/50">
                <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors border border-white/10 text-sm"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            <span>Dashboard</span>
                        </button>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 bg-indigo-400 rounded-full animate-pulse shadow-lg shadow-indigo-500/50"></div>
                        <h2 className="text-xl font-bold text-white tracking-tight">
                            System<span className="text-indigo-400">Insights</span>
                        </h2>
                    </div>
                    <div className="flex items-center gap-4">
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
            <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">
                {error && (
                    <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-xl mb-8">
                        {error}
                    </div>
                )}

                {loading ? (
                    <div className="flex justify-center py-20">
                        <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                        {/* Metrics Column */}
                        <div className="space-y-6">
                            <div className="flex items-center gap-3 mb-6">
                                <Activity className="w-6 h-6 text-indigo-400" />
                                <h3 className="text-2xl font-bold text-white">Model Evaluation</h3>
                            </div>

                            {metrics ? (
                                <>
                                    <div className="glass-card p-6 border-indigo-500/20">
                                        <h4 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-6">Active Model</h4>
                                        <div className="text-xl font-bold text-white mb-2">{metrics.model_name || "Unknown Model"}</div>
                                        <div className="w-full bg-gray-800 rounded-full h-2 mb-8">
                                            <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${(metrics.accuracy || 0) * 100}%` }}></div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <MetricCard title="Accuracy" value={metrics.accuracy} icon={<Target />} color="text-indigo-400" />
                                            <MetricCard title="Precision" value={metrics.precision} icon={<CheckCircle2 />} color="text-emerald-400" />
                                            <MetricCard title="Recall" value={metrics.recall} icon={<ShieldAlert />} color="text-amber-400" />
                                            <MetricCard title="F1-Score" value={metrics.f1} icon={<BarChart3 />} color="text-blue-400" />
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="glass-card p-6 text-center text-gray-500">
                                    No metrics available. Please train the model first.
                                </div>
                            )}
                        </div>

                        {/* Dataset Column */}
                        <div className="space-y-6">
                            <div className="flex items-center gap-3 mb-6">
                                <Database className="w-6 h-6 text-emerald-400" />
                                <h3 className="text-2xl font-bold text-white">Dataset Management</h3>
                            </div>

                            <div className="glass-card p-6 border-emerald-500/20">
                                <h4 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-6">Current Dataset</h4>

                                {datasetInfo?.exists ? (
                                    <div className="space-y-4 mb-8">
                                        <div className="flex justify-between items-center bg-gray-800/50 p-3 rounded-lg border border-gray-700/50">
                                            <span className="text-gray-400">Total Samples</span>
                                            <span className="text-white font-mono font-bold">{datasetInfo.total_rows.toLocaleString()}</span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">
                                                <div className="text-emerald-400 text-sm">Legitimate</div>
                                                <div className="text-white font-mono font-bold">{datasetInfo.legitimate_count.toLocaleString()}</div>
                                            </div>
                                            <div className="bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                                                <div className="text-red-400 text-sm">Phishing</div>
                                                <div className="text-white font-mono font-bold">{datasetInfo.phishing_count.toLocaleString()}</div>
                                            </div>
                                        </div>
                                        <div className="flex justify-between items-center bg-gray-800/50 p-3 rounded-lg border border-gray-700/50">
                                            <span className="text-gray-400">File Size</span>
                                            <span className="text-white font-mono">{datasetInfo.size_mb} MB</span>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="bg-amber-500/10 border border-amber-500/30 text-amber-400 p-4 rounded-xl mb-8">
                                        No dataset found. Please upload a dataset to train the model.
                                    </div>
                                )}

                                <div className="border-t border-gray-700/50 pt-6">
                                    <h4 className="text-gray-400 text-sm font-semibold uppercase tracking-wider mb-4">Upload New Dataset</h4>
                                    <div className="flex flex-col gap-4">
                                        <label className="flex items-center justify-center w-full h-32 px-4 transition bg-gray-800/40 border-2 border-dashed rounded-xl appearance-none cursor-pointer hover:border-gray-500 hover:bg-gray-800/60 border-gray-600">
                                            <div className="flex flex-col items-center gap-2">
                                                <Upload className="w-8 h-8 text-gray-400" />
                                                <span className="font-medium text-gray-400">
                                                    {file ? file.name : "Drop CSV file or click to browse"}
                                                </span>
                                            </div>
                                            <input type="file" name="file_upload" className="hidden" accept=".csv" onChange={handleFileChange} />
                                        </label>
                                        <button
                                            onClick={handleUpload}
                                            disabled={!file || uploading}
                                            className={`w-full py-3 rounded-lg font-bold transition-all ${file && !uploading
                                                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                                                    : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                                                }`}
                                        >
                                            {uploading ? 'Uploading...' : 'Upload & Replace Dataset'}
                                        </button>
                                        <p className="text-xs text-gray-500 text-center">
                                            Uploading a new dataset will replace the existing one. You will need to retrain the model.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                )}
            </div>
        </div>
    );
};

const MetricCard = ({ title, value, icon, color }: any) => {
    // Determine the exact percentage string
    const percentage = value != null ? (value * 100).toFixed(1) : '0.0';
    return (
        <div className="bg-gray-800/40 p-4 rounded-xl border border-gray-700/50 flex flex-col items-center justify-center text-center gap-2">
            <div className={`${color}`}>{icon}</div>
            <div className="text-2xl font-bold text-white tracking-tight">{percentage}%</div>
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-widest">{title}</div>
        </div>
    );
};
