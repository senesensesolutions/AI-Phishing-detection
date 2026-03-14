/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Mail, Lock } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:5000';

export const SignIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate();

    const handleSignIn = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!email || !password) {
            setError('Please fill in all fields');
            return;
        }

        setIsLoading(true);
        try {
            let res: Response;
            try {
                res = await fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });
            } catch {
                setError('Cannot connect to the server. Please make sure the backend is running on http://localhost:5000');
                setIsLoading(false);
                return;
            }

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || 'Invalid email or password');
            }

            // Store session token
            localStorage.setItem('auth_token', data.token);

            // Redirect to dashboard
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.message || 'Invalid email or password');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
            {/* Background effects */}
            <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none"></div>

            <div className="w-full max-w-md relative z-10">
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-500/50"></div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">
                            Threat<span className="text-indigo-400">AI</span> Detector
                        </h2>
                    </div>
                    <p className="text-gray-400">Sign in to access your dashboard</p>
                </div>

                <Card title="Welcome Back">
                    <form onSubmit={handleSignIn} className="space-y-4">
                        <Input
                            label="Email Address"
                            type="email"
                            placeholder="you@example.com"
                            icon={Mail}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />

                        <Input
                            label="Password"
                            type="password"
                            placeholder="••••••••"
                            icon={Lock}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />

                        {error && (
                            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm text-center">
                                {error}
                            </div>
                        )}

                        <Button type="submit" isLoading={isLoading} className="mt-6">
                            Sign In
                        </Button>

                        <p className="text-center text-gray-400 text-sm mt-6">
                            Don't have an account?{' '}
                            <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 transition-colors">
                                Sign up
                            </Link>
                        </p>
                    </form>
                </Card>
            </div>
        </div>
    );
};
