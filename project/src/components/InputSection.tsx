import { Sparkles, Trash2 } from 'lucide-react';

type InputSectionProps = {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  onClear: () => void;
  isAnalyzing: boolean;
  disabled: boolean;
};

export function InputSection({
  value,
  onChange,
  onAnalyze,
  onClear,
  isAnalyzing,
  disabled,
}: InputSectionProps) {
  const canAnalyze = value.trim().length > 0 && !disabled;

  return (
    <div className="glass-card p-8 mb-8">
      <div className="flex items-center justify-between mb-4">
        <label className="text-sm text-gray-400 font-medium">
          Paste email, SMS, or suspicious message
        </label>
        <span className="text-xs text-gray-600 font-mono">
          {value.length} chars
        </span>
      </div>

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g. URGENT: Your account has been compromised. Click here to verify your identity immediately..."
        className="w-full h-48 bg-gray-900/60 border border-gray-700/50 rounded-xl p-5 text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500/60 focus:ring-2 focus:ring-blue-500/20 transition-all duration-300 resize-none text-sm leading-relaxed font-mono"
        autoFocus
        disabled={disabled}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && e.ctrlKey && canAnalyze) {
            onAnalyze();
          }
        }}
      />

      <div className="flex gap-3 mt-4">
        <button
          onClick={onAnalyze}
          disabled={!canAnalyze}
          className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold py-4 px-8 rounded-xl transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed relative overflow-hidden group shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40"
        >
          <div className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left"></div>
          <div className="relative flex items-center justify-center gap-2">
            <Sparkles className={`w-5 h-5 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>{isAnalyzing ? 'Analyzing with AI...' : 'Analyze Message'}</span>
          </div>
        </button>

        {value && (
          <button
            onClick={onClear}
            disabled={disabled}
            className="px-4 py-4 rounded-xl border border-gray-700/50 text-gray-400 hover:text-white hover:border-gray-600 transition-all duration-300 disabled:opacity-40"
            title="Clear"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        )}
      </div>

      <p className="text-xs text-gray-600 mt-3 text-center">
        Press <kbd className="px-1.5 py-0.5 bg-gray-800 rounded text-gray-400 text-xs">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 bg-gray-800 rounded text-gray-400 text-xs">Enter</kbd> to analyze
      </p>
    </div>
  );
}
