import { ShieldAlert, Cpu } from 'lucide-react';

export function Header() {
  return (
    <div className="text-center mb-12">
      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          <div className="absolute inset-0 bg-indigo-500 blur-2xl opacity-40 animate-pulse rounded-full scale-150"></div>
          <div className="relative p-4 glass-card rounded-2xl border-indigo-500/30">
            <ShieldAlert className="w-12 h-12 text-indigo-400" strokeWidth={1.5} />
          </div>
        </div>
      </div>

      <h1 className="text-5xl font-bold mb-4 tracking-tight">
        <span className="bg-gradient-to-r from-indigo-400 via-cyan-300 to-indigo-500 bg-clip-text text-transparent">
          Cybersecurity Threat Detection
        </span>
      </h1>

      <p className="text-gray-400 text-lg mb-6 max-w-lg mx-auto">
        Multi-class <span className="text-indigo-400 font-medium">NLP-powered</span> security analysis
        to detect phishing, spam, and malicious threats instantly
      </p>

      <div className="flex items-center justify-center gap-6 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5 text-indigo-500" />
          <span>ML Engine</span>
        </div>
        <div className="w-1 h-1 bg-gray-700 rounded-full"></div>
        <span>TF-IDF + SVM</span>
        <div className="w-1 h-1 bg-gray-700 rounded-full"></div>
        <span>3-Class Detection</span>
      </div>
    </div>
  );
}
