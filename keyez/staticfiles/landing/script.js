// Year
document.getElementById('y').textContent = new Date().getFullYear()

const themeStorageKey = 'keyez-theme'
const themeToggle = document.getElementById('themeToggle')
const prefersColorScheme = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null

function getStoredTheme() {
  try {
    return localStorage.getItem(themeStorageKey)
  } catch (_) {
    return null
  }
}

function setStoredTheme(value) {
  try {
    localStorage.setItem(themeStorageKey, value)
  } catch (_) {
    // ignore write errors (e.g., Safari private mode)
  }
}

function applyTheme(theme) {
  document.body.dataset.theme = theme
  document.documentElement.style.colorScheme = theme
  if (themeToggle) {
    const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
    themeToggle.setAttribute('aria-label', label)

    // Update SVG icon instead of using emoji
    const svg = themeToggle.querySelector('svg path')
    if (svg) {
      if (theme === 'light') {
        // Moon icon for light mode
        svg.setAttribute('d', 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z')
      } else {
        // Sun icon for dark mode
        svg.setAttribute('d', 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z')
      }
    }
  }
}

let activeTheme = document.body.dataset.theme || 'dark'
const storedTheme = getStoredTheme()

if (storedTheme) {
  activeTheme = storedTheme
} else if (prefersColorScheme) {
  activeTheme = prefersColorScheme.matches ? 'dark' : 'light'
}

applyTheme(activeTheme)

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    activeTheme = activeTheme === 'dark' ? 'light' : 'dark'
    setStoredTheme(activeTheme)
    applyTheme(activeTheme)
  })
}

// Listen for theme changes from other tabs/pages
window.addEventListener('storage', (e) => {
  if (e.key === themeStorageKey && e.newValue) {
    activeTheme = e.newValue
    applyTheme(activeTheme)
  }
})

// ===== Mobile Menu Toggle =====
const mobileMenuToggle = document.getElementById('mobileMenuToggle')
const mobileMenuClose = document.getElementById('mobileMenuClose')
const mobileMenu = document.getElementById('mobileMenu')

if (mobileMenuToggle && mobileMenu && mobileMenuClose) {
  // Open mobile menu
  mobileMenuToggle.addEventListener('click', () => {
    mobileMenu.classList.remove('hidden')
    setTimeout(() => {
      mobileMenu.style.opacity = '1'
    }, 10)
    document.body.style.overflow = 'hidden'
  })

  // Close mobile menu
  const closeMobileMenu = () => {
    mobileMenu.style.opacity = '0'
    setTimeout(() => {
      mobileMenu.classList.add('hidden')
      document.body.style.overflow = ''
    }, 300)
  }

  mobileMenuClose.addEventListener('click', closeMobileMenu)

  // Close menu when clicking on a link
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMobileMenu)
  })
}

if (prefersColorScheme) {
  const handleSchemeChange = (event) => {
    if (getStoredTheme()) return
    activeTheme = event.matches ? 'dark' : 'light'
    applyTheme(activeTheme)
  }

  if (typeof prefersColorScheme.addEventListener === 'function') {
    prefersColorScheme.addEventListener('change', handleSchemeChange)
  } else if (typeof prefersColorScheme.addListener === 'function') {
    prefersColorScheme.addListener(handleSchemeChange)
  }
}

const input = document.getElementById('latinInput')
const out = document.getElementById('khOutput')
const cand = document.getElementById('candidates')

const animatedElements = Array.from(new Set([
  ...document.querySelectorAll('[data-animate]'),
  ...document.querySelectorAll('.card')
]))

animatedElements.forEach(el => {
  if (!el.classList.contains('animate-on-scroll')) {
    el.classList.add('animate-on-scroll')
  }
})

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

