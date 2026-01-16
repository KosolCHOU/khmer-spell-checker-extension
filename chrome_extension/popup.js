// ===== Global State =====
let activeElement = null;
let currentErrors = [];
let ignoredWords = new Set();
let debounceTimer = null;
let badge = null;
let suggestionCard = null;
let currentSuggestionError = null;
let isPanelDragging = false;
let panelDragOffset = { x: 0, y: 0 };
let panelPosition = null; // Store custom panel position when dragged
let isExtensionEnabled = true; // Default state
let currentTheme = 'dark'; // Theme state: 'dark', 'light', or 'auto'
let isApplyingSuggestion = false; // Flag to prevent recheck when applying suggestion
let isMovingCursor = false; // Flag to prevent recheck when just moving cursor
let isProgrammaticClick = false; // Flag to prevent recheck on programmatic clicks in Google Docs
let googleDocsMapping = []; // Mapping of text ranges to Google Docs elements

// Helper function to determine if light mode should be active
function shouldUseLightMode() {
    if (currentTheme === 'light') return true;
    if (currentTheme === 'dark') return false;
    // Auto mode - detect system preference
    if (currentTheme === 'auto') {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    }
    return false;
}

// ===== Google Docs Utilities =====
function isGoogleDocs() {
    return window.location.hostname === 'docs.google.com' && window.location.pathname.includes('/document/');
}

function getGoogleDocsText() {
    let fullText = '';
    googleDocsMapping = [];

    // 1. Try Accessibility SVG scraping (aria-label on rect/g)
    // This provides coordinate mapping implicitly via the rects
    const accessElements = document.querySelectorAll('.kix-canvas-tile-content svg g rect[aria-label]');

    if (accessElements.length > 0) {
        accessElements.forEach(el => {
            const label = el.getAttribute('aria-label');
            if (label) {
                // Approximate mapping: assume the rect covers the text
                googleDocsMapping.push({
                    start: fullText.length,
                    end: fullText.length + label.length,
                    element: el,
                    isRect: true // flag to use getBoundingClientRect directly
                });
                fullText += label + '\n';
            }
        });
        return fullText;
    }

    // 2. Fallback: Try legacy/compat mode (kix-lineview-content)
    const lines = document.querySelectorAll('.kix-lineview-content');
    if (lines.length > 0) {
        lines.forEach(line => {
            let lineText = '';
            const walker = document.createTreeWalker(line, NodeFilter.SHOW_TEXT, null, false);
            let node;
            while (node = walker.nextNode()) {
                lineText += node.nodeValue;
            }

            googleDocsMapping.push({
                start: fullText.length,
                end: fullText.length + lineText.length,
                element: line,
                isRect: false
            });
            fullText += lineText + '\n';
        });
        return fullText;
    }

    // 3. Last Resort: Try hidden input (current paragraph only)
    // We can't highlight easily, but we can check the current sentence
    const iframe = document.querySelector('.docs-texteventtarget-iframe');
    if (iframe) {
        try {
            const doc = iframe.contentDocument || iframe.contentWindow.document;
            const activeInput = doc.body; // text is usually in body or a child
            const text = activeInput.innerText;
            if (text && text.trim().length > 0) {
                // No mapping possible for highlighting, but we can return text
                return text;
            }
        } catch (e) { }
    }

    return '';
}

async function applySuggestionGoogleDocs(error, suggestion) {
    // Strategy: Use real mouse events to select text, then paste

    const marker = document.querySelector(`.kh-highlight-marker[data-error-index="${error.index}"]`);

    if (!marker) {
        console.warn('Marker not found for error:', error);
        await navigator.clipboard.writeText(suggestion);
        showGoogleDocsToast(error.word, suggestion);
        return;
    }

    try {
        const rect = marker.getBoundingClientRect();

        // 1. Copy suggestion to clipboard first
        await navigator.clipboard.writeText(suggestion);
        console.log('Copied to clipboard:', suggestion);

        // 2. Hide marker to click through
        marker.style.pointerEvents = 'none';

        // Calculate positions - start and end of the word
        const startX = rect.left + 2;
        const endX = rect.right - 2;
        const centerY = rect.top + (rect.height / 2);

        const canvasElement = document.elementFromPoint(startX, centerY);

        if (!canvasElement) {
            marker.style.pointerEvents = 'auto';
            console.warn('Canvas element not found');
            showGoogleDocsToast(error.word, suggestion);
            return;
        }

        console.log('Found canvas element:', canvasElement);

        // 3. Select the word by clicking and dragging
        // First, click at the start of the word
        canvasElement.dispatchEvent(new MouseEvent('mousedown', {
            bubbles: true,
            cancelable: true,
            view: window,
            clientX: startX,
            clientY: centerY,
            button: 0
        }));

        await new Promise(resolve => setTimeout(resolve, 50));

        // Move to the end of the word (drag)
        canvasElement.dispatchEvent(new MouseEvent('mousemove', {
            bubbles: true,
            cancelable: true,
            view: window,
            clientX: endX,
            clientY: centerY,
            buttons: 1
        }));

        await new Promise(resolve => setTimeout(resolve, 50));

        // Release at the end
        canvasElement.dispatchEvent(new MouseEvent('mouseup', {
            bubbles: true,
            cancelable: true,
            view: window,
            clientX: endX,
            clientY: centerY,
            button: 0
        }));

        marker.style.pointerEvents = 'auto';

        // 4. Wait for selection to be made
        await new Promise(resolve => setTimeout(resolve, 100));

        // 5. Verify selection was made
        const selection = window.getSelection();
        const selectedText = selection.toString();
        console.log('Selected text:', selectedText);

        if (!selectedText || selectedText.trim().length === 0) {
            console.warn('No text selected, trying double-click method');

            // Fallback: try double-click
            marker.style.pointerEvents = 'none';
            const centerX = rect.left + (rect.width / 2);
            const targetEl = document.elementFromPoint(centerX, centerY);

            if (targetEl) {
                targetEl.dispatchEvent(new MouseEvent('dblclick', {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: centerX,
                    clientY: centerY,
                    button: 0,
                    detail: 2
                }));

                await new Promise(resolve => setTimeout(resolve, 150));
            }

            marker.style.pointerEvents = 'auto';
        }

        // 6. Show instruction to press Ctrl+V
        console.log('Text selected, showing Ctrl+V instruction');
        showCtrlVInstruction(rect, suggestion);

    } catch (e) {
        console.error('Google Docs suggestion application failed:', e);
        await navigator.clipboard.writeText(suggestion);
        showGoogleDocsToast(error.word, suggestion);
    }
}

