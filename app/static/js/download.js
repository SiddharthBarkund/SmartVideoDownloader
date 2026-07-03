/**
 * Smart Video Downloader — Download Manager
 * Handles download state machine, SSE progress, and cancellation.
 */

const DownloadManager = (() => {
    // State: idle | analyzing | ready | downloading | complete | error | cancelled
    let state = 'idle';
    let currentDownloadId = null;
    let currentEventSource = null;
    let selectedFormat = null;
    let videoMetadata = null;

    const { $ } = Utils;

    function getState() { return state; }
    function getSelectedFormat() { return selectedFormat; }
    function getVideoMetadata() { return videoMetadata; }

    /**
     * Set the selected format from the format chips.
     * @param {object} format
     */
    function setSelectedFormat(format) {
        selectedFormat = format;
        const downloadBtn = $('#btn-download');
        if (downloadBtn) downloadBtn.disabled = false;
    }

    /**
     * Analyze a video URL.
     * @param {string} url
     */
    async function analyze(url) {
        if (state === 'analyzing' || state === 'downloading') return;

        state = 'analyzing';
        UI.showLoading('Analyzing video...');

        try {
            const response = await API.analyzeUrl(url);
            videoMetadata = response.data;

            UI.renderVideoInfo(videoMetadata);
            UI.renderFormats(videoMetadata.formats, setSelectedFormat);
            UI.showDownloadControls();

            if (response.warning) {
                UI.showToast(response.warning, 'warning');
            }

            state = 'ready';
            UI.showToast('Video analyzed successfully!', 'success');
        } catch (err) {
            state = 'idle';
            UI.showToast(err.message || 'Analysis failed.', 'error');
        } finally {
            UI.hideLoading();
        }
    }

    /**
     * Start downloading the selected format.
     */
    async function startDownload() {
        if (state !== 'ready' || !selectedFormat || !videoMetadata) return;

        const urlInput = $('#url-input');
        const outputFormat = $('#output-format')?.value || 'mp4';

        // Get download dir from settings
        let downloadDir = null;
        try {
            const settingsResp = await API.getSettings();
            downloadDir = settingsResp.data.download_folder;
        } catch {
            // Use server default
        }

        state = 'downloading';
        UI.resetProgress();

        // Disable buttons during download
        $('#btn-download').disabled = true;
        $('#btn-analyze').disabled = true;
        $('#btn-cancel-download').style.display = 'inline-flex';

        try {
            const response = await API.startDownload({
                url: urlInput.value.trim(),
                format_id: selectedFormat.format_id,
                quality_label: selectedFormat.label,
                output_format: outputFormat,
                download_dir: downloadDir,
            });

            currentDownloadId = response.download_id;

            // Connect to SSE for progress
            currentEventSource = API.streamProgress(
                currentDownloadId,
                handleProgress,
                handleStreamError
            );
        } catch (err) {
            state = 'ready';
            $('#btn-download').disabled = false;
            $('#btn-analyze').disabled = false;
            $('#btn-cancel-download').style.display = 'none';
            UI.showToast(err.message || 'Download failed to start.', 'error');
        }
    }

    /**
     * Handle SSE progress update.
     * @param {object} data
     */
    function handleProgress(data) {
        UI.updateProgress(data);

        if (data.status === 'complete') {
            state = 'complete';
            UI.showToast('Download completed! 🎉', 'success', 6000);
            // Trigger browser download of the file from the server
            if (currentDownloadId) {
                const link = document.createElement('a');
                link.href = `/api/file/${currentDownloadId}`;
                link.download = '';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            resetControls();
        } else if (data.status === 'error') {
            state = 'error';
            UI.showToast(`Download error: ${data.error || 'Unknown'}`, 'error', 8000);
            resetControls();
        } else if (data.status === 'cancelled') {
            state = 'cancelled';
            UI.showToast('Download cancelled.', 'warning');
            resetControls();
        }
    }

    function handleStreamError() {
        if (state === 'downloading') {
            state = 'error';
            UI.showToast('Lost connection to download stream.', 'error');
            resetControls();
        }
    }

    /**
     * Cancel the current download.
     */
    async function cancelDownload() {
        if (!currentDownloadId) return;

        try {
            await API.cancelDownload(currentDownloadId);
        } catch {
            // Even if cancel API fails, close the stream
        }

        if (currentEventSource) {
            currentEventSource.close();
            currentEventSource = null;
        }

        state = 'ready';
        resetControls();
        UI.showToast('Download cancelled.', 'warning');
    }

    /**
     * Reset button states after download ends.
     */
    function resetControls() {
        const analyzeBtn = $('#btn-analyze');
        const downloadBtn = $('#btn-download');
        const cancelBtn = $('#btn-cancel-download');

        if (analyzeBtn) analyzeBtn.disabled = false;
        if (downloadBtn) downloadBtn.disabled = !selectedFormat;
        if (cancelBtn) cancelBtn.style.display = 'none';

        currentDownloadId = null;
        if (currentEventSource) {
            currentEventSource.close();
            currentEventSource = null;
        }
    }

    /**
     * Full reset to idle state.
     */
    function reset() {
        if (currentEventSource) {
            currentEventSource.close();
            currentEventSource = null;
        }
        state = 'idle';
        currentDownloadId = null;
        selectedFormat = null;
        videoMetadata = null;
        resetControls();
        UI.resetHome();
    }

    return {
        getState,
        getSelectedFormat,
        getVideoMetadata,
        setSelectedFormat,
        analyze,
        startDownload,
        cancelDownload,
        reset,
    };
})();
