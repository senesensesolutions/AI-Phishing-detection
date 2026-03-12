import React, { ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    isLoading?: boolean;
    variant?: 'primary' | 'secondary' | 'accent';
}

export const Button: React.FC<ButtonProps> = ({
    children,
    isLoading,
    variant = 'primary',
    className = '',
    disabled,
    ...props
}) => {
    const baseStyles = 'w-full py-3 px-4 rounded-xl font-semibold flex items-center justify-center transition-all duration-300 transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
        primary: 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)] hover:shadow-[0_0_25px_rgba(59,130,246,0.8)] border border-blue-400/30',
        secondary: 'bg-white/10 hover:bg-white/20 text-white border border-white/10 backdrop-blur-md',
        accent: 'bg-green-600 hover:bg-green-500 text-white shadow-[0_0_15px_rgba(34,197,94,0.5)] hover:shadow-[0_0_25px_rgba(34,197,94,0.8)] border border-green-400/30',
    };

    return (
        <button
            {...props}
            disabled={isLoading || disabled}
            className={`${baseStyles} ${variants[variant]} ${className}`}
        >
            {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
            ) : null}
            {children}
        </button>
    );
};
