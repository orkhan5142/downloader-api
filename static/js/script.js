
const mobileToggle = document.getElementById('mobile-toggle');
const sidebar = document.getElementById('sidebar');

mobileToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

// Platform selection
const platformIcons = document.querySelectorAll('.platform-icon');
const urlInput = document.getElementById('url-input');
function detectPlatform(url) {
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        return 'youtube';
    } else if (url.includes('instagram.com')) {
        return 'instagram';
    } else if (url.includes('tiktok.com')) {
        return 'tiktok';
    } else if (url.includes('facebook.com') || url.includes('fb.com') || url.includes('fb.watch')) {
        return 'facebook';
    } else {
        return 'unknown';
    }
}
platformIcons.forEach(icon => {
    icon.addEventListener('click', () => {
        platformIcons.forEach(i => i.classList.remove('active'));
        icon.classList.add('active');
        
        const platform = icon.getAttribute('data-platform');
        if (platform !== "Home") {
            urlInput.placeholder = `Paste your ${platform} video link here...`;
            urlInput.focus();
        }
        
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
        }
    });
});

// Download button functionality
const downloadBtn = document.getElementById('download-btn');
const resultsSection = document.getElementById('results-section');
const processingIndicator = document.querySelector('.processing-indicator span');
const progressBar = document.querySelector('.status-bar .progress');
const downloadResult = document.querySelector('.download-result');
const mediaThumbnail = document.querySelector('.media-thumbnail img');
const mediaDetails = document.querySelector('.media-details');
const availableFormats = document.querySelector('.available-formats');


let currentVideoInfo = {};

// Get formats button click
let currentProcessStage = '';

// Get formats button click
downloadBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    
    if (!url) {
        urlInput.parentElement.classList.add('shake');
        setTimeout(() => {
            urlInput.parentElement.classList.remove('shake');
        }, 500);
        urlInput.focus();
        return;
    }

    // Show loading state
    resultsSection.classList.add('active');
    downloadBtn.disabled = true;
    processingIndicator.textContent = 'Fetching video info...';
    progressBar.style.width = '0%';
    progressBar.classList.remove('complete');
    downloadResult.style.display = 'none';
    currentProcessStage = 'fetching';

    try {
        // Simulate progress for fetching stage
        simulateProgress('fetching', 80, 1500);
        
        // 1. Get available formats
        const response = await fetch('/api/downloader/get-formats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Failed to get formats');
        }

        // Complete fetching stage
        progressBar.style.width = '100%';
        currentProcessStage = 'displaying';
        
        // 2. Display the results
        currentVideoInfo = {
            title: data.title,
            platform: detectPlatform(url)
        };

        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        processingIndicator.textContent = `Error: ${error.message}`;
        progressBar.style.width = '0%';
    } finally {
        downloadBtn.disabled = false;
    }
});

// Simulate progress for a process
function simulateProgress(stage, targetPercent, duration) {
    if (currentProcessStage !== stage) return;
    
    const startTime = Date.now();
    const interval = 30; // update every 30ms
    const increment = (targetPercent / (duration / interval));
    let currentPercent = 0;
    
    const progressInterval = setInterval(() => {
        if (currentProcessStage !== stage) {
            clearInterval(progressInterval);
            return;
        }
        
        const elapsed = Date.now() - startTime;
        if (elapsed >= duration) {
            currentPercent = targetPercent;
            clearInterval(progressInterval);
        } else {
            currentPercent = Math.min(targetPercent, currentPercent + increment);
        }
        
        progressBar.style.width = `${currentPercent}%`;
    }, interval);
}