function showCtrlVInstruction(rect, suggestion) {
    // Check if user has disabled this instruction
    chrome.storage.local.get(['hideCtrlVInstruction'], (result) => {
        if (result.hideCtrlVInstruction) {
            console.log('Ctrl+V instruction hidden by user preference');
            return;
        }

        // Remove any existing instruction
        const existing = document.getElementById('kh-ctrlv-instruction');
        if (existing) existing.remove();

        // Create instruction tooltip
        const tooltip = document.createElement('div');
        tooltip.id = 'kh-ctrlv-instruction';
        tooltip.innerHTML = `
            <div class="kh-ctrlv-content">
                <span class="kh-ctrlv-message">Press <kbd>Ctrl+V</kbd> to paste</span>
                <button class="kh-ctrlv-dismiss" title="Don't show again">×</button>
            </div>
        `;

        // Position near the selected text
        tooltip.style.position = 'fixed';
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.bottom + 8) + 'px';
        tooltip.style.zIndex = '1000002';

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            #kh-ctrlv-instruction {
                background: #1f2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                animation: kh-fade-in 0.2s ease-out;
            }
            
            .kh-ctrlv-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .kh-ctrlv-message {
                color: #e5e7eb;
                font-size: 13px;
                white-space: nowrap;
            }
            
            .kh-ctrlv-message kbd {
                background: #374151;
                border: 1px solid #4b5563;
                border-radius: 3px;
                padding: 2px 5px;
                font-family: monospace;
                font-size: 11px;
                margin: 0 2px;
            }
            
            .kh-ctrlv-dismiss {
                background: transparent;
                border: none;
                color: #9ca3af;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 3px;
                transition: all 0.2s;
            }
            
            .kh-ctrlv-dismiss:hover {
                background: #374151;
                color: #fff;
            }
            
            @keyframes kh-fade-in {
                from { opacity: 0; transform: translateY(-5px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;

        tooltip.appendChild(style);
        document.body.appendChild(tooltip);

        // Handle dismiss button
        const dismissBtn = tooltip.querySelector('.kh-ctrlv-dismiss');
        dismissBtn.addEventListener('click', () => {
            chrome.storage.local.set({ hideCtrlVInstruction: true });
            tooltip.remove();
            document.removeEventListener('paste', handlePaste);
            document.removeEventListener('keydown', handleKeydown);
        });

        // Listen for paste event to remove the instruction
        const handlePaste = () => {
            tooltip.remove();
            document.removeEventListener('paste', handlePaste);
            document.removeEventListener('keydown', handleKeydown);
        };

        // Also remove on Ctrl+V
        const handleKeydown = (e) => {
            if (e.key === 'v' && e.ctrlKey) {
                setTimeout(() => tooltip.remove(), 300);
                document.removeEventListener('paste', handlePaste);
                document.removeEventListener('keydown', handleKeydown);
            }
        };

        document.addEventListener('paste', handlePaste);
        document.addEventListener('keydown', handleKeydown);

        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.remove();
                document.removeEventListener('paste', handlePaste);
                document.removeEventListener('keydown', handleKeydown);
            }
        }, 8000);
    });
}

function showGoogleDocsToast(errorWord, suggestion, clipboardFailed = false) {
    // Remove existing toast if any
    const existing = document.getElementById('kh-docs-suggestion-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'kh-docs-suggestion-toast';
    toast.innerHTML = `
        <div class="kh-docs-toast-content">
            <div class="kh-docs-toast-header">
                <span class="kh-docs-toast-icon">📋</span>
                <strong>Suggestion Copied!</strong>
                <button class="kh-docs-toast-close">×</button>
            </div>
            <div class="kh-docs-toast-body">
                <p>Replace "<span class="kh-error-word">${errorWord}</span>" with:</p>
                <div class="kh-suggestion-preview">${suggestion}</div>
                <p class="kh-docs-toast-instructions">
                    ${clipboardFailed
            ? '<strong>Copy the text above</strong>, then:'
            : ''}
                    <br>1. Double-click the error word to select it
                    <br>2. Press <kbd>Ctrl</kbd>+<kbd>V</kbd> to paste
                </p>
            </div>
        </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        #kh-docs-suggestion-toast {
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: rgba(17, 24, 39, 0.98);
            border: 1px solid rgba(75, 85, 99, 0.4);
            border-radius: 12px;
            padding: 0;
            z-index: 1000001;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            min-width: 280px;
            max-width: 340px;
            animation: slideInUp 0.3s ease-out;
        }
        @keyframes slideInUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .kh-docs-toast-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            border-bottom: 1px solid rgba(75, 85, 99, 0.3);
        }
        .kh-docs-toast-header strong {
            flex: 1;
            color: #22c55e;
            font-size: 14px;
        }
        .kh-docs-toast-icon { font-size: 18px; }
        .kh-docs-toast-close {
            background: none;
            border: none;
            color: #9ca3af;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }
        .kh-docs-toast-close:hover { color: #fff; }
        .kh-docs-toast-body {
            padding: 12px 16px;
            color: #e5e7eb;
        }
        .kh-docs-toast-body p {
            margin: 0 0 8px 0;
            font-size: 13px;
            color: #9ca3af;
        }
        .kh-error-word {
            color: #f87171;
            font-weight: 500;
        }
        .kh-suggestion-preview {
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 6px;
            padding: 10px 14px;
            color: #86efac;
            font-size: 16px;
            font-family: 'Khmer OS Battambang', 'Noto Sans Khmer', sans-serif;
            margin-bottom: 12px;
            text-align: center;
        }
        .kh-docs-toast-instructions {
            font-size: 12px !important;
            line-height: 1.6;
            color: #6b7280 !important;
        }
        .kh-docs-toast-instructions kbd {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 11px;
            font-family: monospace;
        }
    `;

    toast.appendChild(style);
    document.body.appendChild(toast);

    // Close button handler
    toast.querySelector('.kh-docs-toast-close').addEventListener('click', () => {
        toast.remove();
    });

    // Auto-remove after 15 seconds
    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 15000);
}


// ===== Initialization =====
async function init() {
    console.log('🎯 Khmer Spell Checker v2.2 - Content Script Loaded!');

    // Load enabled state and theme
    try {
        const result = await chrome.storage.local.get(['enabled', 'theme']);
        isExtensionEnabled = result.hasOwnProperty('enabled') ? result.enabled : true;
        currentTheme = result.hasOwnProperty('theme') ? result.theme : 'dark';
        console.log('🎨 Theme:', currentTheme);
    } catch (e) {
        console.error('Failed to load settings:', e);
    }

    if (document.getElementById('kh-checker-badge')) return;

    createBadge();
    createSuggestionCard();
    setupEventListeners();

    // Listen for storage changes
    chrome.storage.onChanged.addListener((changes, area) => {
        if (area === 'local') {
            if (changes.enabled) {
                isExtensionEnabled = changes.enabled.newValue;
                console.log('\ud83c\udfaf Khmer Spell Checker enabled state changed:', isExtensionEnabled);

                if (!isExtensionEnabled) {
                    cleanup();
                } else if (activeElement) {
                    // Re-trigger check if we have an active element
                    checkText(activeElement);
                    updateBadgePosition();
                }
            }

            if (changes.theme) {
                currentTheme = changes.theme.newValue;
                console.log('🎨 Theme changed to:', currentTheme);

                // Apply theme to suggestion card immediately
                if (suggestionCard) {
                    const useLightMode = shouldUseLightMode();
                    if (useLightMode) {
                        suggestionCard.classList.add('light-mode');
                    } else {
                        suggestionCard.classList.remove('light-mode');
                    }
                }

                // Apply theme to inline popup if it exists
                const inlinePopup = document.querySelector('.kh-inline-suggestion-popup');
                if (inlinePopup) {
                    const useLightMode = shouldUseLightMode();
                    if (useLightMode) {
                        inlinePopup.classList.add('light-mode');
                    } else {
                        inlinePopup.classList.remove('light-mode');
                    }
                }
            }
        }
    });
}

