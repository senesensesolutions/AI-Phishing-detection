import { Shield, AlertTriangle, CheckCircle, Activity, Tag, Link2, Clock, AlertOctagon } from 'lucide-react';
import { AnalysisResult } from '../types';

type ResultsDisplayProps = {
  result: AnalysisResult;
};

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const isPhishing = result.prediction === 'phishing';
  const isSpam = result.prediction === 'spam';
  const isSafe = result.prediction === 'legitimate';

  const confidencePercent = Math.round(result.confidence * 100);

  // Determine styling based on prediction
  let statusCardClass = '';
  let statusBadgeClass = '';
  let statusIcon = null;
  let statusTitle = '';
  let statusBadgeText = '';
  let barGradientClass = '';

  if (isPhishing) {
    statusCardClass = 'bg-red-500/15 border-red-500/30 shadow-red-500/10';
    statusBadgeClass = 'bg-red-500/15 text-red-400 border-red-500/30';
    statusIcon = <AlertOctagon className="w-8 h-8 text-red-400" />;
    statusTitle = 'Phishing Detected';
    statusBadgeText = '⚠ CRITICAL THREAT';
    barGradientClass = 'bg-gradient-to-r from-red-600 via-red-500 to-orange-400';
  } else if (isSpam) {
    statusCardClass = 'bg-amber-500/15 border-amber-500/30 shadow-amber-500/10';
    statusBadgeClass = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    statusIcon = <AlertTriangle className="w-8 h-8 text-amber-400" />;
    statusTitle = 'Spam Detected';
    statusBadgeText = '⚠ SUSPICIOUS';
    barGradientClass = 'bg-gradient-to-r from-amber-600 via-yellow-500 to-amber-400';
  } else {
    statusCardClass = 'bg-emerald-500/15 border-emerald-500/30 shadow-emerald-500/10';
    statusBadgeClass = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    statusIcon = <CheckCircle className="w-8 h-8 text-emerald-400" />;
    statusTitle = 'Message Appears Safe';
    statusBadgeText = '✓ VERIFIED SAFE';
    barGradientClass = 'bg-gradient-to-r from-emerald-600 via-emerald-500 to-cyan-400';
  }

  return (
    <div className="glass-card p-8 animate-fadeIn">
      {/* Status header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className={`p-3.5 rounded-xl border shadow-lg ${statusCardClass}`}>
            {statusIcon}
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">
              {statusTitle}
            </h3>
            <p className="text-gray-500 text-sm mt-0.5">
              AI analysis complete &middot; NLP confidence score
            </p>
          </div>
        </div>
        <div
          className={`px-5 py-2.5 rounded-full font-bold text-sm tracking-wide border ${statusBadgeClass}`}
        >
          {statusBadgeText}
        </div>
      </div>

      {/* Confidence score */}
      <div className="mb-8 p-5 bg-gray-800/30 rounded-xl border border-gray-700/30">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-gray-300 font-medium text-sm">ML Confidence Score</span>
          </div>
          <span
            className={`font-bold text-2xl ${isPhishing ? 'text-red-400' : isSpam ? 'text-amber-400' : 'text-emerald-400'
              }`}
          >
            {confidencePercent}%
          </span>
        </div>
        <div className="h-3 bg-gray-900 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ease-out ${barGradientClass}`}
            style={{ width: `${confidencePercent}%` }}
          ></div>
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-600">
          <span>0%</span>
          <span>Confidence Level</span>
          <span>100%</span>
        </div>
      </div>

      {/* Security Flags */}
      {result.security_flags && (result.security_flags.has_urls || result.security_flags.has_urgency) && (
        <div className="mb-8 p-5 bg-gray-800/40 rounded-xl border border-gray-700/50">
          <h4 className="text-gray-300 font-semibold text-sm uppercase tracking-wider mb-4">
            Security Flags
          </h4>
          <div className="flex flex-col gap-3">
            {result.security_flags.has_urls && (
              <div className="flex items-center gap-3 text-sm text-gray-300">
                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                  <Link2 className="w-4 h-4" />
                </div>
                <span><strong className="text-blue-300">Suspicious URLs:</strong> The message contains embedded links that may redirect to malicious sites.</span>
              </div>
            )}
            {result.security_flags.has_urgency && (
              <div className="flex items-center gap-3 text-sm text-gray-300">
                <div className="p-2 bg-orange-500/20 rounded-lg text-orange-400">
                  <Clock className="w-4 h-4" />
                </div>
                <span><strong className="text-orange-300">Urgency Tactics:</strong> The message attempts to create a false sense of urgency or panic.</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Analysis summary */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-4 h-4 text-blue-400" />
          <h4 className="text-gray-300 font-semibold text-sm uppercase tracking-wider">
            AI Insights
          </h4>
        </div>
        <div className="space-y-2">
          {isPhishing && (
            <>
              <AnalysisRow color="red" text={`Critical phishing threat detected (${confidencePercent}% confidence)`} />
              <AnalysisRow color="yellow" text="Do not click any links or provide personal information" />
              <AnalysisRow color="blue" text="Verify sender by contacting the organization through official channels" />
            </>
          )}
          {isSpam && (
            <>
              <AnalysisRow color="yellow" text={`Spam or junk message identified (${confidencePercent}% confidence)`} />
              <AnalysisRow color="gray" text="This message likely contains unsolicited offers or marketing." />
              <AnalysisRow color="blue" text="Avoid replying or interacting with the sender to prevent further spam." />
            </>
          )}
          {isSafe && (
            <>
              <AnalysisRow color="green" text={`Message appears legitimate (${confidencePercent}% confidence)`} />
              <AnalysisRow color="blue" text="No known threat signatures detected by the ML model" />
              <AnalysisRow color="gray" text="Always verify sender identity before sharing sensitive information" />
            </>
          )}
        </div>
      </div>

      {/* Key indicators from ML model */}
      {result.indicators && result.indicators.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Tag className="w-4 h-4 text-cyan-400" />
            <h4 className="text-gray-300 font-semibold text-sm uppercase tracking-wider">
              Key Indicator Words
            </h4>
            <span className="text-xs text-gray-600 ml-auto">
              TF-IDF extracted features
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.indicators.map((word, index) => (
              <span
                key={index}
                className={`px-3 py-1.5 rounded-lg text-sm font-mono border ${isPhishing
                    ? 'bg-red-500/10 text-red-300 border-red-500/20'
                    : isSpam
                      ? 'bg-amber-500/10 text-amber-300 border-amber-500/20'
                      : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                  }`}
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AnalysisRow({ color, text }: { color: string; text: string }) {
  const dotColors: Record<string, string> = {
    red: 'bg-red-400',
    yellow: 'bg-amber-400',
    green: 'bg-emerald-400',
    blue: 'bg-blue-400',
    gray: 'bg-gray-500',
  };

  return (
    <div className="flex items-start gap-3 text-gray-400 text-sm bg-gray-800/40 p-3.5 rounded-lg border border-gray-700/20">
      <div
        className={`w-1.5 h-1.5 ${dotColors[color] || 'bg-blue-400'
          } rounded-full mt-1.5 flex-shrink-0`}
      ></div>
      <span>{text}</span>
    </div>
  );
}
