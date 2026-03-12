// API response type matching Flask backend contract
export type AnalysisResult = {
  prediction: 'phishing' | 'spam' | 'legitimate';
  confidence: number; // 0.0 – 1.0
  indicators: string[]; // key TF-IDF words
  security_flags?: {
    has_urls: boolean;
    has_urgency: boolean;
  };
};

// Frontend-enriched state for UI display
export type AnalysisState = {
  result: AnalysisResult | null;
  isLoading: boolean;
  error: string | null;
};
