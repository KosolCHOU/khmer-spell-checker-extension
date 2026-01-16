// Spell Checker JavaScript (v4 - clean rewrite)
document.addEventListener('DOMContentLoaded', () => {
  console.log('[Grammar] v4 script loaded');

  // ===== DOM Elements =====
  const textInput = document.getElementById('textInput');
  const pasteBtn = document.getElementById('pasteBtn');
  const fileUpload = document.getElementById('fileUpload');
  const emptyState = document.getElementById('emptyState');
  const suggestionsList = document.getElementById('suggestionsList');
  const editorEmptyState = document.getElementById('editorEmptyState');


  // ===== State =====
  const checkStatus = document.getElementById('checkStatus');

  let currentErrors = [];
  let ignoredWords = new Set();
  let activeErrorIndex = 0;
  let isProgrammaticChange = false;
  let editorEmptyTimeout = null;
  let hoveredErrorIndex = -1; // Track which error is being hovered

  // ===== Setup Highlight System =====
  // Contenteditable doesn't use the backdrop system in the same way
  // We keep the variable to prevent ReferenceError in existing logic
  const backdrop = document.createElement('div');

  // const wrapper = document.createElement('div');
  // wrapper.className = 'highlight-wrapper';
  // ... removed backdrop insert code ...

  // ===== Utility Functions =====
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function escapeAttr(str) {
    return String(str)
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function getLang() {
    return document.body.getAttribute('data-lang') || 'en';
  }

  // ===== UI Update Functions =====
  function updateCharCount() {
    const text = textInput.innerText || "";
    const chars = text.trim() === "" ? 0 : text.length;
    const lang = getLang();
    const charText = lang === 'km' ? `${chars} តួអក្សរ` : `${chars} characters`;

    // Update toolbar character count
    const toolbarCharCount = document.getElementById('toolbarCharCount');
    if (toolbarCharCount) {
      toolbarCharCount.textContent = charText;
    }
  }


  function updateEditorEmptyState() {
    if (editorEmptyState) {
      if (editorEmptyTimeout) clearTimeout(editorEmptyTimeout);

      const val = textInput.innerText || "";
      if (val.trim() === '') {
        // Force the editor to be truly empty so CSS :empty selector matches
        // Chrome/Firefox often leave <br> or whitespace which breaks :empty
        if (textInput.innerHTML !== '') {
          textInput.innerHTML = '';
        }

        editorEmptyState.style.display = 'flex';
        // Force reflow
        void editorEmptyState.offsetWidth;
        editorEmptyState.style.opacity = '1';
      } else {
        editorEmptyState.style.opacity = '0';
        editorEmptyTimeout = setTimeout(() => {
          const valNow = textInput.innerText || "";
          if (valNow.trim() !== '') {
            editorEmptyState.style.display = 'none';
          }
        }, 300);
      }
    }
  }

  function updateHighlights() {
    // Check for CSS Custom Highlight API support
    if (!CSS.highlights) return;

    // Clear existing highlights
    CSS.highlights.clear();

    const text = textInput.innerText || "";
    if (!text || currentErrors.length === 0) return;

    const segments = [];
    let wOffset = 0;

    // Helper to traverse DOM and map text nodes to linear offsets
    // This attempts to align with innerText's layout logic
    function crawl(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        const len = node.nodeValue.length;
        if (len > 0) {
          segments.push({
            node: node,
            start: wOffset,
            end: wOffset + len
          });
        }
        wOffset += len;
      } else if (node.nodeName === 'BR') {
        wOffset += 1;
      } else {
        // Elements
        const isBlock = ['DIV', 'P', 'LI', 'H1', 'H2', 'H3', 'BLOCKQUOTE'].includes(node.nodeName);

        for (const child of node.childNodes) {
          crawl(child);
        }

        if (isBlock) {
          // Assume block boundary adds a newline in innerText
          wOffset += 1;
        }
      }
    }

    crawl(textInput);

    // Distribute errors into alternating groups to prevent visual merging of adjacent errors
    const rangesOdd = [];
    const rangesEven = [];

    // Sort errors to ensure alternating pattern works for adjacent items
    const sortedErrors = [...currentErrors].sort((a, b) => a.start - b.start);

    sortedErrors.forEach((error, index) => {
      const start = error.start;
      const end = error.end;

      if (typeof start !== 'number' || typeof end !== 'number' || start >= end) return;

      // Find overlapping text segments
      for (const seg of segments) {
        const overlapStart = Math.max(start, seg.start);
        const overlapEnd = Math.min(end, seg.end);

        if (overlapStart < overlapEnd) {
          const range = new Range();
          range.setStart(seg.node, overlapStart - seg.start);
          range.setEnd(seg.node, overlapEnd - seg.start);

          if (index % 2 === 0) {
            rangesEven.push(range);
          } else {
            rangesOdd.push(range);
          }
        }
      }
    });

    if (rangesOdd.length > 0) {
      CSS.highlights.set("grammar-error-odd", new Highlight(...rangesOdd));
    } else {
      CSS.highlights.delete("grammar-error-odd");
    }

    if (rangesEven.length > 0) {
      CSS.highlights.set("grammar-error-even", new Highlight(...rangesEven));
    } else {
      CSS.highlights.delete("grammar-error-even");
    }
  }

  // Enhanced hover/touch interaction system
  function updateHoverHighlight(errorIndex) {
    if (!CSS.highlights) return;

    if (errorIndex === -1 || errorIndex >= currentErrors.length) {
      // Clear hover highlight
      CSS.highlights.delete("grammar-error-hover");
      textInput.style.cursor = 'text';
      return;
    }

    const error = currentErrors[errorIndex];
    if (!error) return;

    // Create hover highlight for the specific error
    const text = textInput.innerText || "";
    const segments = [];
    let wOffset = 0;

    function crawl(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        const len = node.nodeValue.length;
        if (len > 0) {
          segments.push({ node: node, start: wOffset, end: wOffset + len });
        }
        wOffset += len;
      } else if (node.nodeName === 'BR') {
        wOffset += 1;
      } else {
        const isBlock = ['DIV', 'P', 'LI', 'H1', 'H2', 'H3', 'BLOCKQUOTE'].includes(node.nodeName);
        for (const child of node.childNodes) {
          crawl(child);
        }
        if (isBlock) wOffset += 1;
      }
    }

    crawl(textInput);

    const ranges = [];
    const start = error.start;
    const end = error.end;

    if (typeof start === 'number' && typeof end === 'number' && start < end) {
      for (const seg of segments) {
        const overlapStart = Math.max(start, seg.start);
        const overlapEnd = Math.min(end, seg.end);
        if (overlapStart < overlapEnd) {
          const range = new Range();
          range.setStart(seg.node, overlapStart - seg.start);
          range.setEnd(seg.node, overlapEnd - seg.start);
          ranges.push(range);
        }
      }
    }

    if (ranges.length > 0) {
      CSS.highlights.set("grammar-error-hover", new Highlight(...ranges));
      textInput.style.cursor = 'pointer';
    } else {
      CSS.highlights.delete("grammar-error-hover");
      textInput.style.cursor = 'text';
    }
  }

  function findErrorAtPosition(x, y) {
    const range = document.caretRangeFromPoint(x, y);
    if (!range) return -1;

    const text = textInput.innerText || "";
    let offset = 0;

    function getOffset(node, targetNode, targetOffset) {
      if (node === targetNode) return offset + targetOffset;

      if (node.nodeType === Node.TEXT_NODE) {
        offset += node.nodeValue.length;
      } else if (node.nodeName === 'BR') {
        offset += 1;
      } else {
        for (const child of node.childNodes) {
          const result = getOffset(child, targetNode, targetOffset);
          if (result !== -1) return result;
        }
      }
      return -1;
    }

    const clickOffset = getOffset(textInput, range.startContainer, range.startOffset);
    if (clickOffset === -1) return -1;

    // Find which error contains this offset
    for (let i = 0; i < currentErrors.length; i++) {
      const error = currentErrors[i];
      if (clickOffset >= error.start && clickOffset < error.end) {
        return i;
      }
    }

    return -1;
  }

  // Mouse hover handlers
  textInput.addEventListener('mousemove', (e) => {
    const errorIndex = findErrorAtPosition(e.clientX, e.clientY);
    if (errorIndex !== hoveredErrorIndex) {
      hoveredErrorIndex = errorIndex;
      updateHoverHighlight(errorIndex);
    }
  });

  textInput.addEventListener('mouseleave', () => {
    hoveredErrorIndex = -1;
    updateHoverHighlight(-1);
  });

  // Touch handlers for mobile
  textInput.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      const errorIndex = findErrorAtPosition(touch.clientX, touch.clientY);
      if (errorIndex !== -1) {
        hoveredErrorIndex = errorIndex;
        updateHoverHighlight(errorIndex);
        // Activate suggestion after a brief delay
        setTimeout(() => {
          if (hoveredErrorIndex === errorIndex) {
            activateSuggestion(errorIndex);
          }
        }, 150);
      }
    }
  });

  textInput.addEventListener('touchend', () => {
    // Keep hover highlight briefly after touch
    setTimeout(() => {
      hoveredErrorIndex = -1;
      updateHoverHighlight(-1);
    }, 300);
  });

  // Click handler to activate suggestions
  textInput.addEventListener('click', (e) => {
    const errorIndex = findErrorAtPosition(e.clientX, e.clientY);
    if (errorIndex !== -1) {
      activateSuggestion(errorIndex);
    }
  });


  function showEmptyState(type = 'default') {
    const lang = getLang();
    emptyState.classList.remove('hidden');
    suggestionsList.classList.add('hidden');



    if (type === 'success') {
      emptyState.innerHTML = `
        <div class="mb-4 relative">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-green-500/10 to-emerald-400/10 flex items-center justify-center backdrop-blur-sm border border-green-500/20">
            <svg class="w-8 h-8 text-green-400/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <h3 class="text-sm font-semibold text-green-400 mb-1">
          ${lang === 'km' ? 'អបអរសាទរ!' : 'Great Work!'}
        </h3>
        <p class="text-slate-400 text-xs leading-relaxed">
          ${lang === 'km' ? 'រកមិនឃើញកំហុស' : 'No errors found'}
        </p>
      `;
    } else if (type === 'allclear') {
      emptyState.innerHTML = `
        <div class="mb-4 relative">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-green-500/10 to-emerald-400/10 flex items-center justify-center backdrop-blur-sm border border-green-500/20">
            <svg class="w-8 h-8 text-green-400/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
        </div>
        <h3 class="text-sm font-semibold text-green-400 mb-1">
          ${lang === 'km' ? 'ល្អឥតខ្ចោះ!' : 'All Clear!'}
        </h3>
        <p class="text-slate-400 text-xs leading-relaxed">
          ${lang === 'km' ? 'គ្មានបញ្ហានៅសល់' : 'No issues remaining'}
        </p>
      `;
    } else {
      emptyState.innerHTML = `
        <div class="mb-4 relative">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-cyan-500/10 to-lime-400/10 flex items-center justify-center backdrop-blur-sm border border-cyan-500/20">
            <svg class="w-8 h-8 text-cyan-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
        </div>
        <h3 class="text-sm font-semibold text-slate-300 mb-1">
          ${lang === 'km' ? 'ចាប់ផ្តើមពិនិត្យ' : 'Start Checking'}
        </h3>
        <p class="text-slate-400 text-xs leading-relaxed">
          ${lang === 'km' ? 'វាយ ឬបិតអត្ថបទរបស់អ្នក' : 'Type or paste your text'}
        </p>
      `;
    }
  }

  function showSuggestions() {
    if (currentErrors.length === 0) {
      showEmptyState('success');
      updateHighlights();
      return;
    }

    emptyState.classList.add('hidden');
    suggestionsList.classList.remove('hidden');

    suggestionsList.innerHTML = '';

    // Ensure activeErrorIndex is within bounds
    if (activeErrorIndex >= currentErrors.length) {
      activeErrorIndex = Math.max(0, currentErrors.length - 1);
    }

    currentErrors.forEach((error, index) => {
      const isActive = index === activeErrorIndex;
      const div = document.createElement('div');
      div.className = `suggestion-item error cursor-pointer ${isActive ? 'active' : ''}`;
      div.setAttribute('data-error-index', index);

      // Determine invalid suggestion visibility
      const visibilityClass = isActive ? '' : 'hidden';

      div.innerHTML = `
        <div class="flex items-start justify-between mb-2">
          <span class="error-word">${escapeHtml(error.word)}</span>
          <div class="flex gap-2">
            <button class="ignore-btn font-bold text-slate-400 hover:text-white transition-colors" data-error-index="${index}">Ignore</button>
          </div>
        </div>
        <div class="suggestions-container ${visibilityClass}">
          <p class="text-xs text-slate-400 mb-3">Suggested correction</p>
          <div class="flex flex-wrap gap-1">
            ${error.suggestions.map(s =>
        `<button type="button" class="suggestion-word" data-error-index="${index}" data-suggestion="${escapeAttr(s)}">${escapeHtml(s)}</button>`
      ).join('')}
          </div>
        </div>
      `;
      suggestionsList.appendChild(div);
    });

    // Ensure the list scrolls to the top to show the first error
    suggestionsList.scrollTop = 0;

    updateHighlights();
  }

  function resetAll() {
    currentErrors = [];

    ignoredWords.clear();
    showEmptyState('default');
    updateHighlights();
    updateEditorEmptyState();
  }

  function setCheckingStatus(isChecking) {
    if (isChecking) {
      if (checkStatus) checkStatus.classList.remove('opacity-0');
      const lang = getLang();
      if (checkStatus) checkStatus.textContent = lang === 'km' ? 'កំពុងពិនិត្យ...' : 'Checking...';
    } else {
      if (checkStatus) checkStatus.classList.add('opacity-0');
    }
  }

  // ===== API Call =====
  async function checkGrammar() {
    const text = (textInput.innerText || "").trim();
    if (!text) {
      resetAll();
      return;
    }

    setCheckingStatus(true);
    // Don't disable input, just show status

    try {
      const response = await fetch('/api/spell-check/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      const data = await response.json();
      console.log('[Grammar] API response:', data);

      if (!data.success) {
        throw new Error(data.error || 'API error');
      }

      // Cleanup ignoredWords: if a word is no longer returned as an error, remove it from the ignore list.
      // This handles the case where a user modifies an ignored word (making it a "new" word/error or fixing it).
      // If it's not in the current error list, we shouldn't be holding onto it as ignored.
      // Cleanup ignoredWords: if a word is no longer returned as an error, remove it from the ignore list.
      const allFoundErrors = new Set(Object.values(data.errors || {}).map(e => e.original));
      for (const word of ignoredWords) {
        if (!allFoundErrors.has(word)) {
          ignoredWords.delete(word);
        }
      }

      // Calculate token offsets for precise positioning
      const tokens = data.tokens || [];
      let cursor = 0;
      const tokenOffsets = tokens.map(t => {
        const current = cursor;
        cursor += t.length;
        return current;
      });

      // Map errors with positions
      currentErrors = [];
      const errorEntries = Object.entries(data.errors || {});

      // Calculate offset due to trimming
      // The API analyzes 'text' which is trimmed. 
      // We need to map back to 'textInput.value' which may have leading whitespace.
      const rawText = textInput.innerText || "";
      const match = rawText.match(/^\s*/);
      const leadingOffset = match ? match[0].length : 0;

      for (const [key, info] of errorEntries) {
        const idx = parseInt(key, 10);
        const start = tokenOffsets[idx];

        if (start !== undefined && !ignoredWords.has(info.original)) {
          // Adjust position by adding leading whitespace offset
          const adjustStart = start + leadingOffset;
          const adjustEnd = adjustStart + info.original.length;

          currentErrors.push({
            word: info.original,
            suggestions: info.suggestions || [],
            start: adjustStart,
            end: adjustEnd
          });
        }
      }

      // Sort errors by their position in the text
      currentErrors.sort((a, b) => a.start - b.start);

      showSuggestions();

    } catch (err) {
      console.error('[Grammar] Error:', err);
      // Fail silently on auto-check errors to avoid annoying alerts while typing
      // maybe just log it
    } finally {
      setCheckingStatus(false);
    }
  }

  // Create debounced version
  const debouncedCheckGrammar = debounce(checkGrammar, 500);

  // ===== Apply Actions =====
  async function applySuggestion(errorIndex, suggestion) {
    const error = currentErrors[errorIndex];
    if (!error) return;

    if (typeof error.start !== 'number' || typeof error.end !== 'number') {
      console.warn("Missing error position for suggestion application");
      return;
    }

    const lengthDiff = suggestion.length - error.word.length;

    // 1. Find DOM Range for the error (matching updateHighlights crawler logic)
    const start = error.start;
    const end = error.end;
    let current = 0;
    const range = document.createRange();
    let startFound = false;
    let endFound = false;

    function walk(node) {
      if (startFound && endFound) return;
      if (node.nodeType === Node.TEXT_NODE) {
        const len = node.length;
        if (!startFound && current + len >= start) {
          range.setStart(node, start - current);
          startFound = true;
        }
        if (!endFound && current + len >= end) {
          range.setEnd(node, end - current);
          endFound = true;
        }
        current += len;
      } else if (node.nodeName === 'BR') {
        current += 1;
      } else {
        const isBlock = ['DIV', 'P', 'LI', 'H1', 'H2', 'H3', 'BLOCKQUOTE'].includes(node.nodeName);
        for (const child of node.childNodes) {
          walk(child);
        }
        if (isBlock) current += 1;
      }
    }
    walk(textInput);

    // 2. Execute Replacement
    if (startFound && endFound) {
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      // Prevent auto-recheck during programmatic insertion
      isProgrammaticChange = true;
      // Using execCommand ensures the change is added to the Undo stack
      document.execCommand('insertText', false, suggestion);
      // Reset flag after the current event loop to allow manual edits again
      setTimeout(() => { isProgrammaticChange = false; }, 100);
    } else {
      console.warn("Could not locate error range in DOM");
      return;
    }

    updateCharCount();

    // Client-side update: Remove fixed error and shift subsequent errors
    const fixedEnd = error.end;

    // Remove the applied error
    const newErrors = [];
    currentErrors.forEach((e, idx) => {
      if (idx === errorIndex) return; // Skip the fixed one

      // If this error is AFTER the fixed one, shift its position
      if (typeof e.start === 'number' && typeof e.end === 'number' && e.start > error.start) {
        e.start += lengthDiff;
        e.end += lengthDiff;
      }
      newErrors.push(e);
    });

    currentErrors = newErrors;

    // Smooth removal: animate out the item, then remove only that item
    const itemToRemove = suggestionsList.querySelector(`[data-error-index="${errorIndex}"]`);
    if (itemToRemove) {
      itemToRemove.classList.add('removing');

      // Wait for animation to complete, then remove only this item
      setTimeout(() => {
        itemToRemove.remove();

        // Update the remaining items' indices
        const remainingItems = suggestionsList.querySelectorAll('.suggestion-item');
        remainingItems.forEach((item, index) => {
          item.setAttribute('data-error-index', index);
          // Update all buttons within the item
          item.querySelectorAll('[data-error-index]').forEach(btn => {
            btn.setAttribute('data-error-index', index);
          });
        });

        updateHighlights();

        // Only show empty state if no errors remain
        if (currentErrors.length === 0) {
          showEmptyState('success');
        } else {
          // Activate the next error in sequence
          // If we fixed error at index N, the next error is now at index N (since we removed one)
          // Unless we fixed the last error, then activate the new last one
          const nextIndex = Math.min(errorIndex, currentErrors.length - 1);
          activateSuggestion(nextIndex);
        }
      }, 300); // Match the slideOut animation duration
    } else {
      // Fallback if item not found
      updateHighlights();
      if (currentErrors.length === 0) {
        showEmptyState('success');
      } else {
        showSuggestions();
      }
    }
  }

  function applyIgnore(errorIndex) {
    const error = currentErrors[errorIndex];
    if (error && error.word) {
      ignoredWords.add(error.word);
    }

    // Remove the error from list
    currentErrors.splice(errorIndex, 1);

    // Smooth removal: animate out the item, then remove only that item
    const itemToRemove = suggestionsList.querySelector(`[data-error-index="${errorIndex}"]`);
    if (itemToRemove) {
      itemToRemove.classList.add('removing');

      // Wait for animation to complete, then remove only this item
      setTimeout(() => {
        itemToRemove.remove();

        // Update the remaining items' indices
        const remainingItems = suggestionsList.querySelectorAll('.suggestion-item');
        remainingItems.forEach((item, index) => {
          item.setAttribute('data-error-index', index);
          // Update all buttons within the item
          item.querySelectorAll('[data-error-index]').forEach(btn => {
            btn.setAttribute('data-error-index', index);
          });
        });

        updateHighlights();

        // Only show empty state if no errors remain
        if (currentErrors.length === 0) {
          showEmptyState('success');
        } else {
          // Activate the next error in sequence
          const nextIndex = Math.min(errorIndex, currentErrors.length - 1);
          activateSuggestion(nextIndex);
        }
      }, 300); // Match the slideOut animation duration
    } else {
      // Fallback if item not found
      updateHighlights();
      if (currentErrors.length === 0) {
        showEmptyState('success');
      } else {
        showSuggestions();
      }
    }
  }

  // Helper to activate a suggestion card
  function activateSuggestion(index) {
    activeErrorIndex = index;
    const allItems = suggestionsList.querySelectorAll('.suggestion-item');
    allItems.forEach(el => {
      const itemIndex = parseInt(el.getAttribute('data-error-index'), 10);
      const container = el.querySelector('.suggestions-container');

      if (itemIndex === index) {
        el.classList.add('active');
        if (container) container.classList.remove('hidden');

        // Scroll into view if needed - prioritize showing at the top
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        el.classList.remove('active');
        if (container) container.classList.add('hidden');
      }
    });
  }

  // ===== Event Listeners =====

  // Suggestion click (using event delegation)
  suggestionsList.addEventListener('click', async (e) => {
    // Handle suggestion word button click
    const btn = e.target.closest('.suggestion-word');
    if (btn) {
      e.stopPropagation(); // Prevent triggering the card click
      const errorIndex = parseInt(btn.getAttribute('data-error-index'), 10);
      const suggestion = btn.getAttribute('data-suggestion');
      await applySuggestion(errorIndex, suggestion);
      return;
    }

    // Handle ignore button click
    const ignoreBtn = e.target.closest('.ignore-btn');
    if (ignoreBtn) {
      e.stopPropagation(); // Prevent triggering the card click
      const errorIndex = parseInt(ignoreBtn.getAttribute('data-error-index'), 10);
      applyIgnore(errorIndex);
      return;
    }

  });

  // Handle card navigation and accordion behavior on mousedown
  // Helper to interpret cursor position in contenteditable
  function getCursorIndex() {
    const sel = window.getSelection();
    if (!sel.rangeCount || !textInput.contains(sel.anchorNode)) return 0;
    const range = sel.getRangeAt(0);
    const preRange = range.cloneRange();
    preRange.selectNodeContents(textInput);
    preRange.setEnd(range.startContainer, range.startOffset);
    const str = preRange.toString();
    // Approximate newline count from blocks/br
    const frag = preRange.cloneContents();
    const nl = frag.querySelectorAll('div, p, br, li, h1, h2, h3').length;
    return str.length + nl;
  }

  // Helper to set cursor position
  function setCursorIndex(targetIndex) {
    let current = 0;
    let found = false;

    // Recursive walk to find position
    function walk(node) {
      if (found) return;
      if (node.nodeType === Node.TEXT_NODE) {
        const len = node.nodeValue.length;
        if (current + len >= targetIndex) {
          const range = document.createRange();
          range.setStart(node, targetIndex - current);
          range.collapse(true);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          found = true;
          return;
        }
        current += len;
      } else if (node.nodeName === 'BR') {
        current += 1;
      } else {
        const isBlock = ['DIV', 'P', 'LI', 'H1', 'H2', 'H3'].includes(node.nodeName);
        for (const child of node.childNodes) {
          walk(child);
          if (found) return;
        }
        if (isBlock) current += 1;
      }
    }
    walk(textInput);
    textInput.focus();
  }

  // Handle card navigation and accordion behavior on mousedown
  suggestionsList.addEventListener('mousedown', (e) => {
    // 1. Ignore if clicking buttons (buttons handle their own clicks, or we let click bubble)
    if (e.target.closest('button') || e.target.closest('.suggestion-word') || e.target.closest('.ignore-btn')) {
      return;
    }

    // 2. Handle card click (navigation + accordion)
    const item = e.target.closest('.suggestion-item.error');
    if (item) {
      // Prevent default to stop input from losing focus
      e.preventDefault();

      const errorIndex = parseInt(item.getAttribute('data-error-index'), 10);

      // Activate this item
      activateSuggestion(errorIndex);

      // --- Navigation Logic ---
      const error = currentErrors[errorIndex];

      if (error && typeof error.start === 'number' && typeof error.end === 'number') {
        setCursorIndex(error.end);
      }
    }
  });

  // Handle cursor positioning to activate suggestions
  const handleCursorActivity = () => {
    const cursor = getCursorIndex();

    // Find error at cursor
    const errorIndex = currentErrors.findIndex(e => {
      if (typeof e.start !== 'number' || typeof e.end !== 'number') return false;
      // Check if cursor is within [start, end]
      return cursor >= e.start && cursor <= e.end;
    });

    if (errorIndex !== -1) {
      activateSuggestion(errorIndex);
    }
  };

  textInput.addEventListener('click', handleCursorActivity);
  textInput.addEventListener('keyup', (e) => {
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'].includes(e.key)) {
      handleCursorActivity();
    }
  });

  // ===== Transliteration & Latin-to-Khmer Popup =====
  let translitPopup = null;
  let currentTranslitCandidates = [];
  let activeTranslitIndex = 0;
  let lastLatinWordRange = null; // Store range of the word being typed

  function closeTranslitPopup() {
    if (translitPopup) {
      translitPopup.remove();
      translitPopup = null;
    }
    currentTranslitCandidates = [];
    activeTranslitIndex = 0;
    lastLatinWordRange = null;
  }

  async function updateTransliteration(text) {
    if (!text) {
      closeTranslitPopup();
      return;
    }

    try {
      const response = await fetch('/transliterate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.candidates && data.candidates.length > 0) {
        // Use 3 candidates max as requested
        let candidates = data.candidates.slice(0, 3);

        // Reorder logic: API returns [2nd, Best, 3rd... center weighted in original design]
        // User wants Best on Left -> [Best, 2nd, 3rd...]
        if (candidates.length >= 2) {
          const best = candidates[1];
          candidates.splice(1, 1);
          candidates.unshift(best);
        }

        currentTranslitCandidates = candidates;
        activeTranslitIndex = 0; // Default to first (best)
        showTranslitPopup();
      } else {
        // console.log('Transliteration returned no candidates');
        closeTranslitPopup();
      }
    } catch (e) {
      console.error('Transliteration error:', e);
      closeTranslitPopup();
    }
  }

  // Debounced version for API calls
  const debouncedTransliterate = debounce((text) => updateTransliteration(text), 150);

  function showTranslitPopup() {
    if (!lastLatinWordRange) return;

    // Check theme for dynamic styling
    const isLight = document.body.getAttribute('data-theme') === 'light';
    const bgClass = isLight ? '!bg-white/95 !border-slate-200' : '!bg-slate-900 !border-slate-800';
    const inactiveTextClass = isLight ? 'text-slate-500' : 'text-slate-400';

    if (!translitPopup) {
      translitPopup = document.createElement('div');
      document.body.appendChild(translitPopup);
    }

    // Update base classes for theme
    translitPopup.className = `inline-popup translit-popup !p-1 !overflow-hidden !shadow-2xl !rounded-full border backdrop-blur-sm !min-w-0 !w-auto ${bgClass}`;

    // Ensure structure exists
    if (!translitPopup.querySelector('.translit-track')) {
      translitPopup.innerHTML = `
        <div class="relative flex items-center h-10 translit-track">
           <div id="translitHighlight" class="absolute top-0 bottom-0 my-auto h-full bg-cyan-500 rounded-full shadow-md transition-all duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]"></div>
           <div id="translitButtons" class="relative z-10 flex h-full"></div>
        </div>
      `;
    }

    const highlight = translitPopup.querySelector('#translitHighlight');
    const btnContainer = translitPopup.querySelector('#translitButtons');

    // Render buttons
    btnContainer.innerHTML = currentTranslitCandidates.map((s, i) => {
      return `<button type="button" 
                class="translit-btn flex items-center justify-center px-4 min-w-[3rem] h-full text-base font-normal transition-colors duration-200 outline-none" 
                data-idx="${i}">
                <span class="relative z-20 pb-1">${escapeHtml(s)}</span>
              </button>`;
    }).join('');

    // Update active state visuals and add click handlers
    const buttons = btnContainer.querySelectorAll('.translit-btn');
    buttons.forEach((btn, i) => {
      const base = 'translit-btn flex items-center justify-center px-4 min-w-[3rem] h-full text-base font-normal transition-colors duration-200 outline-none';
      if (i === activeTranslitIndex) {
        btn.className = `${base} text-white font-semibold`;
      } else {
        btn.className = `${base} ${inactiveTextClass}`;
      }

      // Add click handler for each button
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const candidate = currentTranslitCandidates[i];
        if (candidate) {
          applyTransliteration(candidate);
        }
      });

      // Also add touch handler for better mobile support
      btn.addEventListener('touchend', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const candidate = currentTranslitCandidates[i];
        if (candidate) {
          applyTransliteration(candidate);
        }
      });
    });

    // Move highlight
    const activeBtn = buttons[activeTranslitIndex];
    if (activeBtn) {
      highlight.style.left = activeBtn.offsetLeft + 'px';
      highlight.style.width = activeBtn.offsetWidth + 'px';
    }

    // Position Popup
    const rect = lastLatinWordRange.getBoundingClientRect();
    const popupRect = translitPopup.getBoundingClientRect();

    // Position below the word
    let top = rect.bottom + window.scrollY + 8;
    // Align left with the word start instead of centering to avoid floating left
    let left = rect.left + window.scrollX;

    // Keep within viewport
    const padding = 10;
    if (left < padding) left = padding;
    if (left + popupRect.width > window.innerWidth - padding) {
      left = window.innerWidth - popupRect.width - padding;
    }

    translitPopup.style.top = `${top}px`;
    translitPopup.style.left = `${left}px`;
  }

  function applyTransliteration(candidate) {
    if (!lastLatinWordRange || !candidate) return;

    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(lastLatinWordRange);

    // Programmatic change flag to skip grammar check loop
    isProgrammaticChange = true;

    // Insert text (with a trailing space common for typing flow?)
    // Converting functionality from social demo: remove space, let user type it?
    // Social demo logic: `fbInput.value = (val + text).trim();`
    // Here we replace the word exactly.
    document.execCommand('insertText', false, candidate);

    // Reset
    closeTranslitPopup();

    // Reset flag later
    setTimeout(() => { isProgrammaticChange = false; }, 100);
  }

  // Handle typing input for detection
  textInput.addEventListener('input', (e) => {
    // Skip if we just did a programmatic change (like inserting the replacement)
    if (isProgrammaticChange) return;

    const sel = window.getSelection();
    if (!sel.isCollapsed) {
      closeTranslitPopup();
      return;
    }

    const anchorNode = sel.anchorNode;
    // Only care about text nodes
    if (anchorNode.nodeType !== Node.TEXT_NODE) {
      closeTranslitPopup();
      return;
    }

    const text = anchorNode.textContent;
    const offset = sel.anchorOffset;

    // Find the Latin word being typed (look back from cursor as long as it's Latin)
    // We change from /\S/ (non-whitespace) to /[a-zA-Z]/ so we stop at Khmer characters
    // This allows typing "KhmerWordLatinInput" and correctly extracting "LatinInput"
    let start = offset;
    while (start > 0 && /[a-zA-Z]/.test(text[start - 1])) {
      start--;
    }

    const word = text.slice(start, offset);

    // Check if word is valid Latin (SingKhmer)
    // Regex: Starts with Latin letter, contains only Latin letters/symbols allowed in transliteration
    if (word && /^[a-zA-Z]+$/.test(word)) {
      // It's a candidate for transliteration
      currentLatinWord = word;

      // Save range for positioning and replacement
      const range = document.createRange();
      range.setStart(anchorNode, start);
      range.setEnd(anchorNode, offset);
      lastLatinWordRange = range;

      debouncedTransliterate(word);
    } else {
      closeTranslitPopup();
    }
  });

  // Handle keys for navigation/selection
  textInput.addEventListener('keydown', (e) => {
    if (!translitPopup || currentTranslitCandidates.length === 0) return;

    // Number selection 1-3
    if (/^[1-3]$/.test(e.key)) {
      e.preventDefault();
      const idx = parseInt(e.key) - 1;
      if (currentTranslitCandidates[idx]) {
        applyTransliteration(currentTranslitCandidates[idx]);
      }
      return;
    }

    // Navigation
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      activeTranslitIndex = (activeTranslitIndex + 1) % currentTranslitCandidates.length;
      showTranslitPopup();
      return;
    }

    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      activeTranslitIndex = (activeTranslitIndex - 1 + currentTranslitCandidates.length) % currentTranslitCandidates.length;
      showTranslitPopup();
      return;
    }

    // Selection
    if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault(); // Stop newline/tab
      applyTransliteration(currentTranslitCandidates[activeTranslitIndex]);
      return;
    }

    // Space: usually commits the word as is OR commits the top candidate.
    // In many IMEs, Space commits the selected candidate.
    // Let's implement Space commits selection to be smooth
    if (e.key === ' ') {
      // Prevent default space insertion, insert candidate + space
      e.preventDefault();
      applyTransliteration(currentTranslitCandidates[activeTranslitIndex] + ' ');
      return;
    }

    // Escape to dismiss
    if (e.key === 'Escape') {
      closeTranslitPopup();
      return;
    }
  });


  // ===== INLINE POPUP FOR MOBILE =====
  let inlinePopup = null;
  let currentPopupErrorIndex = -1;

  function isMobileView() {
    return window.innerWidth < 1024;
  }

  function closeInlinePopup() {
    if (inlinePopup) {
      inlinePopup.classList.add('closing');
      setTimeout(() => {
        if (inlinePopup && inlinePopup.parentNode) {
          inlinePopup.remove();
        }
        inlinePopup = null;
        currentPopupErrorIndex = -1;
      }, 150);
    }
  }

  function showInlinePopup(errorIndex, clickEvent) {
    // Close any existing popup
    closeInlinePopup();

    const error = currentErrors[errorIndex];
    if (!error) return;

    currentPopupErrorIndex = errorIndex;

    // Create popup element
    const popup = document.createElement('div');
    popup.className = 'inline-popup';

    const lang = getLang();
    const suggestionsLabel = lang === 'km' ? 'ការណែនាំ' : 'Suggested correction';
    const ignoreLabel = lang === 'km' ? 'មិនអើពើ' : 'Ignore';

    popup.innerHTML = `
      <div class="flex items-start justify-between mb-2">
        <span class="error-word">${escapeHtml(error.word)}</span>
        <button class="ignore-btn inline-popup-ignore" data-error-index="${errorIndex}">${ignoreLabel}</button>
      </div>
      <div class="suggestions-container">
        <p class="text-xs text-slate-400 mb-3">${suggestionsLabel}</p>
        <div class="flex flex-wrap gap-1">
          ${error.suggestions.map(s =>
      `<button type="button" class="suggestion-word inline-popup-suggestion" data-error-index="${errorIndex}" data-suggestion="${escapeAttr(s)}">${escapeHtml(s)}</button>`
    ).join('')}
        </div>
      </div>
    `;

    // Position the popup
    document.body.appendChild(popup);
    inlinePopup = popup;

    // Get the position of the clicked error
    const range = document.createRange();
    let current = 0;
    let found = false;

    function walk(node) {
      if (found) return;
      if (node.nodeType === Node.TEXT_NODE) {
        const len = node.length;
        if (current + len >= error.start && !found) {
          range.setStart(node, Math.max(0, error.start - current));
          range.setEnd(node, Math.min(len, error.end - current));
          found = true;
          return;
        }
        current += len;
      } else if (node.nodeName === 'BR') {
        current += 1;
      } else {
        const isBlock = ['DIV', 'P', 'LI', 'H1', 'H2', 'H3', 'BLOCKQUOTE'].includes(node.nodeName);
        for (const child of node.childNodes) {
          walk(child);
          if (found) return;
        }
        if (isBlock) current += 1;
      }
    }
    walk(textInput);

    if (found) {
      const rect = range.getBoundingClientRect();
      const popupRect = popup.getBoundingClientRect();

      // Position above the error word
      let top = rect.top + window.scrollY - popupRect.height - 12;
      let left = rect.left + window.scrollX + (rect.width / 2) - (popupRect.width / 2);

      // Keep popup within viewport
      const padding = 10;
      if (left < padding) left = padding;
      if (left + popupRect.width > window.innerWidth - padding) {
        left = window.innerWidth - popupRect.width - padding;
      }

      // If popup would go above viewport, show it below instead
      if (top < padding) {
        top = rect.bottom + window.scrollY + 12;
        // Flip arrow to bottom
        popup.style.setProperty('--arrow-position', 'bottom');
      }

      popup.style.top = `${top}px`;
      popup.style.left = `${left}px`;
    }

    // Add event listeners for popup buttons
    popup.addEventListener('click', async (e) => {
      e.stopPropagation();

      const suggestionBtn = e.target.closest('.inline-popup-suggestion');
      if (suggestionBtn) {
        const idx = parseInt(suggestionBtn.getAttribute('data-error-index'), 10);
        const suggestion = suggestionBtn.getAttribute('data-suggestion');
        closeInlinePopup();
        await applySuggestion(idx, suggestion);
        return;
      }

      const ignoreBtn = e.target.closest('.inline-popup-ignore');
      if (ignoreBtn) {
        const idx = parseInt(ignoreBtn.getAttribute('data-error-index'), 10);
        closeInlinePopup();
        applyIgnore(idx);
        return;
      }
    });
  }

  // Click handler for error highlights on mobile
  textInput.addEventListener('click', (e) => {
    if (!isMobileView()) return;

    const cursor = getCursorIndex();
    const errorIndex = currentErrors.findIndex(err => {
      if (typeof err.start !== 'number' || typeof err.end !== 'number') return false;
      return cursor >= err.start && cursor <= err.end;
    });

    if (errorIndex !== -1) {
      e.preventDefault();
      e.stopPropagation();
      showInlinePopup(errorIndex, e);
    }
  });

  // Close popup when clicking outside
  document.addEventListener('click', (e) => {
    if (!isMobileView()) return;
    if (inlinePopup && !inlinePopup.contains(e.target) && !textInput.contains(e.target)) {
      closeInlinePopup();
    }
  });

  // Close popup on window resize if switching to desktop view
  window.addEventListener('resize', () => {
    if (!isMobileView() && inlinePopup) {
      closeInlinePopup();
    }
  });



  // Paste event to normalize pasted content
  textInput.addEventListener('paste', (e) => {
    e.preventDefault();

    // Get plain text from clipboard
    const text = (e.clipboardData || window.clipboardData).getData('text/plain');

    // Get current selection
    const selection = window.getSelection();
    if (!selection.rangeCount) return;

    // Delete current selection if any
    selection.deleteFromDocument();

    // Create a text node with plain text (no formatting)
    const textNode = document.createTextNode(text);

    // Insert the text node at cursor position
    const range = selection.getRangeAt(0);
    range.insertNode(textNode);

    // Move cursor to end of inserted text
    range.setStartAfter(textNode);
    range.setEndAfter(textNode);
    selection.removeAllRanges();
    selection.addRange(range);

    // Trigger input event manually since we prevented default
    textInput.dispatchEvent(new Event('input', { bubbles: true }));
  });

  // Text input events
  textInput.addEventListener('input', () => {
    updateEditorEmptyState();
    updateCharCount();
    updateHighlights();
    // Auto-check grammar only if it's a manual edit
    if (!isProgrammaticChange) {
      debouncedCheckGrammar();
    }
  });



  // Paste button
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      textInput.innerText = text;
      updateEditorEmptyState();
      updateCharCount();
      updateHighlights();
      // Trigger check immediately
      await checkGrammar();
    } catch (err) {
      console.warn('Clipboard read failed, focusing input instead:', err);
      textInput.focus();
    }
  });

  // File upload
  fileUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const lang = getLang();
    const fileName = file.name.toLowerCase();

    // Handle .txt files directly in the browser
    if (fileName.endsWith('.txt')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        textInput.innerText = event.target.result;
        updateEditorEmptyState();
        updateCharCount();
        updateHighlights();
      };
      reader.readAsText(file);
      return;
    }

    // For .docx, .pdf, and .doc files, send to backend
    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    textInput.disabled = true;
    textInput.placeholder = lang === 'km' ? 'កំពុងដកស្រង់អត្ថបទ...' : 'Extracting text...';

    try {
      const response = await fetch('/api/extract-file-text/', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success && data.text) {
        textInput.innerText = data.text;
        updateCharCount();
        updateEditorEmptyState();
        updateHighlights();
        // Trigger check immediately
        await checkGrammar();
      } else {
        const errorMsg = data.error || 'Failed to extract text from file';
        alert(errorMsg);
      }
    } catch (err) {
      console.error('File extraction error:', err);
      alert(lang === 'km'
        ? 'មានបញ្ហាក្នុងការដកស្រង់អត្ថបទពីឯកសារ។'
        : 'Error extracting text from file.');
    } finally {
      // Restore input state
      textInput.disabled = false;
      const placeholder = textInput.getAttribute(`data-placeholder-${lang}`);
      if (placeholder) {
        textInput.placeholder = placeholder;
      }
      // Clear file input so same file can be selected again
      fileUpload.value = '';
    }
  });


  // Language change observer
  const langObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.attributeName === 'data-lang') {
        const lang = getLang();
        const placeholder = textInput.getAttribute(`data-placeholder-${lang}`);
        if (placeholder) {
          textInput.placeholder = placeholder;
        }
        updateCharCount();
      }
    }
  });

  langObserver.observe(document.body, {
    attributes: true,
    attributeFilter: ['data-lang']
  });

  // ===== Initialize =====
  updateCharCount();
  updateEditorEmptyState();
  updateHighlights();

  console.log('[Grammar] v4 initialized');

  // ===== Toolbar Button Functionality (Integrated) =====

  // Copy button
  const copyBtnToolbar = document.querySelector('[data-action="copy"]');
  if (copyBtnToolbar) {
    copyBtnToolbar.addEventListener('click', async () => {
      if (textInput && textInput.innerText) {
        try {
          await navigator.clipboard.writeText(textInput.innerText);
          // Visual feedback
          copyBtnToolbar.classList.add('active');
          setTimeout(() => copyBtnToolbar.classList.remove('active'), 200);
        } catch (err) {
          console.error('Failed to copy:', err);
        }
      }
    });
  }

  // Fullscreen button
  const fullscreenBtnToolbar = document.querySelector('[data-action="fullscreen"]');
  if (fullscreenBtnToolbar) {
    fullscreenBtnToolbar.addEventListener('click', () => {
      if (textInput) {
        if (!document.fullscreenElement) {
          textInput.requestFullscreen().catch(err => {
            console.error('Fullscreen error:', err);
          });
        } else {
          document.exitFullscreen();
        }
      }
    });
  }

  // Format execution function
  function execFormat(command, value = null) {
    if (!textInput) return;
    textInput.focus();

    // Prevent auto-recheck during formatting
    isProgrammaticChange = true;
    document.execCommand(command, false, value);

    // Trigger input event to update char count and highlights, 
    // but the flag will block the API check
    textInput.dispatchEvent(new Event('input', { bubbles: true }));

    // Reset flag
    setTimeout(() => { isProgrammaticChange = false; }, 100);
  }

  // Formatting Buttons
  const formatButtons = document.querySelectorAll('[data-format]');
  formatButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault(); // Prevent focus loss
      const format = btn.dataset.format;

      switch (format) {
        case 'bold':
          execFormat('bold');
          break;
        case 'italic':
          execFormat('italic');
          break;
        case 'underline':
          execFormat('underline');
          break;
        case 'link':
          const url = prompt('Enter link URL:', 'https://');
          if (url) execFormat('createLink', url);
          break;
        case 'ul':
          execFormat('insertUnorderedList');
          break;
        case 'ol':
          execFormat('insertOrderedList');
          break;
      }

      // Toggle active state
      setTimeout(updateButtonStates, 10);
    });
  });

  // Update button active states based on selection
  function updateButtonStates() {
    if (document.activeElement !== textInput) return;

    formatButtons.forEach(btn => {
      const format = btn.dataset.format;
      let isActive = false;

      try {
        switch (format) {
          case 'bold': isActive = document.queryCommandState('bold'); break;
          case 'italic': isActive = document.queryCommandState('italic'); break;
          case 'underline': isActive = document.queryCommandState('underline'); break;
          case 'ul': isActive = document.queryCommandState('insertUnorderedList'); break;
          case 'ol': isActive = document.queryCommandState('insertOrderedList'); break;
        }
      } catch (e) { }

      if (isActive) btn.classList.add('active');
      else btn.classList.remove('active');
    });
  }

  // Check state on cursor move
  textInput.addEventListener('keyup', updateButtonStates);
  textInput.addEventListener('mouseup', updateButtonStates);
  textInput.addEventListener('click', updateButtonStates);

  // Undo/Redo Buttons
  const undoBtn = document.querySelector('[data-action="undo"]');
  const redoBtn = document.querySelector('[data-action="redo"]');

  if (undoBtn) {
    undoBtn.addEventListener('click', () => execFormat('undo'));
  }

  if (redoBtn) {
    redoBtn.addEventListener('click', () => execFormat('redo'));
  }

  // Heading Select
  const headingSelect = document.querySelector('.toolbar-select');
  if (headingSelect) {
    headingSelect.addEventListener('change', () => {
      const val = headingSelect.value;

      if (val === 'Body text') execFormat('formatBlock', '<P>');
      else if (val === 'Heading 1') execFormat('formatBlock', '<H1>');
      else if (val === 'Heading 2') execFormat('formatBlock', '<H2>');
      else if (val === 'Heading 3') execFormat('formatBlock', '<H3>');
    });
  }
});