if (prefersReducedMotion.matches || typeof IntersectionObserver === 'undefined') {
  animatedElements.forEach(el => el.classList.add('is-visible'))
} else if (animatedElements.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.18, rootMargin: '0px 0px -40px' })

  animatedElements.forEach(el => {
    const rect = el.getBoundingClientRect()
    if (rect.top <= window.innerHeight * 0.85) {
      el.classList.add('is-visible')
    } else {
      observer.observe(el)
    }
  })
}

// Old simple demo removed - now using AI model API

// number keys 1-3 to pick candidate (context-aware: main demo or social demo)
window.addEventListener('keydown', (e) => {
  const ae = document.activeElement
  const fbC = document.getElementById('fbCandidates')
  let target = null
  // Number keys 1-3 still pick candidates
  if (/^[1-3]$/.test(e.key)) {
    if (ae && ae.id === 'fbInput' && fbC) {
      target = fbC
    } else if (cand) {
      target = cand
    }
    if (!target) return
    const children = Array.from(target.children)
    const idx = Number(e.key) - 1
    if (children[idx]) children[idx].click()
    return
  }
  // Enter key picks the middle candidate in the main bar
  if (e.key === 'Enter' && cand && document.activeElement === input) {
    const mid = cand.children[1]
    if (mid) mid.click()
    e.preventDefault()
    return
  }
})

// Language toggle
const langStorageKey = 'keyez-lang'
const langBtn = document.getElementById('langToggle')

function getStoredLang() {
  try {
    return localStorage.getItem(langStorageKey) || 'en'
  } catch (_) {
    return 'en'
  }
}

function setStoredLang(value) {
  try { localStorage.setItem(langStorageKey, value) } catch (_) { }
}

function applyLang(lang) {
  document.body.dataset.lang = lang
  document.documentElement.lang = lang === 'en' ? 'en' : 'km'
  if (langBtn) { langBtn.textContent = lang === 'en' ? 'EN' : 'ខ្មែរ' }
  const elements = document.querySelectorAll('[data-lang-en][data-lang-km]')
  elements.forEach(el => {
    const text = lang === 'en' ? el.dataset.langEn : el.dataset.langKm
    if (text) {
      if (el.tagName === 'H1' && text.includes('.')) {
        const parts = text.split('.').filter(p => p.trim())
        el.innerHTML = parts.map(p => p.trim() + '.').join('<br/>')
      } else {
        el.textContent = text
      }
    }
  })
  // Font is now handled by CSS via body[data-lang="km"]
}

let activeLang = getStoredLang()
applyLang(activeLang)
if (langBtn) {
  langBtn.addEventListener('click', () => {
    activeLang = activeLang === 'en' ? 'km' : 'en'
    setStoredLang(activeLang)
    applyLang(activeLang)
  })
}

// Active navigation tracking
const navLinks = document.querySelectorAll('header nav a[href^="#"]')
const sections = Array.from(navLinks).map(link => {
  const href = link.getAttribute('href')
  return { link, section: document.querySelector(href), id: href }
})

function updateActiveNav() {
  const scrollPos = window.scrollY + 150 // offset for fixed header

  let currentSection = null

  // Find the current section based on scroll position
  for (let i = sections.length - 1; i >= 0; i--) {
    const { section, id } = sections[i]
    if (section && section.offsetTop <= scrollPos) {
      currentSection = id
      break
    }
  }

  // Update active class on nav links
  navLinks.forEach(link => {
    const href = link.getAttribute('href')
    if (href === currentSection) {
      link.classList.add('active')
    } else {
      link.classList.remove('active')
    }
  })
}

// Update on scroll with throttle
let ticking = false
window.addEventListener('scroll', () => {
  if (!ticking) {
    window.requestAnimationFrame(() => {
      updateActiveNav()
      ticking = false
    })
    ticking = true
  }
})

// Update on load
window.addEventListener('load', updateActiveNav)
// Update immediately
updateActiveNav()