// ===== UI Creation =====
function createBadge() {
    badge = document.createElement('div');
    badge.id = 'kh-checker-badge';
    badge.className = 'kh-checker-badge';
    badge.style.display = 'none';
    badge.textContent = '0';

    badge.addEventListener('mousedown', (e) => {
        e.preventDefault();
        e.stopPropagation();
    });

    badge.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (currentErrors.length > 0) {
            showAllErrorsPanel();
        } else if (isGoogleDocs() && currentErrors.length === 0) {
            // Check if we failed to read text
            const text = getGoogleDocsText();
            if (!text.trim()) {
                showAccessibilityToast();
            }
        }
    });

    document.body.appendChild(badge);
}

function showAccessibilityToast() {
    let toast = document.getElementById('kh-access-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'kh-access-toast';
        toast.className = 'kh-toast';
        toast.innerHTML = `
            <div class="kh-toast-content">
                <strong>Enable Spell Check</strong>
                <p>Go to <b>Tools > Accessibility settings</b> and turn on <b>Screen reader support</b> to use this extension.</p>
            </div>
            <button class="kh-toast-close">×</button>
        `;

        // Add styles dynamically if not present
        if (!document.getElementById('kh-toast-style')) {
            const style = document.createElement('style');
            style.id = 'kh-toast-style';
            style.textContent = `
                .kh-toast {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #333;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    z-index: 10000;
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    font-family: sans-serif;
                    max-width: 300px;
                    animation: slideIn 0.3s ease-out;
                }
                .kh-toast-content strong { display: block; margin-bottom: 4px; color: #ffeb3b; }
                .kh-toast-content p { margin: 0; font-size: 13px; line-height: 1.4; opacity: 0.9; }
                .kh-toast-close { background: none; border: none; color: white; cursor: pointer; font-size: 20px; padding: 0; opacity: 0.7; }
                .kh-toast-close:hover { opacity: 1; }
                @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `;
            document.head.appendChild(style);
        }

        toast.querySelector('.kh-toast-close').addEventListener('click', () => {
            toast.remove();
        });

        document.body.appendChild(toast);

        // Auto-remove after 10s
        setTimeout(() => toast.remove(), 10000);
    }
}

function createSuggestionCard() {
    suggestionCard = document.createElement('div');
    suggestionCard.id = 'kh-suggestion-card';
    suggestionCard.className = 'kh-suggestion-card hidden';

    // Apply light mode if enabled
    const useLightMode = shouldUseLightMode();
    if (useLightMode) {
        suggestionCard.classList.add('light-mode');
    }

    suggestionCard.innerHTML = `
        <div class="kh-card-header">
            <div class="kh-header-logo-group">
                <svg class="kh-header-logo" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="panelLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#38bdf8;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#0ea5e9;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <circle cx="16" cy="16" r="14" fill="url(#panelLogoGradient)" opacity="0.15"/>
                    <path d="M10 6C10 5.44772 10.4477 5 11 5H17L22 10V25C22 25.5523 21.5523 26 21 26H11C10.4477 26 10 25.5523 10 25V6Z" 
                          stroke="currentColor" stroke-width="1.5" fill="none"/>
                    <path d="M17 5V9C17 9.55228 17.4477 10 18 10H22" 
                          stroke="currentColor" stroke-width="1.5" fill="none"/>
                    <text x="16" y="19" font-family="Khmer OS Battambang, Hanuman" font-size="10" 
                          fill="currentColor" text-anchor="middle" font-weight="600">ក</text>
                    <circle cx="23" cy="23" r="4.5" fill="#10b981" stroke="currentColor" stroke-width="1"/>
                    <path d="M21 23L22.5 24.5L25 21.5" stroke="white" stroke-width="1.5" 
                          stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                </svg>
                <span class="kh-header-title">Khmer Spell Checker</span>
            </div>
            <button class="kh-card-close">×</button>
        </div>
        <div class="kh-card-body">
            <p class="kh-card-label">Suggested corrections:</p>
            <div class="kh-card-suggestions"></div>
        </div>
    `;

    document.body.appendChild(suggestionCard);

    // Get header element for dragging
    const header = suggestionCard.querySelector('.kh-card-header');

    // Make header draggable
    header.style.cursor = 'grab';
    header.addEventListener('mousedown', (e) => {
        // Check if it's a left click
        if (e.button !== 0) return;

        // Start dragging
        isPanelDragging = true;
        const rect = suggestionCard.getBoundingClientRect();
        panelDragOffset.x = e.clientX - rect.left;
        panelDragOffset.y = e.clientY - rect.top;

        header.style.cursor = 'grabbing';

        // Prevent text selection
        e.preventDefault();
        e.stopPropagation();
    });



    // Event listeners
    suggestionCard.querySelector('.kh-card-close').addEventListener('click', hideSuggestionCard);

    // Prevent focus loss when clicking on the panel
    suggestionCard.addEventListener('mousedown', (e) => {
        // Prevent default to stop focus change, but allow clicks to work
        e.preventDefault();
    });

    // Prevent card from closing when clicking inside it
    suggestionCard.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

// ===== Event Listeners =====
function setupEventListeners() {
    // Monitor focus on editable elements
    document.addEventListener('focusin', handleFocusIn, true);
    document.addEventListener('focusout', handleFocusOut, true);

    // Global mouse events for dragging
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    // Update highlights on scroll and resize
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            if (currentErrors.length > 0 && activeElement) {
                renderHighlights();
                updateBadgePosition();
            }
        }, 100);
    }, true);

    window.addEventListener('resize', () => {
        if (currentErrors.length > 0 && activeElement) {
            renderHighlights();
            updateBadgePosition();
        }
    });
}

function handleFocusIn(e) {
    const target = e.target;

    if (!isExtensionEnabled) return;

    // Special handling for Google Docs
    if (isGoogleDocs()) {
        const editor = document.querySelector('.kix-appview-editor');
        if (editor && (editor.contains(target) || target.classList.contains('docs-texteventtarget-iframe'))) {
            activeElement = editor;
            setupGoogleDocsListeners();
            checkText(activeElement);
            updateBadgePosition();

            // Check if we need to show accessibility warning
            setTimeout(() => {
                const text = getGoogleDocsText();
                if (!text.trim()) {
                    showAccessibilityToast();
                }
            }, 2000);

            return;
        }
    }

    if (!isEditable(target)) return;

    activeElement = target;

    // Add input listener (only once)
    if (!target.khmerCheckerListenerAdded) {
        target.addEventListener('input', handleInput);
        target.addEventListener('click', handleClick);
        target.khmerCheckerListenerAdded = true;
    }

    // Initial check - skip if we're just moving cursor or text hasn't changed
    const currentText = getText(target);
    if (!isMovingCursor && currentText !== previousText) {
        previousText = currentText;
        checkText(target);
    }
    updateBadgePosition();
}

function handleFocusOut(e) {
    setTimeout(() => {
        if (isGoogleDocs()) return; // Keep active in Docs

        // Only cleanup if focus moved to a different editable element
        // Keep highlights and badge visible when clicking outside
        const newFocus = document.activeElement;

        // Check if focus moved to another editable element (not our UI)
        if (newFocus &&
            isEditable(newFocus) &&
            newFocus !== activeElement &&
            !suggestionCard.contains(newFocus) &&
            newFocus !== badge) {
            // User switched to a different text field - cleanup old one
            cleanup();
        }
        // Otherwise, keep everything active (highlights, badge, panel)
        // This allows users to click outside and come back without rechecking
    }, 200);
}


