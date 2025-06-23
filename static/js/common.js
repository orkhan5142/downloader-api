const initializeHeaderScripts = () => {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        body.className = savedTheme + '-mode';
        themeToggle.checked = savedTheme === 'dark';
    } else if (systemPrefersDark) {
        body.className = 'dark-mode';
        themeToggle.checked = true;
    } else {
        body.className = 'light-mode';
        themeToggle.checked = false;
    }

    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            body.classList.replace('light-mode', 'dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.replace('dark-mode', 'light-mode');
            localStorage.setItem('theme', 'light');
        }
    });

    // Mobile toggle
    const mobileToggle = document.getElementById('mobile-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
};


const loadComponent = async (selector, url, callback) => {
    const element = document.querySelector(selector);
    if (element) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Could not load ${url}: ${response.statusText}`);
            const text = await response.text();
            element.innerHTML = text;
            if (callback) callback();
        } catch (error) {
            console.error(`Failed to load component from ${url}:`, error);
            element.innerHTML = `<p style="color: red; text-align: center;">Error: Could not load content.</p>`;
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    loadComponent('#header-placeholder', '/static/partials/_header.html', initializeHeaderScripts);
    
    loadComponent('#footer-placeholder', '/static/partials/_footer.html');
});