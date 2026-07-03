/**
 * Smart Video Downloader — Main Application Controller
 * Hash-based router, event binding, and module initialization.
 */

const App = (() => {
    const { $, $$, debounce } = Utils;

    // ── Router ─────────────────────────────────

    const PAGES = ['home', 'history', 'settings', 'about'];

    function navigate(page) {
        if (!PAGES.includes(page)) page = 'home';

        // Update active section
        $$('.page-section').forEach(el => el.classList.remove('active'));
        const target = $(`#page-${page}`);
        if (target) target.classList.add('active');

        // Update active nav link
        $$('.sidebar__link').forEach(el => el.classList.remove('active'));
        const navLink = $(`.sidebar__link[data-page="${page}"]`);
        if (navLink) navLink.classList.add('active');

        // Load page-specific data
        if (page === 'history') loadHistory();
        if (page === 'settings') loadSettings();

        // Close mobile sidebar
        closeMobileSidebar();
    }

    function initRouter() {
        // Listen for hash changes
        window.addEventListener('hashchange', () => {
            const page = location.hash.replace('#', '') || 'home';
            navigate(page);
        });

        // Initial navigation
        const initial = location.hash.replace('#', '') || 'home';
        navigate(initial);
    }

    // ── Mobile Sidebar ─────────────────────────

    function openMobileSidebar() {
        $('.sidebar').classList.add('open');
        $('.sidebar-overlay').classList.add('active');
    }

    function closeMobileSidebar() {
        $('.sidebar').classList.remove('open');
        $('.sidebar-overlay').classList.remove('active');
    }

    // ── Home Page Events ───────────────────────

    function bindHomeEvents() {
        // Paste button
        $('#btn-paste').addEventListener('click', async () => {
            const text = await Utils.readClipboard();
            if (text) {
                $('#url-input').value = text;
                UI.showToast('URL pasted from clipboard', 'info', 2000);
            } else {
                UI.showToast('Clipboard is empty or access denied', 'warning');
            }
        });

        // Analyze button
        $('#btn-analyze').addEventListener('click', () => {
            const url = $('#url-input').value.trim();
            if (!url) {
                UI.showToast('Please enter a video URL', 'warning');
                return;
            }
            DownloadManager.analyze(url);
        });

        // Download button
        $('#btn-download').addEventListener('click', () => {
            DownloadManager.startDownload();
        });

        // Cancel download button
        $('#btn-cancel-download').addEventListener('click', () => {
            DownloadManager.cancelDownload();
        });

        // Clear button
        $('#btn-clear').addEventListener('click', () => {
            DownloadManager.reset();
        });

        // Enter key on URL input
        $('#url-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                $('#btn-analyze').click();
            }
        });
    }

    // ── History Page ───────────────────────────

    async function loadHistory(search = '') {
        try {
            const response = await API.getHistory(search);
            UI.renderHistory(response.data);
        } catch (err) {
            UI.showToast('Failed to load history', 'error');
        }
    }

    function bindHistoryEvents() {
        // Search
        const searchInput = $('#history-search');
        if (searchInput) {
            searchInput.addEventListener('input', debounce((e) => {
                loadHistory(e.target.value);
            }, 400));
        }

        // Clear all history
        $('#btn-clear-history').addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all download history?')) return;
            try {
                await API.clearHistory();
                UI.showToast('History cleared', 'success');
                loadHistory();
            } catch (err) {
                UI.showToast('Failed to clear history', 'error');
            }
        });

        // Delegate click events for individual history items
        $('#history-list').addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-action]');
            if (!btn) return;

            const action = btn.dataset.action;
            const id = parseInt(btn.dataset.id);

            if (action === 'delete') {
                try {
                    await API.deleteHistoryItem(id);
                    UI.showToast('Record deleted', 'info');
                    loadHistory($('#history-search')?.value || '');
                } catch (err) {
                    UI.showToast('Failed to delete record', 'error');
                }
            } else if (action === 'open') {
                try {
                    await API.openFileLocation(id);
                } catch (err) {
                    UI.showToast(err.message || 'File not found', 'warning');
                }
            }
        });
    }

    // ── Settings Page ──────────────────────────

    async function loadSettings() {
        try {
            const response = await API.getSettings();
            UI.renderSettings(response.data);
        } catch (err) {
            UI.showToast('Failed to load settings', 'error');
        }
    }

    function bindSettingsEvents() {
        // Theme toggle
        $('#settings-theme').addEventListener('change', async (e) => {
            const theme = e.target.checked ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', theme);
            try {
                await API.updateSettings({ theme });
            } catch { /* non-critical */ }
        });

        // Auto-open toggle
        $('#settings-auto-open').addEventListener('change', async (e) => {
            try {
                await API.updateSettings({ auto_open_folder: e.target.checked });
                UI.showToast('Setting updated', 'success', 2000);
            } catch (err) {
                UI.showToast('Failed to save setting', 'error');
            }
        });

        // Download folder input
        const folderInput = $('#settings-folder');
        folderInput.addEventListener('change', debounce(async () => {
            const folder = folderInput.value.trim();
            if (!folder) return;
            try {
                await API.updateSettings({ download_folder: folder });
                UI.showToast('Download folder updated', 'success', 2000);
            } catch (err) {
                UI.showToast('Invalid folder path', 'error');
            }
        }, 600));

        // Language selector
        $('#settings-language').addEventListener('change', async (e) => {
            try {
                await API.updateSettings({ language: e.target.value });
                UI.showToast('Language updated', 'success', 2000);
            } catch (err) {
                UI.showToast('Failed to save setting', 'error');
            }
        });
    }

    // ── Sidebar Navigation ─────────────────────

    function bindNavigation() {
        $$('.sidebar__link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                location.hash = page;
            });
        });

        // Mobile hamburger
        const hamburger = $('#hamburger-btn');
        if (hamburger) {
            hamburger.addEventListener('click', openMobileSidebar);
        }

        // Overlay click closes sidebar
        const overlay = $('.sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', closeMobileSidebar);
        }
    }

    // ── Theme initialization ───────────────────

    async function initTheme() {
        try {
            const response = await API.getSettings();
            const theme = response.data.theme || 'dark';
            document.documentElement.setAttribute('data-theme', theme);
        } catch {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    }

    // ── Boot ───────────────────────────────────

    function init() {
        initTheme();
        bindNavigation();
        bindHomeEvents();
        bindHistoryEvents();
        bindSettingsEvents();
        initRouter();

        console.log('%c⚡ Smart Video Downloader v1.0', 'color: #7c6df0; font-size: 16px; font-weight: bold;');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return { navigate, loadHistory, loadSettings };
})();