let previousText = ''; // Track previous text content

function handleInput() {
    if (!activeElement || !isExtensionEnabled) return;

    // Skip recheck if we're applying a suggestion
    if (isApplyingSuggestion) {
        isApplyingSuggestion = false;
        return;
    }

    // Get current text
    const currentText = getText(activeElement);

    // If we're moving cursor, check if text actually changed
    if (isMovingCursor) {
        if (currentText === previousText) {
            // Text hasn't changed, just cursor movement - skip recheck
            setTimeout(() => {
                isMovingCursor = false;
            }, 100);
            return;
        } else {
            // Text changed - user is typing, reset flag and proceed with recheck
            isMovingCursor = false;
        }
    }

    // Update previous text
    previousText = currentText;

    // Show loading state on badge while typing instead of hiding it
    if (badge) {
        badge.style.display = 'flex';
        badge.className = 'kh-checker-badge loading';
        badge.textContent = '⟳';
    }
    clearHighlights();

    // Debounce check
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        checkText(activeElement);
    }, isGoogleDocs() ? 1500 : 800);
}

function setupGoogleDocsListeners() {
    if (window.khmerDocsListenerAdded) return;
    window.khmerDocsListenerAdded = true;

    // Monitor for changes in the line views
    const observer = new MutationObserver((mutations) => {
        // Skip if we're programmatically clicking (e.g., moving cursor to error)
        if (isProgrammaticClick) {
            return;
        }

        // Only recheck if there were actual text content changes
        const hasContentChange = mutations.some(mutation =>
            mutation.type === 'characterData' ||
            (mutation.type === 'childList' && mutation.addedNodes.length > 0)
        );

        if (hasContentChange) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                checkText(activeElement);
            }, 1500);
        }
    });

    const editorBody = document.querySelector('.kix-paginatedpage-canvas') || document.querySelector('.kix-appview-editor');
    if (editorBody) {
        observer.observe(editorBody, { childList: true, subtree: true, characterData: true });
    }

    // Add scroll listener to re-render highlights when scrolling
    document.addEventListener('scroll', () => {
        if (isGoogleDocs()) {
            renderHighlights();
            updateBadgePosition();
        }
    }, true);
}

function handleClick(e) {
    if (!isExtensionEnabled) return;

    // Set flag to prevent recheck on focus
    isMovingCursor = true;
    setTimeout(() => {
        isMovingCursor = false;
    }, 100);

    // Check if clicked on highlighted error
    const marker = e.target.closest('.kh-highlight-marker');
    if (marker) {
        e.preventDefault();
        e.stopPropagation();
        const errorIndex = parseInt(marker.dataset.errorIndex);
        const error = currentErrors[errorIndex];
        if (error) {
            showSuggestionCard(error, e.clientX, e.clientY);
        }
    }
}

function handleMouseMove(e) {
    if (!isPanelDragging || !suggestionCard) return;

    // Add dragging class for visual feedback
    suggestionCard.classList.add('dragging');

    // Update panel position
    const x = e.clientX - panelDragOffset.x;
    const y = e.clientY - panelDragOffset.y;

    // Keep panel within viewport
    const maxX = window.innerWidth - suggestionCard.offsetWidth;
    const maxY = window.innerHeight - suggestionCard.offsetHeight;

    panelPosition = {
        x: Math.max(0, Math.min(x, maxX)),
        y: Math.max(0, Math.min(y, maxY))
    };

    suggestionCard.style.left = panelPosition.x + 'px';
    suggestionCard.style.top = panelPosition.y + 'px';
}

function handleMouseUp(e) {
    if (isPanelDragging) {
        // Remove dragging class
        suggestionCard.classList.remove('dragging');

        // Reset cursor
        const header = suggestionCard.querySelector('.kh-card-header');
        if (header) {
            header.style.cursor = 'grab';
        }

        isPanelDragging = false;
    }
}



// ===== Utilities =====
function isEditable(el) {
    if (isGoogleDocs()) return true;
    return (el.tagName === 'TEXTAREA' ||
        (el.tagName === 'INPUT' && el.type === 'text') ||
        el.isContentEditable);
}

function getText(el) {
    if (isGoogleDocs()) {
        return getGoogleDocsText();
    }
    if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        return el.value;
    } else {
        return el.innerText || el.textContent || '';
    }
}

function setText(el, text) {
    if (isGoogleDocs()) return; // Handled by applySuggestionGoogleDocs
    if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        el.value = text;
    } else {
        el.innerText = text;
    }
}