// ===== Theme Toggle (separate from main script) =====
document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('themeToggle');
  const themeStorageKey = 'keyez-theme'; // Use same key as landing page

  function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);

    // Update button icon
    const svg = themeToggle?.querySelector('svg path');
    if (svg) {
      if (theme === 'light') {
        // Moon icon for light mode
        svg.setAttribute('d', 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z');
      } else {
        // Sun icon for dark mode
        svg.setAttribute('d', 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z');
      }
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.body.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

      localStorage.setItem(themeStorageKey, newTheme);
      applyTheme(newTheme);
    });

    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem(themeStorageKey) || 'dark';
    applyTheme(savedTheme);
  }

  // Listen for theme changes from other tabs/pages
  window.addEventListener('storage', (e) => {
    if (e.key === themeStorageKey && e.newValue) {
      applyTheme(e.newValue);
    }
  });

  // ===== Language Toggle =====
  const langToggle = document.getElementById('langToggle');
  const langStorageKey = 'keyez-lang';

  function getStoredLang() {
    try {
      return localStorage.getItem(langStorageKey) || 'en';
    } catch (_) {
      return 'en';
    }
  }

  function setStoredLang(value) {
    try { localStorage.setItem(langStorageKey, value); } catch (_) { }
  }

  function applyLang(lang) {
    document.body.setAttribute('data-lang', lang);
    document.documentElement.lang = lang === 'en' ? 'en' : 'km';
    if (langToggle) { langToggle.textContent = lang === 'en' ? 'EN' : 'ខ្មែរ'; }

    // Update all elements with translations
    const elements = document.querySelectorAll('[data-lang-en][data-lang-km]');
    elements.forEach(el => {
      const text = lang === 'en' ? el.dataset.langEn : el.dataset.langKm;
      if (text) {
        // Special handling for placeholder attributes if needed
        if (el.hasAttribute('placeholder')) {
          el.setAttribute('placeholder', text);
        } else {
          el.textContent = text;
        }
      }
    });

    // Update body class for fonts
    if (lang === 'km') {
      document.body.classList.add('font-[Noto_Sans_Khmer]');
      document.body.classList.remove('font-[Inter]');
    } else {
      document.body.classList.add('font-[Inter]');
      document.body.classList.remove('font-[Noto_Sans_Khmer]');
    }
  }

  let activeLang = getStoredLang();
  applyLang(activeLang);

  if (langToggle) {
    langToggle.addEventListener('click', () => {
      activeLang = activeLang === 'en' ? 'km' : 'en';
      setStoredLang(activeLang);
      applyLang(activeLang);
    });
  }

  // ===== Mobile Menu Toggle =====
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const mobileMenuClose = document.getElementById('mobileMenuClose');
  const mobileMenu = document.getElementById('mobileMenu');

  if (mobileMenuToggle && mobileMenu && mobileMenuClose) {
    // Open mobile menu
    mobileMenuToggle.addEventListener('click', () => {
      mobileMenu.classList.remove('hidden');
      setTimeout(() => {
        mobileMenu.style.opacity = '1';
      }, 10);
      document.body.style.overflow = 'hidden';
    });

    // Close mobile menu
    const closeMobileMenu = () => {
      mobileMenu.style.opacity = '0';
      setTimeout(() => {
        mobileMenu.classList.add('hidden');
        document.body.style.overflow = '';
      }, 300);
    };

    mobileMenuClose.addEventListener('click', closeMobileMenu);

    // Close menu when clicking on a link
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeMobileMenu);
    });

    // Close menu when clicking backdrop
    mobileMenu.addEventListener('click', (e) => {
      if (e.target === mobileMenu) closeMobileMenu();
    });
  }

  // ===== Toolbar More Toggle (Mobile) =====
  const toolbarMoreToggle = document.getElementById('toolbarMoreToggle');
  const toolbarSecondary = document.getElementById('toolbarSecondary');

  if (toolbarMoreToggle && toolbarSecondary) {
    toolbarMoreToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = toolbarSecondary.classList.contains('hidden');
      if (isHidden) {
        toolbarSecondary.classList.remove('hidden');
        toolbarSecondary.classList.add('flex');
      } else {
        toolbarSecondary.classList.add('hidden');
        toolbarSecondary.classList.remove('flex');
      }
    });

    // Close secondary toolbar when clicking outside
    document.addEventListener('click', (e) => {
      if (toolbarSecondary && !toolbarSecondary.contains(e.target) && toolbarMoreToggle && !toolbarMoreToggle.contains(e.target)) {
        if (!toolbarSecondary.classList.contains('hidden') && window.innerWidth < 768) {
          toolbarSecondary.classList.add('hidden');
          toolbarSecondary.classList.remove('flex');
        }
      }
    });
  }

  // ===== Sync Format Select Dropdowns =====
  const formatSelect = document.getElementById('formatSelect');
  const formatSelectMobile = document.getElementById('formatSelectMobile');

  if (formatSelect && formatSelectMobile) {
    // Sync desktop to mobile
    formatSelect.addEventListener('change', () => {
      formatSelectMobile.value = formatSelect.value;
    });

    // Sync mobile to desktop
    formatSelectMobile.addEventListener('change', () => {
      formatSelect.value = formatSelectMobile.value;
    });
  }
});
