/* eslint-disable @typescript-eslint/no-explicit-any */
import { AnalysisResult } from '../types';

const API_BASE_URL = 'http://localhost:5000';

/**
 * Sends message text to the Flask backend for phishing analysis.
 * Returns prediction, confidence score, and key indicator words.
 */
export async function analyzeMessage(text: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
            errorData?.message || `Server error: ${response.status}`
        );
    }

    const data = await response.json();
    return data as AnalysisResult;
}

/**
 * Health check for the backend API.
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

/**
 * Fetches evaluation metrics.
 */
export async function getMetrics(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return response.json();
}

/**
 * Fetches dataset info.
 */
export async function getDatasetInfo(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/dataset`);
    if (!response.ok) throw new Error('Failed to fetch dataset info');
    return response.json();
}

/**
 * Uploads a new dataset file.
 */
export async function uploadDataset(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/api/dataset/upload`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || 'Failed to upload dataset');
    }
    return response.json();
}
