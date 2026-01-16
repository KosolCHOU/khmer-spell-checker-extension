// Minimal Popup Logic for Toggle
document.addEventListener('DOMContentLoaded', async () => {
    const enableToggle = document.getElementById('enableToggle');
    const themeSelect = document.getElementById('themeSelect');

    // Load initial state
    try {
        const result = await chrome.storage.local.get(['enabled', 'theme']);
        // Default to true if not set
        const isEnabled = result.hasOwnProperty('enabled') ? result.enabled : true;
        const theme = result.hasOwnProperty('theme') ? result.theme : 'dark';
        enableToggle.checked = isEnabled;
        themeSelect.value = theme;
    } catch (e) {
        console.error('Failed to load settings:', e);
    }

    // Handle enable toggle change
    enableToggle.addEventListener('change', async () => {
        const isEnabled = enableToggle.checked;
        try {
            await chrome.storage.local.set({ enabled: isEnabled });
            console.log('Extension enabled state:', isEnabled);
        } catch (e) {
            console.error('Failed to save settings:', e);
        }
    });

    // Handle theme change
    themeSelect.addEventListener('change', async () => {
        const theme = themeSelect.value;
        try {
            await chrome.storage.local.set({ theme: theme });
            console.log('Theme changed to:', theme);
        } catch (e) {
            console.error('Failed to save theme setting:', e);
        }
    });
});