function formatSize(bytes) {
    if (!bytes || isNaN(bytes)) return 'N/A';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

function displayResults(data) {
    // Update processing indicator
    processingIndicator.textContent = 'Select your preferred format';
    
    // Update thumbnail
    const videoId = extractVideoId(urlInput.value);
    if (videoId) {
        mediaThumbnail.src = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    }
    mediaThumbnail.alt = data.title;
    
    // Update media details
    mediaDetails.innerHTML = `
        <h3>${data.title}</h3>
        <div class="source">
            <i class="fab fa-${currentVideoInfo.platform.toLowerCase()}"></i>
            <span>${currentVideoInfo.platform.charAt(0).toUpperCase() + currentVideoInfo.platform.slice(1)}</span>
        </div>
    `;
    
    // Clear existing formats
    availableFormats.innerHTML = '';
    
    // Filter formats based on platform
    const filteredFormats = data.formats.filter(format => {
        const resolution = format.height || parseInt(format.resolution || format.format_note);
        // Apply filesize filter only for YouTube
        if (currentVideoInfo.platform === 'youtube') {
            return (
                (format.ext === 'mp4' || format.ext === 'm4a') &&
                format.filesize && 
                format.filesize > 100000
            );
        } else {
            // For other platforms, skip filesize filter
            return (
                (format.ext === 'mp4' || format.ext === 'm4a')
            );
        }
    });
    
    // Group formats (just for sorting, we won't display headers)
    const formatGroups = {
        video: {},  // Video with audio
        videoOnly: {}, // Video only
        audioOnly: {}  // Audio only
    };
    
    filteredFormats.forEach(format => {
        // Determine format type
        let type, quality;
        
        if (format.vcodec !== 'none' && format.acodec !== 'none') {
            // Video with audio
            type = 'video';
            quality = format.resolution || format.format_note || 'HD';
        } else if (format.vcodec !== 'none' && format.acodec === 'none') {
            // Video only
            type = 'videoOnly';
            quality = format.resolution || format.format_note || 'HD';
        } else if (format.vcodec === 'none' && format.acodec !== 'none') {
            // Audio only
            type = 'audioOnly';
            quality = format.abr ? `${format.abr}kbps` : 'High Quality';
        } else {
            // Skip if neither video nor audio
            return;
        }
        
        if (!formatGroups[type][quality]) {
            formatGroups[type][quality] = [];
        }
        formatGroups[type][quality].push(format);
    });
    
    // Display formats in order without group headers
    // 1. Video with audio (highest quality first)
    Object.keys(formatGroups.video)
        .sort((a, b) => {
            const numA = parseInt(a) || 0;
            const numB = parseInt(b) || 0;
            return numB - numA;
        })
        .forEach(quality => {
            const bestFormat = formatGroups.video[quality]
                .sort((a, b) => b.filesize - a.filesize)[0];
            availableFormats.appendChild(createFormatItem(bestFormat, 'Video'));
        });
    
    // 2. Video only (highest quality first)
    Object.keys(formatGroups.videoOnly)
        .sort((a, b) => {
            const numA = parseInt(a) || 0;
            const numB = parseInt(b) || 0;
            return numB - numA;
        })
        .forEach(quality => {
            const bestFormat = formatGroups.videoOnly[quality]
                .sort((a, b) => b.filesize - a.filesize)[0];
            availableFormats.appendChild(createFormatItem(bestFormat, 'Video Only'));
        });
    
    // 3. Audio only (highest bitrate first)
    Object.keys(formatGroups.audioOnly)
        .sort((a, b) => {
            const bitrateA = parseInt(a) || 0;
            const bitrateB = parseInt(b) || 0;
            return bitrateB - bitrateA;
        })
        .forEach(quality => {
            const bestFormat = formatGroups.audioOnly[quality]
                .sort((a, b) => b.filesize - a.filesize)[0];
            availableFormats.appendChild(createFormatItem(bestFormat, 'Audio'));
        });
    
    // Show results section
    downloadResult.style.display = 'block';
    progressBar.style.width = '100%';
}

function createFormatItem(format) {
    const formatItem = document.createElement('div');
    formatItem.className = 'format-item';
    
    // Determine icon and type based on format
    let icon, typeLabel;
    if (format.vcodec !== 'none' && format.acodec !== 'none') {
        icon = 'fa-video';
        typeLabel = 'Video with Audio';
    } else if (format.vcodec !== 'none') {
        icon = 'fa-volume-mute';
        typeLabel = 'Video Only';
    } else {
        icon = 'fa-volume-up';
        typeLabel = 'Audio';
    }
    
    // Quality label
    let qualityLabel = '';
    if (format.vcodec !== 'none') {
        qualityLabel = format.resolution || format.format_note || 'HD';
    } else {
        const bitrate = format.abr || format.tbr || '';
        qualityLabel = bitrate ? `${bitrate}kbps` : 'High Quality';
    }
    
    const fileSize = format.filesize ? ` (${formatSize(format.filesize)})` : '';
    const codecInfo = format.vcodec || format.acodec ? ` [${(format.vcodec || format.acodec).split('.')[0]}]` : '';
    
    formatItem.innerHTML = `
        <span class="format-info">
            <i class="fas ${icon}"></i>
            <span class="format-quality">${qualityLabel}</span>
            <span class="format-details">${typeLabel} • ${format.ext.toUpperCase()}${codecInfo}${fileSize}</span>
        </span>
        <i class="fas fa-download download-icon"></i>
    `;
    
    // Determine download type based on format
    let downloadType;
    if (format.vcodec !== 'none' && format.acodec !== 'none') {
        downloadType = 'video';
    } else if (format.vcodec !== 'none') {
        downloadType = 'video only';
    } else {
        downloadType = 'audio';
    }
    
    formatItem.addEventListener('click', () => {
        downloadFormat(format.format_id, downloadType);
    });
    
    return formatItem;
}

async function downloadFormat(formatId, downloadType) {
    currentProcessStage = 'downloading';
    processingIndicator.textContent = 'Preparing download...';
    progressBar.style.width = '0%';
    progressBar.classList.remove('complete');
    
    // Simulate initial download progress
    simulateProgress('downloading', 70, 1000);
    
    try {
        const response = await fetch('/api/downloader/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: urlInput.value.trim(),
                download_type: downloadType,
                format_id: formatId
            })
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        // Simulate finalizing progress

        
        // Get filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = currentVideoInfo.title || 'download';
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
            if (filenameMatch) filename = filenameMatch[1];
        } else {
            filename += downloadType === 'video' ? '.mp4' : '.m4a';
        }

        // Create blob from response
        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        
        // Create download link
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(downloadUrl);
        }, 100);

        // Complete the progress
        processingIndicator.textContent = 'Download complete!';
        progressBar.style.width = '100%';
        progressBar.classList.add('complete');
        currentProcessStage = 'complete';
        
    } catch (error) {
        console.error('Download error:', error);
        processingIndicator.textContent = `Error: ${error.message}`;
        progressBar.style.width = '0%';
        currentProcessStage = 'error';
    }
}


// Helper function to extract video ID from URL
function extractVideoId(url) {
    // YouTube
    const youtubeRegExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const youtubeMatch = url.match(youtubeRegExp);
    if (youtubeMatch && youtubeMatch[2].length === 11) {
        return youtubeMatch[2];
    }
    
    // TikTok
    const tiktokRegExp = /tiktok\.com\/.+\/video\/(\d+)/;
    const tiktokMatch = url.match(tiktokRegExp);
    if (tiktokMatch) {
        return tiktokMatch[1];
    }
    
    return null;
}