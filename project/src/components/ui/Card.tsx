import React from 'react';

interface CardProps {
    children: React.ReactNode;
    title?: string;
    className?: string;
}

export const Card: React.FC<CardProps> = ({ children, title, className = '' }) => {
    return (
        <div className={`backdrop-blur-xl bg-white/10 border border-white/20 p-8 rounded-2xl shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] w-full max-w-md ${className}`}>
            {title && (
                <h2 className="text-3xl font-bold text-white mb-6 text-center tracking-tight">
                    {title}
                </h2>
            )}
            {children}
        </div>
    );
};