function moveCursorToError(error) {
    if (!activeElement) return;

    // Special handling for Google Docs
    if (isGoogleDocs()) {
        const marker = document.querySelector(`.kh-highlight-marker[data-error-index="${error.index}"]`);
        if (marker) {
            const rect = marker.getBoundingClientRect();
            // Click near the end of the word (right side)
            // ensuring we stay within the element bounds
            const clickX = rect.left + (rect.width * 0.9);

            const clickEvent = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: clickX,
                clientY: rect.top + (rect.height / 2)
            });

            marker.style.pointerEvents = 'none';
            const docsElement = document.elementFromPoint(clickX, rect.top + (rect.height / 2));
            marker.style.pointerEvents = 'auto';

            if (docsElement) {
                // Set flag to prevent MutationObserver from triggering recheck
                isProgrammaticClick = true;
                docsElement.dispatchEvent(clickEvent);
                docsElement.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                // Reset flag after a short delay
                setTimeout(() => {
                    isProgrammaticClick = false;
                }, 200);
            }
        }
        return;
    }

    // Ensure the element has focus
    activeElement.focus();

    // Set cursor position to the end of the error word
    if (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT') {
        // Place cursor at the end of the error word
        activeElement.setSelectionRange(error.end, error.end);
    } else if (activeElement.isContentEditable) {
        // For contenteditable elements
        try {
            const selection = window.getSelection();
            const range = document.createRange();

            // Find the text node and position
            const walker = document.createTreeWalker(
                activeElement,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            let currentOffset = 0;
            let endNode = null;
            let endOffset = 0;
            let node;

            while (node = walker.nextNode()) {
                const nodeLength = node.nodeValue.length;
                const nodeEnd = currentOffset + nodeLength;

                // Find end position
                if (!endNode && currentOffset <= error.end && error.end <= nodeEnd) {
                    endNode = node;
                    endOffset = error.end - currentOffset;
                    break;
                }

                currentOffset = nodeEnd;
            }

            if (endNode) {
                // Place cursor at the end of the error word
                range.setStart(endNode, endOffset);
                range.setEnd(endNode, endOffset);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        } catch (e) {
            console.error('Error setting cursor position:', e);
        }
    }
}

function cleanup() {
    if (activeElement) {
        activeElement.removeEventListener('input', handleInput);
        activeElement.removeEventListener('click', handleClick);
    }

    clearHighlights();
    if (badge) badge.style.display = 'none';
    hideSuggestionCard();
    currentErrors = [];
    activeElement = null;
}

// ===== Spell Checking =====
async function checkText(element) {
    if (!element || !isExtensionEnabled) return;

    const text = getText(element);
    if (!text.trim()) {
        currentErrors = [];
        updateBadge();
        clearHighlights();
        return;
    }

    setBadgeLoading(true);

    try {
        const response = await chrome.runtime.sendMessage({
            action: 'checkText',
            text: text
        });

        if (response && response.success) {
            processResults(response.data, text);
        } else {
            console.error('Spell check API failed:', response ? response.error : 'No response');
            updateBadge(); // Reset to normal badge state
        }
    } catch (error) {
        console.error('Spell check error:', error);
        updateBadge(); // Reset to normal badge state
    } finally {
        setBadgeLoading(false);
    }
}

function processResults(data, text) {
    const { tokens, errors } = data;

    // Build error list with positions
    currentErrors = [];
    let position = 0;

    tokens.forEach((token, index) => {
        const error = errors.find(e => e.index === index);

        if (error && !ignoredWords.has(token)) {
            // Use the full error token text (which might be merged from multiple tokens)
            // instead of the single token segment for highlighting
            const errorWord = error.token || token;

            currentErrors.push({
                word: errorWord,
                start: position,
                end: position + errorWord.length,
                suggestions: error.suggestions.map(s => s.word).slice(0, 5),
                index: currentErrors.length
            });
        }

        position += token.length;
    });

    updateBadge();
    renderHighlights();

    // Update panel if it's currently visible
    if (!suggestionCard.classList.contains('hidden')) {
        if (currentErrors.length > 0) {
            showAllErrorsPanel();
        } else {
            showSuccessState();
        }
    }
}

// ===== Badge =====
function updateBadge() {
    if (!badge) return;

    if (currentErrors.length > 0) {
        badge.textContent = currentErrors.length;
        badge.className = 'kh-checker-badge has-errors';
        badge.style.display = 'flex';
    } else {
        badge.textContent = '✓';
        badge.className = 'kh-checker-badge no-errors';
        badge.style.display = 'flex';
    }

    updateBadgePosition();
}

function showSuccessState() {
    const cardBody = suggestionCard.querySelector('.kh-card-body');
    const isAlreadyVisible = !suggestionCard.classList.contains('hidden');

    // Get text stats for encouragement
    const text = activeElement ? getText(activeElement) : '';
    const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    const charCount = text.length;

    cardBody.innerHTML = `
        <div class="kh-success-state">
            <svg class="kh-success-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="successLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <circle cx="16" cy="16" r="14" fill="url(#successLogoGradient)" opacity="0.2"/>
                <path d="M10 6C10 5.44772 10.4477 5 11 5H17L22 10V25C22 25.5523 21.5523 26 21 26H11C10.4477 26 10 25.5523 10 25V6Z" 
                      stroke="currentColor" stroke-width="1.5" fill="none"/>
                <path d="M17 5V9C17 9.55228 17.4477 10 18 10H22" 
                      stroke="currentColor" stroke-width="1.5" fill="none"/>
                <text x="16" y="19" font-family="Khmer OS Battambang, Hanuman" font-size="10" 
                      fill="currentColor" text-anchor="middle" font-weight="600">ក</text>
                <circle cx="23" cy="23" r="4.5" fill="#10b981"/>
                <path d="M21 23L22.5 24.5L25 21.5" stroke="white" stroke-width="1.5" 
                      stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            </svg>
            <h3 class="kh-success-title">Perfect!</h3>
            <p class="kh-success-message">No errors found</p>
            <div class="kh-success-stats">
                <div class="kh-stat">
                    <span class="kh-stat-value">${wordCount}</span>
                    <span class="kh-stat-label">words</span>
                </div>
                <div class="kh-stat-divider"></div>
                <div class="kh-stat">
                    <span class="kh-stat-value">${charCount}</span>
                    <span class="kh-stat-label">characters</span>
                </div>
            </div>
        </div>
    `;

    // Only reposition if the panel is being opened for the first time
    if (!isAlreadyVisible) {
        const rect = badge.getBoundingClientRect();
        positionSuggestionCard(rect.left, rect.bottom + 5);
    }

    suggestionCard.classList.remove('hidden');
}

function setBadgeLoading(isLoading) {
    if (!badge) return;

    if (isLoading) {
        badge.className = 'kh-checker-badge loading';
        badge.textContent = '⟳';
    }
}

function updateBadgePosition() {
    if (!activeElement || !badge) return;

    if (isGoogleDocs()) {
        const cursor = document.querySelector('.kix-cursor');
        if (cursor) {
            const rect = cursor.getBoundingClientRect();
            badge.style.top = (window.scrollY + rect.bottom + 5) + 'px';
            badge.style.left = (window.scrollX + rect.right + 5) + 'px';
            badge.style.position = 'absolute';
            badge.style.display = 'flex';
            return;
        }
        // Fallback to bottom right of editor
        const rect = activeElement.getBoundingClientRect();
        badge.style.top = (window.scrollY + rect.bottom - 60) + 'px';
        badge.style.left = (window.scrollX + rect.right - 60) + 'px';
        badge.style.position = 'absolute';
        badge.style.display = 'flex';
        return;
    }

    const rect = activeElement.getBoundingClientRect();
    let top = rect.bottom - 24;
    let left = rect.right - 24;

    // Try to get cursor position
    try {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const r = range.getBoundingClientRect();
            if (r.top !== 0 || r.bottom !== 0) {
                top = r.bottom + 5;
                left = r.right + 5;
            }
        }
    } catch (e) { /* ignore */ }

    badge.style.top = top + 'px';
    badge.style.left = left + 'px';
}

function showAllErrorsPanel() {
    if (currentErrors.length === 0) return;

    const cardBody = suggestionCard.querySelector('.kh-card-body');
    const isAlreadyVisible = !suggestionCard.classList.contains('hidden');

    cardBody.innerHTML = '';

    currentErrors.forEach((error, index) => {
        const errorItem = document.createElement('div');
        errorItem.className = 'kh-error-item';
        errorItem.dataset.errorIndex = index;

        const errorWordDiv = document.createElement('div');
        errorWordDiv.className = 'kh-error-word-container';
        errorWordDiv.innerHTML = `
            <span class="kh-error-text">${escapeHtml(error.word)}</span>
            <button class="kh-error-ignore" data-error-index="${index}">Ignore</button>
        `;
        errorItem.appendChild(errorWordDiv);

        // Add ignore button event listener
        const ignoreBtn = errorWordDiv.querySelector('.kh-error-ignore');
        ignoreBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            handleIgnoreSpecificError(error);
        });

        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'kh-suggestions-container';

        const suggestionsWrapper = document.createElement('div');
        suggestionsWrapper.className = 'kh-suggestions-wrapper';

        error.suggestions.forEach(s => {
            const chip = document.createElement('span');
            chip.className = 'kh-suggestion-chip';
            chip.dataset.errorIndex = index;
            chip.dataset.suggestion = s;
            chip.textContent = s;
            chip.addEventListener('click', (e) => {
                e.stopPropagation();
                applySuggestion(currentErrors[parseInt(chip.dataset.errorIndex)], chip.dataset.suggestion);
            });
            suggestionsWrapper.appendChild(chip);
        });

        suggestionsContainer.appendChild(suggestionsWrapper);
        errorItem.appendChild(suggestionsContainer);

        errorItem.addEventListener('click', (e) => {
            // Don't toggle if clicking on a suggestion chip
            if (e.target.classList.contains('kh-suggestion-chip')) {
                return;
            }

            // Prevent focus loss from the text field
            e.preventDefault();
            e.stopPropagation();

            // Move cursor to the error word
            moveCursorToError(error);

            toggleErrorSuggestions(errorItem);
        });

        cardBody.appendChild(errorItem);

        // Automatically activate the first error item
        if (index === 0) {
            errorItem.classList.add('active');
        }
    });

    // Only reposition if the panel is being opened for the first time
    // If it's already visible, keep its current position
    if (!isAlreadyVisible) {
        const rect = badge.getBoundingClientRect();
        positionSuggestionCard(rect.left, rect.bottom + 5);
    }

    suggestionCard.classList.remove('hidden');
}

