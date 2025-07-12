document.addEventListener('DOMContentLoaded', function () {
    const urlInput = document.getElementById('url-input');
    const downloadBtn = document.getElementById('download-btn');
    const resultsSection = document.getElementById('results-section');
    const processingIndicator = resultsSection.querySelector('.processing-indicator');
    const downloadResultContainer = resultsSection.querySelector('.download-result');
    const statusBar = resultsSection.querySelector('.status-bar .progress');
    
    // Default state
    resultsSection.style.display = 'none';

    downloadBtn.addEventListener('click', handleGetFormats);
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleGetFormats();
        }
    });

    async function handleGetFormats() {
        const url = urlInput.value.trim();
        if (!url) {
            showError("Please paste a valid video URL.");
            return;
        }

        const urlParams = new URLSearchParams(window.location.search);
        const platform = urlParams.get('platform');

        // Show processing state
        resultsSection.style.display = 'block';
        processingIndicator.style.display = 'flex';
        downloadResultContainer.style.display = 'none';
        statusBar.style.width = '25%';
        setButtonState(true, 'Processing...');
        // Clear previous results and errors
        document.getElementById('available-formats').innerHTML = '';
        document.getElementById('media-details').innerHTML = '';

        try {
            const response = await fetch('/api/downloader/get-formats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, platform: platform }),
            });

            const data = await response.json();
            
            if (!response.ok || !data.success) {
                // 'detail' is the key FastAPI uses for HTTPErrors
                throw new Error(data.detail || data.message || "Could not fetch video formats.");
            }

            statusBar.style.width = '75%';
            displayResults(data, url, platform);

        } catch (error) {
            showError(error.message);
        } finally {
            setButtonState(false, 'Download Now');
        }
    }

    function displayResults(data, url, platform) {
        processingIndicator.style.display = 'none';
        downloadResultContainer.style.display = 'block';

        document.getElementById('video-thumbnail').src = data.thumbnail || '/static/images/placeholder.png';
        const mediaDetails = document.getElementById('media-details');
        mediaDetails.innerHTML = `
            <h4 style="color: var(--text); margin: 0 0 5px 0;">${data.title}</h4>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                Duration: ${formatDuration(data.duration)}
            </p>
        `;

        const formatsContainer = document.getElementById('available-formats');
        formatsContainer.innerHTML = ''; // Clear previous formats

        if (data.formats && data.formats.length > 0) {
            data.formats.forEach(format => {
                const formatButton = createFormatButton(format, url, platform);
                formatsContainer.appendChild(formatButton);
            });
        } else {
            formatsContainer.innerHTML = `<p style="color: var(--text-secondary);">No downloadable formats found.</p>`;
        }
        statusBar.style.width = '100%';
    }

    function createFormatButton(format, url, platform) {
        const button = document.createElement('button');
        button.className = 'download-btn'; // Re-use styling
        button.style.fontSize = '0.8rem';
        button.style.padding = '8px 12px';
        button.style.marginBottom = '5px'; // Spacing between buttons
        button.style.marginRight = '5px';

        const fileSize = format.filesize ? formatBytes(format.filesize) : 'N/A';
        const isAudioOnly = format.vcodec === 'none' && format.acodec !== 'none';
        
        let label = '';
        if (isAudioOnly) {
            label = `🎵 Audio (${format.ext}) - ${fileSize}`;
        } else {
            const resolution = format.resolution || format.format_note;
            label = `🎥 ${resolution} (${format.ext}) - ${fileSize}`;
        }
        
        button.innerHTML = label;

        button.addEventListener('click', (e) => {
            const downloadType = isAudioOnly ? 'audio' : 'video';
            // Disable all format buttons during download
            document.querySelectorAll('#available-formats .download-btn').forEach(btn => btn.disabled = true);
            e.currentTarget.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Downloading...`;
            triggerDownload(url, downloadType, format.format_id, platform, e.currentTarget);
        });

        return button;
    }

    async function triggerDownload(url, downloadType, formatId, platform, clickedButton) {
        const originalButtonText = clickedButton.innerHTML;

        try {
            // Step 1: Prepare download to get the filename (already part of the main download flow in backend)
            // Step 2: Fetch the actual file content
            const downloadResponse = await fetch('/api/downloader/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    download_type: downloadType,
                    format_id: formatId,
                    platform: platform,
                }),
            });
    
            if (!downloadResponse.ok) {
                 const errorData = await downloadResponse.json();
                 throw new Error(errorData.detail || 'Download failed. The server returned an error.');
            }
    
            const contentDisposition = downloadResponse.headers.get('content-disposition');
            let filename = "download";
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/);
                if (filenameMatch && filenameMatch.length > 1) {
                    filename = decodeURIComponent(filenameMatch[1]);
                } else {
                     const filenameFallback = contentDisposition.match(/filename="?([^"]+)"?/);
                     if(filenameFallback && filenameFallback.length > 1) {
                        filename = filenameFallback[1];
                     }
                }
            }

            // Step 3: Create a blob and trigger browser download
            const blob = await downloadResponse.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            a.remove();
    
        } catch (error) {
            alert(`Download Error: ${error.message}`);
        } finally {
            // Re-enable all format buttons
            document.querySelectorAll('#available-formats .download-btn').forEach(btn => {
                btn.disabled = false;
            });
            clickedButton.innerHTML = originalButtonText;
        }
    }

    function setButtonState(disabled, text) {
        downloadBtn.disabled = disabled;
        downloadBtn.innerHTML = disabled ? `<i class="fas fa-spinner fa-spin"></i> ${text}` : `<i class="fas fa-arrow-down"></i> ${text}`;
    }

    function showError(message) {
        resultsSection.style.display = 'block';
        processingIndicator.style.display = 'none';
        downloadResultContainer.style.display = 'block';
        document.getElementById('available-formats').innerHTML = `<p style="color: red; font-weight: bold;">${message}</p>`;
        statusBar.style.width = '0%';
    }

    // Helper functions
    function formatDuration(seconds) {
        if (!seconds || seconds <= 0) return 'N/A';
        return new Date(seconds * 1000).toISOString().slice(11, 19);
    }

    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
});