// --- Provider interchangeable (mock aujourd’hui, API demain) ---
const CandidateProvider = {
  // Using AI Model API for transliteration
  async suggestRomanToKhmer(query) {
    const q = query.toLowerCase().trim();
    if (!q) return [];

    try {
      // Call the AI model API
      console.log('🔄 CandidateProvider calling API for:', q);
      const response = await fetch('/transliterate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: q })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ CandidateProvider API response:', result);

      if (result.success && result.candidates) {
        // API returns [2nd, BEST, 3rd] - we want [BEST, 2nd, 3rd] for display
        return [result.candidates[1], result.candidates[0], result.candidates[2]].filter(Boolean);
      }

      // Fallback to common words on API failure
      return FALLBACKS.slice(0, 3);
    } catch (error) {
      console.error('❌ CandidateProvider error:', error);
      // Fallback to common words on error
      return FALLBACKS.slice(0, 3);
    }
  }
};

// ---- Toujours 3 suggestions : liste de secours très courante ----
const FALLBACKS = [
  'ខ្ញុំ', 'អ្នក', 'យើង', 'ទៅ', 'មក', 'បាន', 'កំពុង', 'នឹង',
  'សួស្តី', 'អរគុណ', 'សុំទោស', 'បាទ', 'ចាស',
  'បង', 'ប្អូន', 'មិត្ត', 'គ្រូ',
  'ផ្ទះ', 'សាលា', 'ធ្វើការ', 'រៀន', 'ញ៉ាំ', 'ផឹក',
  'ទីក្រុង', 'ភ្នំពេញ', 'ផ្សារ', 'ធនាគារ', 'ប្រាក់'
];

// --- Gestion UI ---
const fbCandidates = document.getElementById('fbCandidates');
let candidateState = { items: [], selectedIndex: 0 };

