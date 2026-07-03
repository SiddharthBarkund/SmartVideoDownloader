/**
 * Smart Video Downloader — JS Utilities
 * Shared helper functions used across all modules.
 */

const Utils = (() => {
    /**
     * Format bytes to human-readable string.
     * @param {number} bytes
     * @returns {string}
     */
    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return 'Unknown';
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let i = 0;
        let size = bytes;
        while (size >= 1024 && i < units.length - 1) {
            size /= 1024;
            i++;
        }
        return `${size.toFixed(1)} ${units[i]}`;
    }

    /**
     * Format seconds to MM:SS or HH:MM:SS.
     * @param {number} seconds
     * @returns {string}
     */
    function formatDuration(seconds) {
        if (!seconds || seconds <= 0) return 'Unknown';
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        return `${m}:${String(s).padStart(2, '0')}`;
    }

    /**
     * Format ISO date to readable string.
     * @param {string} isoString
     * @returns {string}
     */
    function formatDate(isoString) {
        if (!isoString) return 'Unknown';
        try {
            const d = new Date(isoString);
            return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        } catch {
            return isoString;
        }
    }

    /**
     * Debounce a function.
     * @param {Function} fn
     * @param {number} delay - milliseconds
     * @returns {Function}
     */
    function debounce(fn, delay = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delay);
        };
    }

    /**
     * Copy text to clipboard.
     * @param {string} text
     * @returns {Promise<boolean>}
     */
    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Read text from clipboard.
     * @returns {Promise<string>}
     */
    async function readClipboard() {
        try {
            return await navigator.clipboard.readText();
        } catch {
            return '';
        }
    }

    /**
     * Safely query a DOM element.
     * @param {string} selector
     * @param {Element} [parent=document]
     * @returns {Element|null}
     */
    function $(selector, parent = document) {
        return parent.querySelector(selector);
    }

    /**
     * Query all matching DOM elements.
     * @param {string} selector
     * @param {Element} [parent=document]
     * @returns {Element[]}
     */
    function $$(selector, parent = document) {
        return Array.from(parent.querySelectorAll(selector));
    }

    return { formatBytes, formatDuration, formatDate, debounce, copyToClipboard, readClipboard, $, $$ };
})();
