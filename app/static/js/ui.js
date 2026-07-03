/**
 * Smart Video Downloader — UI Module
 * Handles DOM rendering, toasts, loading overlays, and UI state updates.
 */

const UI = (() => {
    const { $, $$ } = Utils;

    // ── Toast Notifications ────────────────────

    /**
     * Display a toast notification.
     * @param {string} message
     * @param {'success'|'error'|'info'|'warning'} type
     * @param {number} duration - auto-dismiss in ms (0 = manual)
     */
    function showToast(message, type = 'info', duration = 4000) {
        const container = $('#toast-container');
        const icons = {
            success: 'check_circle',
            error: 'error',
            info: 'info',
            warning: 'warning',
        };

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.innerHTML = `
            <span class="material-symbols-rounded toast__icon">${icons[type]}</span>
            <span class="toast__content">${message}</span>
            <button class="toast__close" aria-label="Close">&times;</button>
        `;

        // Close button
        toast.querySelector('.toast__close').addEventListener('click', () => dismissToast(toast));

        container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => dismissToast(toast), duration);
        }
    }

    function dismissToast(toast) {
        toast.classList.add('exiting');
        toast.addEventListener('animationend', () => toast.remove());
    }

    // ── Loading Spinner ────────────────────────

    function showLoading(text = 'Analyzing video...') {
        const overlay = $('#spinner-overlay');
        const textEl = $('#spinner-text');
        if (textEl) textEl.textContent = text;
        overlay.classList.add('active');
    }

    function hideLoading() {
        const overlay = $('#spinner-overlay');
        overlay.classList.remove('active');
    }

    // ── Video Info Rendering ───────────────────

    /**
     * Render video metadata in the info card.
     * @param {object} data - video metadata from /api/analyze
     */
    function renderVideoInfo(data) {
        const infoCard = $('#video-info');
        const thumbImg = $('#video-thumbnail-img');
        const durationBadge = $('#video-duration-badge');
        const title = $('#video-title');
        const channel = $('#video-channel');
        const views = $('#video-views');
        const uploadDate = $('#video-upload-date');
        const fileSize = $('#video-filesize');

        if (data.thumbnail) {
            thumbImg.src = data.thumbnail;
            thumbImg.alt = data.title;
        }

        durationBadge.textContent = data.duration_formatted || '';
        title.textContent = data.title || 'Untitled';
        channel.textContent = data.channel || 'Unknown';
        views.textContent = data.views_formatted || 'Unknown';
        uploadDate.textContent = data.upload_date_formatted || 'Unknown';
        fileSize.textContent = data.filesize_formatted || 'Unknown';

        infoCard.classList.add('visible');
    }

    /**
     * Render available format chips for quality selection.
     * @param {Array} formats - list of format objects
     * @param {function} onSelect - callback when a format is clicked
     */
    function renderFormats(formats, onSelect) {
        const container = $('#format-grid');
        const section = $('#format-selection');

        container.innerHTML = '';

        formats.forEach((fmt, index) => {
            const chip = document.createElement('button');
            chip.className = 'format-chip';
            chip.dataset.formatId = fmt.format_id;
            chip.dataset.index = index;
            chip.innerHTML = `
                <span class="format-chip__label">${fmt.label}</span>
                <span class="format-chip__size">${fmt.filesize ? Utils.formatBytes(fmt.filesize) : '—'}</span>
            `;

            chip.addEventListener('click', () => {
                // Deselect all
                $$('.format-chip', container).forEach(c => c.classList.remove('selected'));
                chip.classList.add('selected');
                onSelect(fmt);
            });

            container.appendChild(chip);
        });

        section.classList.add('visible');
    }

    // ── Progress Bar ───────────────────────────

    /**
     * Update the download progress UI.
     * @param {object} data - { percent, speed, eta, filesize, status }
     */
    function updateProgress(data) {
        const fill = $('#progress-fill');
        const percentText = $('#progress-percent');
        const speedText = $('#progress-speed');
        const etaText = $('#progress-eta');
        const sizeText = $('#progress-size');

        fill.style.width = `${data.percent || 0}%`;
        percentText.textContent = `${(data.percent || 0).toFixed(1)}%`;
        speedText.textContent = data.speed || '—';
        etaText.textContent = data.eta || '—';
        sizeText.textContent = data.filesize || '—';
    }

    /**
     * Show the download controls section.
     */
    function showDownloadControls() {
        $('#download-controls').classList.add('visible');
    }

    function hideDownloadControls() {
        $('#download-controls').classList.remove('visible');
    }

    /**
     * Reset the progress bar.
     */
    function resetProgress() {
        updateProgress({ percent: 0, speed: '—', eta: '—', filesize: '—' });
    }

    // ── History Rendering ──────────────────────

    /**
     * Render the history list.
     * @param {Array} items - download history records
     */
    function renderHistory(items) {
        const list = $('#history-list');
        list.innerHTML = '';

        if (!items || items.length === 0) {
            list.innerHTML = `
                <div class="history-empty">
                    <span class="material-symbols-rounded">history</span>
                    <p>No downloads yet</p>
                </div>
            `;
            return;
        }

        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'history-item anim-fade-up';
            el.innerHTML = `
                <div class="history-item__thumb">
                    ${item.thumbnail ? `<img src="${item.thumbnail}" alt="${item.title}">` : ''}
                </div>
                <div class="history-item__info">
                    <div class="history-item__title" title="${item.title}">${item.title}</div>
                    <div class="history-item__date">${Utils.formatDate(item.downloaded_at)}</div>
                </div>
                <div class="history-item__actions">
                    <button class="btn btn--ghost btn--icon" title="Open file location" data-action="open" data-id="${item.id}">
                        <span class="material-symbols-rounded">folder_open</span>
                    </button>
                    <button class="btn btn--ghost btn--icon" title="Delete" data-action="delete" data-id="${item.id}">
                        <span class="material-symbols-rounded">delete</span>
                    </button>
                </div>
            `;
            list.appendChild(el);
        });
    }

    // ── Settings Rendering ─────────────────────

    /**
     * Populate the settings form with current values.
     * @param {object} settings
     */
    function renderSettings(settings) {
        const folderInput = $('#settings-folder');
        const themeToggle = $('#settings-theme');
        const autoOpenToggle = $('#settings-auto-open');
        const langSelect = $('#settings-language');

        if (folderInput) folderInput.value = settings.download_folder || '';
        if (themeToggle) themeToggle.checked = settings.theme === 'light';
        if (autoOpenToggle) autoOpenToggle.checked = settings.auto_open_folder === true;
        if (langSelect) langSelect.value = settings.language || 'en';
    }

    // ── Reset Home Page ────────────────────────

    /**
     * Reset the home page to its initial state.
     */
    function resetHome() {
        $('#video-info').classList.remove('visible');
        $('#format-selection').classList.remove('visible');
        hideDownloadControls();
        resetProgress();
        $('#url-input').value = '';
        $('#btn-download').disabled = true;
    }

    return {
        showToast,
        showLoading,
        hideLoading,
        renderVideoInfo,
        renderFormats,
        updateProgress,
        showDownloadControls,
        hideDownloadControls,
        resetProgress,
        renderHistory,
        renderSettings,
        resetHome,
    };
})();