// util: debounce pour limiter les requêtes
function debounce(fn, delay = 80) {
  let t = null; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

// extrait le dernier token roman (singkhmer) depuis ta zone de saisie
function getLastRomanToken(text) {
  // autorise lettres + apostrophes (pinyin-like)
  const m = text.match(/([a-zA-Z']+)$/);
  return m ? m[1] : "";
}

// remplace le dernier token par le khmer choisi + espace
function commitCandidateToInput(khmerWord) {
  const input = document.getElementById('fbInput') || document.querySelector('textarea, input[type="text"]');
  if (!input) return;
  const before = input.value;
  const m = before.match(/([a-zA-Z']+)$/);
  if (m) {
    input.value = before.slice(0, m.index) + khmerWord;
  } else {
    input.value = before + khmerWord;
  }
  input.focus();
  // reset barre
  renderCandidates([]);
}

// rend les pills
function renderCandidates(list) {
  // Early return if fbCandidates doesn't exist
  if (!fbCandidates) return;

  // Normalize to exactly 3 slots, and place best (index 0) in the middle visual slot
  const top3 = list.slice(0, 3);
  const slots = [top3[1] || '', top3[0] || '', top3[2] || ''];
  candidateState.items = slots;
  candidateState.selectedIndex = slots.some(Boolean) ? 1 : 0;
  fbCandidates.innerHTML = "";

  for (let i = 0; i < 3; i++) {
    const txt = slots[i] || '';
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'slot' + (i === 1 && txt ? ' primary' : '');
    b.setAttribute('data-idx', String(i));
    b.setAttribute('role', 'option');
    b.setAttribute('aria-selected', i === 1 && txt ? 'true' : 'false');
    if (txt) {
      b.textContent = txt;
      b.addEventListener('click', () => commitCandidateToInput(txt));
    } else {
      b.textContent = '';
      b.setAttribute('disabled', '');
      b.setAttribute('aria-hidden', 'true');
    }
    fbCandidates.appendChild(b);
  }
}

// met à jour la sélection visuelle
function updateSelectedCandidate() {
  [...fbCandidates.children].forEach((el, i) => {
    el.setAttribute('aria-selected', i === candidateState.selectedIndex ? 'true' : 'false');
  });
  // auto-scroll le pill sélectionné dans la vue
  const selected = fbCandidates.children[candidateState.selectedIndex];
  if (selected) {
    const rect = selected.getBoundingClientRect();
    const parentRect = fbCandidates.getBoundingClientRect();
    if (rect.right > parentRect.right) fbCandidates.scrollLeft += (rect.right - parentRect.right) + 12;
    if (rect.left < parentRect.left) fbCandidates.scrollLeft -= (parentRect.left - rect.left) + 12;
  }
}

// écoute la saisie pour déclencher les suggestions

// Universal input handler for period replacement and candidate bar
const onInputChanged = debounce(async (e) => {
  // Use event target if available, else fallback
  const input = e && e.target ? e.target : (document.getElementById('fbInput') || document.querySelector('textarea, input[type="text"]'));
  if (!input) return;

  const cursorPos = input.selectionStart;
  const val = input.value;

  // ✅ 1. Si l'utilisateur tape ".", remplace automatiquement par "។"
  if (cursorPos > 0 && val[cursorPos - 1] === '.') {
    // Replace the period with Khmer period at cursor position
    const before = val.slice(0, cursorPos - 1);
    const after = val.slice(cursorPos);
    input.value = before + '។' + after;
    input.setSelectionRange(cursorPos, cursorPos);
    input.focus();
    if (typeof renderCandidates === 'function') renderCandidates([]);
    if (typeof fbCandidates !== 'undefined' && fbCandidates) fbCandidates.innerHTML = '';
    return;
  }

  const token = getLastRomanToken(input.value);

  // ✅ 2. Si rien à suggérer, on nettoie
  if (token.length === 0) {
    if (typeof renderCandidates === 'function') renderCandidates([]);
    if (typeof fbCandidates !== 'undefined' && fbCandidates) fbCandidates.innerHTML = '';
    return;
  }

  // ✅ 3. Sinon, on fait la recherche normale
  const cands = await CandidateProvider.suggestRomanToKhmer(token);
  if (typeof renderCandidates === 'function') renderCandidates(cands);
}, 30); // Reduced from 80ms to 30ms for better responsiveness


// branchements
(function initCandidateBar() {
  // Attach to all relevant inputs, regardless of social demo
  const inputs = [
    document.getElementById('fbInput'),
    document.getElementById('latinInput'),
    ...Array.from(document.querySelectorAll('textarea, input[type="text"]'))
  ].filter(Boolean);
  inputs.forEach(input => {
    input.addEventListener('input', onInputChanged);
    input.addEventListener('keyup', (e) => {
      // Enter valide le candidat sélectionné
      if (e.key === 'Enter' && candidateState.items.length) {
        commitCandidateToInput(candidateState.items[candidateState.selectedIndex]);
        e.preventDefault();
      }
    });
  });

  // 2) navigation via ←/→ quand la barre a le focus (ou global si tu préfères)
  window.addEventListener('keydown', (e) => {
    // Only navigate candidates if there are visible items, otherwise allow normal cursor movement
    if (!candidateState.items.length || !candidateState.items.some(Boolean)) return;
    if (e.key === 'ArrowRight') {
      candidateState.selectedIndex = Math.min(candidateState.selectedIndex + 1, candidateState.items.length - 1);
      updateSelectedCandidate(); e.preventDefault();
    } else if (e.key === 'ArrowLeft') {
      candidateState.selectedIndex = Math.max(candidateState.selectedIndex - 1, 0);
      updateSelectedCandidate(); e.preventDefault();
    }
  });

  // 3) expose une fonction pour le clavier virtuel : quand l’utilisateur tape une lettre
  window.fbKeyboardOnCharInserted = () => onInputChanged();

  // 4) initial
  if (typeof renderCandidates === 'function') renderCandidates([]);
})();



