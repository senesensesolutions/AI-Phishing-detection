import { AnalysisResult, PhishingIndicator } from '../types';

export class PhishingDetector {
  private urgencyPatterns = [
    /urgent/i, /immediately/i, /act now/i, /expire/i, /suspended/i,
    /verify.*account/i, /confirm.*identity/i, /unusual.*activity/i,
    /limited.*time/i, /within.*hours/i, /last.*chance/i
  ];

  private threatPatterns = [
    /account.*closed/i, /account.*locked/i, /unauthorized.*access/i,
    /security.*alert/i, /suspicious.*activity/i, /compromised/i
  ];

  private moneyPatterns = [
    /claim.*prize/i, /won.*lottery/i, /inheritance/i, /refund/i,
    /transfer.*money/i, /payment.*failed/i, /update.*billing/i,
    /verify.*payment/i, /tax.*refund/i
  ];

  private linkPatterns = [
    /click.*here/i, /click.*link/i, /verify.*here/i, /login.*here/i,
    /update.*here/i, /confirm.*here/i
  ];

  private impersonationPatterns = [
    /amazon/i, /paypal/i, /netflix/i, /apple/i, /microsoft/i,
    /bank/i, /irs/i, /fedex/i, /dhl/i, /support.*team/i
  ];

  private suspiciousUrls = [
    /bit\.ly/i, /tinyurl/i, /goo\.gl/i, /ow\.ly/i,
    /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,
    /-secure-/i, /-login-/i, /-verify-/i, /-account-/i
  ];

  private genericGreetings = [
    /dear customer/i, /dear user/i, /dear member/i, /valued customer/i,
    /hello user/i, /attention/i
  ];

  analyze(text: string): AnalysisResult {
    const cleanedText = this.cleanText(text);
    const indicators = this.detectIndicators(cleanedText);
    const score = this.calculatePhishingScore(indicators);

    const confidence = Math.min(Math.max(score, 0), 100);
    const status: 'safe' | 'phishing' = confidence >= 50 ? 'phishing' : 'safe';
    const insights = this.generateInsights(indicators, confidence, status);

    return {
      status,
      confidence: status === 'phishing' ? confidence : 100 - confidence,
      insights,
      indicators
    };
  }

  private cleanText(text: string): string {
    return text.trim().replace(/\s+/g, ' ');
  }

  private detectIndicators(text: string): PhishingIndicator[] {
    const indicators: PhishingIndicator[] = [];

    const urgencyCount = this.urgencyPatterns.filter(p => p.test(text)).length;
    if (urgencyCount > 0) {
      indicators.push({
        type: 'Urgency Tactics',
        severity: urgencyCount > 2 ? 'high' : urgencyCount > 1 ? 'medium' : 'low',
        description: `Creates false sense of urgency (${urgencyCount} instances)`
      });
    }

    const threatCount = this.threatPatterns.filter(p => p.test(text)).length;
    if (threatCount > 0) {
      indicators.push({
        type: 'Threat Language',
        severity: 'high',
        description: 'Uses threatening language to create panic'
      });
    }

    const moneyCount = this.moneyPatterns.filter(p => p.test(text)).length;
    if (moneyCount > 0) {
      indicators.push({
        type: 'Financial Lure',
        severity: 'high',
        description: 'Contains suspicious financial offers or requests'
      });
    }

    const linkCount = this.linkPatterns.filter(p => p.test(text)).length;
    if (linkCount > 0) {
      indicators.push({
        type: 'Suspicious Links',
        severity: 'medium',
        description: 'Pressures clicking on links'
      });
    }

    const impersonationCount = this.impersonationPatterns.filter(p => p.test(text)).length;
    if (impersonationCount > 0) {
      indicators.push({
        type: 'Brand Impersonation',
        severity: 'high',
        description: 'May be impersonating trusted organizations'
      });
    }

    const urlCount = this.suspiciousUrls.filter(p => p.test(text)).length;
    if (urlCount > 0) {
      indicators.push({
        type: 'Suspicious URLs',
        severity: 'high',
        description: 'Contains shortened or suspicious URLs'
      });
    }

    const genericCount = this.genericGreetings.filter(p => p.test(text)).length;
    if (genericCount > 0) {
      indicators.push({
        type: 'Generic Greeting',
        severity: 'low',
        description: 'Uses impersonal greeting instead of your name'
      });
    }

    const hasSpellingErrors = this.detectSpellingIssues(text);
    if (hasSpellingErrors) {
      indicators.push({
        type: 'Poor Grammar',
        severity: 'medium',
        description: 'Contains unusual formatting or grammar'
      });
    }

    return indicators;
  }

  private detectSpellingIssues(text: string): boolean {
    const suspiciousPatterns = [
      /[A-Z]{3,}[a-z]+[A-Z]/,
      /\s{2,}/,
      /[!?]{2,}/
    ];
    return suspiciousPatterns.some(p => p.test(text));
  }

  private calculatePhishingScore(indicators: PhishingIndicator[]): number {
    let score = 0;

    indicators.forEach(indicator => {
      switch (indicator.severity) {
        case 'high':
          score += 25;
          break;
        case 'medium':
          score += 15;
          break;
        case 'low':
          score += 8;
          break;
      }
    });

    return score;
  }

  private generateInsights(
    indicators: PhishingIndicator[],
    confidence: number,
    status: 'safe' | 'phishing'
  ): string[] {
    const insights: string[] = [];

    if (status === 'phishing') {
      insights.push(`High probability of phishing attempt detected (${confidence.toFixed(1)}% confidence)`);

      const highSeverity = indicators.filter(i => i.severity === 'high');
      if (highSeverity.length > 0) {
        insights.push(`Found ${highSeverity.length} critical warning signs`);
      }

      insights.push('Recommendation: Do not click links or provide personal information');

      if (indicators.some(i => i.type === 'Brand Impersonation')) {
        insights.push('Verify sender by contacting organization directly through official channels');
      }
    } else {
      insights.push(`Message appears safe (${confidence.toFixed(1)}% confidence)`);

      if (indicators.length > 0) {
        insights.push(`Detected ${indicators.length} minor concern(s) - exercise caution`);
      } else {
        insights.push('No common phishing indicators detected');
      }

      insights.push('Always verify sender identity before sharing sensitive information');
    }

    return insights;
  }
}