function toggleErrorSuggestions(errorItem) {
    const isActive = errorItem.classList.contains('active');
    const allItems = suggestionCard.querySelectorAll('.kh-error-item');

    // Close all other items
    allItems.forEach(item => {
        item.classList.remove('active');
    });

    // Toggle the clicked item (if it wasn't active, make it active)
    if (!isActive) {
        errorItem.classList.add('active');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== Highlighting =====
function renderHighlights() {
    clearHighlights();

    if (!activeElement || currentErrors.length === 0) return;

    console.log('[Highlight] Rendering highlights for', currentErrors.length, 'errors');
    console.log('[Highlight] Active element:', activeElement.tagName, activeElement.className);

    if (isGoogleDocs()) {
        renderGoogleDocsHighlights();
        return;
    }

    let successCount = 0;
    currentErrors.forEach((error, index) => {
        const marker = createHighlightMarker(error, index);
        if (marker) {
            document.body.appendChild(marker);
            successCount++;
            console.log('[Highlight] Created marker', index, 'at position:', marker.style.left, marker.style.top);
        } else {
            console.warn('[Highlight] Failed to create marker for error:', error);
        }
    });

    console.log('[Highlight] Successfully created', successCount, 'of', currentErrors.length, 'markers');
}

function createHighlightMarker(error, index) {
    if (!activeElement) return null;

    const text = getText(activeElement);

    // Verify the active element is still valid and visible
    if (!document.body.contains(activeElement)) {
        console.warn('[Highlight] Active element no longer in DOM');
        return null;
    }

    const rect = activeElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
        console.warn('[Highlight] Active element has zero dimensions');
        return null;
    }

    // For contenteditable (like Gmail), use Range API
    if (activeElement.isContentEditable) {
        try {
            const walker = document.createTreeWalker(
                activeElement,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            let currentOffset = 0;
            let node;

            while (node = walker.nextNode()) {
                const nodeLength = node.nodeValue.length;
                const nodeStart = currentOffset;
                const nodeEnd = currentOffset + nodeLength;

                // Check if this node contains the error
                if (nodeStart <= error.start && nodeEnd >= error.end) {
                    const range = document.createRange();
                    range.setStart(node, error.start - nodeStart);
                    range.setEnd(node, error.end - nodeStart);

                    const rects = range.getClientRects();
                    if (rects.length > 0) {
                        const rect = rects[0];

                        const marker = document.createElement('div');
                        marker.className = 'kh-highlight-marker';
                        // Add contextual class for blue highlighting
                        if (error.error_type === 'contextual') {
                            marker.classList.add('contextual');
                        }
                        marker.dataset.errorIndex = index;
                        marker.style.position = 'fixed';
                        marker.style.left = rect.left + 'px';
                        marker.style.top = rect.top + 'px';
                        marker.style.width = rect.width + 'px';
                        marker.style.height = rect.height + 'px';

                        marker.addEventListener('click', (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            showSuggestionCard(error, e.clientX, e.clientY);
                        });

                        return marker;
                    }
                }

                currentOffset = nodeEnd;
            }
        } catch (e) {
            console.error('Error creating highlight:', e);
        }
        return null;
    }

    // For textarea/input - use canvas for accurate text measurement
    if (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT') {
        try {
            const rect = activeElement.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(activeElement);

            console.log('[Highlight] Creating marker for textarea:', {
                tagName: activeElement.tagName,
                className: activeElement.className,
                id: activeElement.id,
                placeholder: activeElement.placeholder,
                rect: { left: rect.left, top: rect.top, width: rect.width, height: rect.height },
                errorIndex: index
            });

            // Get padding and font metrics
            const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
            const paddingTop = parseFloat(computedStyle.paddingTop) || 0;
            const fontSize = parseFloat(computedStyle.fontSize) || 16;
            const lineHeight = parseFloat(computedStyle.lineHeight) || fontSize * 1.2;

            // Create a mirror div that matches the textarea exactly
            const mirror = document.createElement('div');
            mirror.style.cssText = computedStyle.cssText;
            mirror.style.position = 'absolute';
            mirror.style.visibility = 'hidden';
            mirror.style.whiteSpace = 'pre-wrap';
            mirror.style.wordWrap = 'break-word';
            mirror.style.overflow = 'hidden';
            mirror.style.width = computedStyle.width;
            mirror.style.height = 'auto';
            mirror.style.border = computedStyle.border;
            mirror.style.padding = computedStyle.padding;
            mirror.style.font = computedStyle.font;
            mirror.style.lineHeight = computedStyle.lineHeight;

            document.body.appendChild(mirror);

            // Insert text before error
            const textBefore = text.substring(0, error.start);
            mirror.textContent = textBefore;

            // Create a span for the error word
            const errorSpan = document.createElement('span');
            const errorText = text.substring(error.start, error.end);
            errorSpan.textContent = errorText;
            errorSpan.style.display = 'inline';
            mirror.appendChild(errorSpan);

            // Get the bounding rect of the error span
            const spanRect = errorSpan.getBoundingClientRect();
            const mirrorRect = mirror.getBoundingClientRect();

            // Calculate position relative to mirror
            const relativeLeft = spanRect.left - mirrorRect.left;
            const relativeTop = spanRect.top - mirrorRect.top;

            document.body.removeChild(mirror);

            const marker = document.createElement('div');
            marker.className = 'kh-highlight-marker';
            // Add contextual class for blue highlighting
            if (error.error_type === 'contextual') {
                marker.classList.add('contextual');
            }
            marker.dataset.errorIndex = index;
            marker.style.position = 'fixed';
            marker.style.left = (rect.left + relativeLeft) + 'px';
            marker.style.top = (rect.top + relativeTop) + 'px';
            marker.style.width = spanRect.width + 'px';
            marker.style.height = spanRect.height + 'px';
            marker.style.zIndex = '999998';

            console.log('[Highlight] Created textarea marker (span method):', {
                errorIndex: index,
                errorText: errorText,
                spanRect: { left: spanRect.left, top: spanRect.top, width: spanRect.width, height: spanRect.height },
                mirrorRect: { left: mirrorRect.left, top: mirrorRect.top },
                relativePos: { left: relativeLeft, top: relativeTop },
                finalPos: { left: marker.style.left, top: marker.style.top }
            });

            marker.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                showSuggestionCard(error, e.clientX, e.clientY);
            });

            return marker;
        } catch (e) {
            console.error('[Highlight] Error creating textarea marker:', e);
            return null;
        }
    }

    return null;
}

