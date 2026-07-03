/**
 * Smart Video Downloader — API Client
 * Centralized HTTP communication with the FastAPI backend.
 */

const API = (() => {
    const BASE = '/api';

    /**
     * Generic fetch wrapper with error handling.
     * @param {string} endpoint
     * @param {object} options - fetch options
     * @returns {Promise<object>}
     */
    async function request(endpoint, options = {}) {
        const url = `${BASE}${endpoint}`;
        const config = {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (err) {
            if (err.name === 'TypeError') {
                throw new Error('Network error. Is the server running?');
            }
            throw err;
        }
    }

    // ── Video API ──────────────────────────────

    /**
     * Analyze a video URL for metadata and available formats.
     * @param {string} url
     * @returns {Promise<object>}
     */
    async function analyzeUrl(url) {
        return request('/analyze', {
            method: 'POST',
            body: JSON.stringify({ url }),
        });
    }

    /**
     * Start a download and return a download_id.
     * @param {object} params - { url, format_id, quality_label, output_format, download_dir }
     * @returns {Promise<object>}
     */
    async function startDownload(params) {
        return request('/download', {
            method: 'POST',
            body: JSON.stringify(params),
        });
    }

    /**
     * Cancel an active download.
     * @param {string} downloadId
     * @returns {Promise<object>}
     */
    async function cancelDownload(downloadId) {
        return request(`/cancel/${downloadId}`, { method: 'POST' });
    }

    /**
     * Connect to SSE progress stream.
     * @param {string} downloadId
     * @param {function} onMessage - called with parsed JSON data
     * @param {function} onError - called on error
     * @returns {EventSource}
     */
    function streamProgress(downloadId, onMessage, onError) {
        const eventSource = new EventSource(`${BASE}/progress/${downloadId}`);

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);

                // Close on terminal states
                if (['complete', 'error', 'cancelled'].includes(data.status)) {
                    eventSource.close();
                }
            } catch (err) {
                console.error('SSE parse error:', err);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            if (onError) onError();
        };

        return eventSource;
    }

    // ── History API ────────────────────────────

    async function getHistory(search = '') {
        const query = search ? `?search=${encodeURIComponent(search)}` : '';
        return request(`/history${query}`);
    }

    async function deleteHistoryItem(id) {
        return request(`/history/${id}`, { method: 'DELETE' });
    }

    async function clearHistory() {
        return request('/history', { method: 'DELETE' });
    }

    async function openFileLocation(id) {
        return request(`/history/${id}/open`, { method: 'POST' });
    }

    // ── Settings API ───────────────────────────

    async function getSettings() {
        return request('/settings');
    }

    async function updateSettings(data) {
        return request('/settings', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    return {
        analyzeUrl,
        startDownload,
        cancelDownload,
        streamProgress,
        getHistory,
        deleteHistoryItem,
        clearHistory,
        openFileLocation,
        getSettings,
        updateSettings,
    };
})();
