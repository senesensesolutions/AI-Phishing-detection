import React, { InputHTMLAttributes } from 'react';
import { LucideIcon } from 'lucide-react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label: string;
    icon?: LucideIcon;
    error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ label, icon: Icon, error, className = '', ...props }, ref) => {
        return (
            <div className="mb-4 w-full">
                <label className="block text-sm font-medium text-gray-300 mb-1.5 ml-1">
                    {label}
                </label>
                <div className="relative">
                    {Icon && (
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Icon className="h-5 w-5 text-gray-400" />
                        </div>
                    )}
                    <input
                        {...props}
                        ref={ref}
                        className={`w-full bg-black/40 border border-gray-600/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-300 ${Icon ? 'pl-10' : ''
                            } ${error ? 'border-red-500 focus:ring-red-500/50 text-red-100' : ''} ${className}`}
                    />
                </div>
                {error && <p className="mt-1.5 text-sm text-red-400 ml-1">{error}</p>}
            </div>
        );
    }
);

Input.displayName = 'Input';