function clearHighlights() {
    document.querySelectorAll('.kh-highlight-marker').forEach(el => el.remove());
}

function renderGoogleDocsHighlights() {
    currentErrors.forEach((error, index) => {
        // Find which mapped element this error belongs to
        const mapping = googleDocsMapping.find(m => error.start >= m.start && error.start < m.end);
        if (!mapping) return;

        let rect, marker;

        if (mapping.isRect) {
            // We have a direct rect from accessibility tree!
            // The rect contains the whole line, so we need to calculate the word's position within it
            const elRect = mapping.element.getBoundingClientRect();
            const ariaLabel = mapping.element.getAttribute('aria-label') || '';

            // Calculate relative position of error within this aria-label
            const relativeStart = error.start - mapping.start;
            const relativeEnd = error.end - mapping.start;

            // Estimate character width (approximate)
            const totalChars = ariaLabel.length;
            const charWidth = totalChars > 0 ? elRect.width / totalChars : 0;

            // Calculate the error word's position within the rect
            const errorLeft = elRect.left + (relativeStart * charWidth);
            const errorWidth = (relativeEnd - relativeStart) * charWidth;

            rect = {
                left: errorLeft,
                top: elRect.top,
                width: errorWidth,
                height: elRect.height
            };

        } else {
            // Legacy DOM logic
            const lineEl = mapping.element;
            const relativeStart = error.start - mapping.start;
            const relativeEnd = error.end - mapping.start;

            // Try to find the exact text node within the line element
            const walker = document.createTreeWalker(lineEl, NodeFilter.SHOW_TEXT, null, false);
            let node;
            let currentOffset = 0;

            while (node = walker.nextNode()) {
                const nodeLength = node.nodeValue.length;
                const nodeStart = currentOffset;
                const nodeEnd = currentOffset + nodeLength;

                if (nodeStart <= relativeStart && nodeEnd >= relativeEnd) {
                    const range = document.createRange();
                    range.setStart(node, relativeStart - nodeStart);
                    range.setEnd(node, relativeEnd - nodeStart);
                    const rects = range.getClientRects();
                    if (rects.length > 0) rect = rects[0];
                    break;
                }
                currentOffset = nodeEnd;
            }
        }

        if (rect) {
            marker = document.createElement('div');
            marker.className = 'kh-highlight-marker';
            // Add contextual class for blue highlighting
            if (error.error_type === 'contextual') {
                marker.classList.add('contextual');
            }
            marker.dataset.errorIndex = index;
            marker.style.position = 'fixed';
            marker.style.left = rect.left + 'px';
            marker.style.top = rect.top + 'px';
            marker.style.width = rect.width + 'px';
            marker.style.height = (rect.height || 20) + 'px';
            // Removed: manual styling override to match standard kh-highlight-marker

            marker.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                showSuggestionCard(error, e.clientX, e.clientY);
            });

            document.body.appendChild(marker);
        }
    });
}

// ===== Suggestion Card =====
function showSuggestionCard(error, x, y) {
    currentSuggestionError = error;

    // Set flag to prevent recheck when moving cursor
    isMovingCursor = true;

    // Move cursor to the end of the error word
    moveCursorToError(error);

    // Check if the floating panel is visible
    if (!suggestionCard.classList.contains('hidden')) {
        // Panel is visible - activate the error item in the panel instead
        const errorItems = suggestionCard.querySelectorAll('.kh-error-item');

        // Deactivate all items
        errorItems.forEach(item => item.classList.remove('active'));

        // Find and activate the clicked error item
        const targetItem = suggestionCard.querySelector(`.kh-error-item[data-error-index="${error.index}"]`);
        if (targetItem) {
            targetItem.classList.add('active');

            // Scroll the item into view if needed
            targetItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        return; // Don't show inline popup
    }

    // Panel is hidden - show inline popup
    let popup = document.querySelector('.kh-inline-suggestion-popup');
    if (!popup) {
        popup = document.createElement('div');
        popup.className = 'kh-inline-suggestion-popup';

        // Apply light mode if enabled
        const useLightMode = shouldUseLightMode();
        if (useLightMode) {
            popup.classList.add('light-mode');
        }

        document.body.appendChild(popup);

        // Click outside to close
        popup.addEventListener('mousedown', (e) => {
            e.preventDefault(); // Prevent focus loss
        });
    } else {
        // Update theme if popup already exists
        const useLightMode = shouldUseLightMode();
        if (useLightMode) {
            popup.classList.add('light-mode');
        } else {
            popup.classList.remove('light-mode');
        }
    }

    // Clear and populate with suggestions
    popup.innerHTML = '';

    error.suggestions.forEach(suggestion => {
        const chip = document.createElement('div');
        chip.className = 'kh-inline-suggestion-chip';
        chip.textContent = suggestion;
        chip.addEventListener('click', (e) => {
            e.stopPropagation();
            applySuggestion(error, suggestion);
            hideInlineSuggestionPopup();
        });
        popup.appendChild(chip);
    });

    // Add ignore button
    const ignoreBtn = document.createElement('button');
    ignoreBtn.className = 'kh-inline-ignore-btn';
    ignoreBtn.textContent = 'Ignore';
    ignoreBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        handleIgnoreSpecificError(error);
        hideInlineSuggestionPopup();
    });
    popup.appendChild(ignoreBtn);

    // Position popup above the clicked word
    // Find the highlight marker for this error
    const marker = document.querySelector(`.kh-highlight-marker[data-error-index="${error.index}"]`);
    if (marker) {
        const markerRect = marker.getBoundingClientRect();
        popup.style.left = markerRect.left + 'px';
        popup.style.top = (markerRect.top - popup.offsetHeight - 8) + 'px';

        // Adjust if popup goes off screen
        setTimeout(() => {
            const popupRect = popup.getBoundingClientRect();
            if (popupRect.top < 10) {
                // Show below if not enough space above
                popup.style.top = (markerRect.bottom + 8) + 'px';
            }
            if (popupRect.right > window.innerWidth - 10) {
                popup.style.left = (window.innerWidth - popupRect.width - 10) + 'px';
            }
            if (popupRect.left < 10) {
                popup.style.left = '10px';
            }
        }, 0);
    }

    // Show popup
    popup.classList.add('visible');

    // Add click-outside-to-close listener
    setTimeout(() => {
        const closeOnClickOutside = (e) => {
            if (!popup.contains(e.target) && !e.target.classList.contains('kh-highlight-marker')) {
                hideInlineSuggestionPopup();
                document.removeEventListener('click', closeOnClickOutside);
            }
        };
        document.addEventListener('click', closeOnClickOutside);
    }, 100);
}

function hideInlineSuggestionPopup() {
    const popup = document.querySelector('.kh-inline-suggestion-popup');
    if (popup) {
        popup.classList.remove('visible');
    }
}

function positionSuggestionCard(x, y) {
    // If panel has been manually positioned, keep it there
    if (panelPosition) {
        suggestionCard.style.left = panelPosition.x + 'px';
        suggestionCard.style.top = panelPosition.y + 'px';
        return;
    }

    const cardWidth = 340;
    const cardHeight = 300;
    const padding = 10;

    let left = x - cardWidth / 2;
    let top = y + padding;

    // Keep in viewport
    if (left < padding) left = padding;
    if (left + cardWidth > window.innerWidth - padding) {
        left = window.innerWidth - cardWidth - padding;
    }
    if (top + cardHeight > window.innerHeight - padding) {
        top = y - cardHeight - padding;
    }

    suggestionCard.style.left = left + 'px';
    suggestionCard.style.top = top + 'px';
}

function hideSuggestionCard() {
    suggestionCard.classList.add('hidden');
    currentSuggestionError = null;
}

// Keep DOM panel indices in sync with currentErrors after mutations
function updatePanelIndices() {
    if (!suggestionCard || suggestionCard.classList.contains('hidden')) return;
    const items = suggestionCard.querySelectorAll('.kh-error-item');
    items.forEach((item, idx) => {
        item.dataset.errorIndex = String(idx);
        const ignoreBtn = item.querySelector('.kh-error-ignore');
        if (ignoreBtn) ignoreBtn.dataset.errorIndex = String(idx);
        item.querySelectorAll('.kh-suggestion-chip').forEach(chip => {
            chip.dataset.errorIndex = String(idx);
        });
    });
}

// Activate a specific error item by index in the panel
function activatePanelItem(index) {
    if (!suggestionCard || suggestionCard.classList.contains('hidden')) return;
    const allItems = suggestionCard.querySelectorAll('.kh-error-item');
    allItems.forEach(item => item.classList.remove('active'));
    const target = suggestionCard.querySelector(`.kh-error-item[data-error-index="${index}"]`);
    if (target) {
        target.classList.add('active');
        // Keep the activated item in view for the user
        try { target.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); } catch (_) { }
    }
}

// ===== Actions =====
function applySuggestion(error, suggestion) {
    if (!activeElement) return;

    if (isGoogleDocs()) {
        applySuggestionGoogleDocs(error, suggestion);
    } else {
        const text = getText(activeElement);
        const newText = text.substring(0, error.start) + suggestion + text.substring(error.end);
        setText(activeElement, newText);
    }

    const cursorPosition = error.start + suggestion.length;

    // Set cursor position after the corrected word
    if (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT') {
        activeElement.focus();
        activeElement.setSelectionRange(cursorPosition, cursorPosition);
    } else if (activeElement.isContentEditable) {
        // For contenteditable elements
        activeElement.focus();
        try {
            const selection = window.getSelection();
            const range = document.createRange();

            // Find the text node and position
            const walker = document.createTreeWalker(
                activeElement,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            let currentOffset = 0;
            let node;
            let found = false;

            while (node = walker.nextNode()) {
                const nodeLength = node.nodeValue.length;
                const nodeEnd = currentOffset + nodeLength;

                if (currentOffset <= cursorPosition && cursorPosition <= nodeEnd) {
                    range.setStart(node, cursorPosition - currentOffset);
                    range.setEnd(node, cursorPosition - currentOffset);
                    selection.removeAllRanges();
                    selection.addRange(range);
                    found = true;
                    break;
                }

                currentOffset = nodeEnd;
            }

            // If not found, set cursor at the end
            if (!found && activeElement.lastChild) {
                range.selectNodeContents(activeElement);
                range.collapse(false);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        } catch (e) {
            console.error('Error setting cursor position:', e);
        }
    }

    // Set flag to prevent recheck when input event fires
    isApplyingSuggestion = true;

    // Trigger input event
    activeElement.dispatchEvent(new Event('input', { bubbles: true }));

    // Find the DOM element BEFORE we modify the array
    const errorItem = !suggestionCard.classList.contains('hidden')
        ? suggestionCard.querySelector(`.kh-error-item[data-error-index="${error.index}"]`)
        : null;

    // Update error positions locally without rechecking
    const lengthDiff = suggestion.length - (error.end - error.start);
    const errorIndex = currentErrors.findIndex(e => e.index === error.index);

    if (errorIndex !== -1) {
        // Remove the corrected error
        currentErrors.splice(errorIndex, 1);

        // Update positions of subsequent errors
        currentErrors.forEach(err => {
            if (err.start > error.start) {
                err.start += lengthDiff;
                err.end += lengthDiff;
            }
        });

        // Re-index errors
        currentErrors.forEach((err, idx) => {
            err.index = idx;
        });
    }

    // Update badge and highlights
    updateBadge();
    renderHighlights();

    // Only update the panel if it was already visible
    if (!suggestionCard.classList.contains('hidden')) {
        // Animate the removal of the specific error item
        if (errorItem) {
            // Add removing class for animation
            errorItem.classList.add('removing');

            // Remove from DOM after animation completes
            setTimeout(() => {
                errorItem.remove();

                // If no errors left, show success state
                if (currentErrors.length === 0) {
                    showSuccessState();
                } else {
                    // Re-sync indices and activate the item that moved into this slot
                    const removedIdx = Number(errorItem.dataset.errorIndex || 0);
                    updatePanelIndices();
                    const nextIndex = Math.min(removedIdx, currentErrors.length - 1);
                    activatePanelItem(nextIndex);
                }
            }, 300);
        } else if (currentErrors.length === 0) {
            // If no error item found and no errors left, show success
            showSuccessState();
        } else {
            // When we don't have the DOM node, activate the first item by default
            updatePanelIndices();
            activatePanelItem(0);
        }
    }
}


function handleIgnoreSpecificError(error) {
    if (!error) return;

    // Find the DOM element BEFORE we modify the array
    const errorItem = suggestionCard.querySelector(`.kh-error-item[data-error-index="${error.index}"]`);

    // Add to ignored words
    ignoredWords.add(error.word);

    // Remove from current errors
    const errorIndex = currentErrors.findIndex(e => e.index === error.index);
    if (errorIndex !== -1) {
        currentErrors.splice(errorIndex, 1);

        // Re-index remaining errors
        currentErrors.forEach((err, idx) => {
            err.index = idx;
        });
    }

    // Update UI
    updateBadge();
    renderHighlights();

    // Only update the panel if it was already visible
    if (!suggestionCard.classList.contains('hidden')) {
        // Animate the removal of the specific error item
        if (errorItem) {
            // Add removing class for animation
            errorItem.classList.add('removing');

            // Remove from DOM after animation completes
            setTimeout(() => {
                errorItem.remove();

                // If no errors left, show success state
                if (currentErrors.length === 0) {
                    showSuccessState();
                } else {
                    // Re-sync indices and activate the item that moved into this slot
                    const removedIdx = Number(errorItem.dataset.errorIndex || 0);
                    updatePanelIndices();
                    const nextIndex = Math.min(removedIdx, currentErrors.length - 1);
                    activatePanelItem(nextIndex);
                }
            }, 300);
        } else if (currentErrors.length === 0) {
            // If no error item found and no errors left, show success
            showSuccessState();
        } else {
            // When we don't have the DOM node, activate the first item by default
            updatePanelIndices();
            activatePanelItem(0);
        }
    }
}

function handleIgnoreError() {
    if (!currentSuggestionError) return;

    ignoredWords.add(currentSuggestionError.word);

    // Remove from current errors
    const index = currentErrors.findIndex(e => e.index === currentSuggestionError.index);
    if (index !== -1) {
        currentErrors.splice(index, 1);
    }

    updateBadge();
    renderHighlights();
    hideSuggestionCard();
}

// ===== Initialize =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
