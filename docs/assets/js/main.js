/**
 * Cidadão.AI - Technical Documentation JavaScript
 * Enhanced functionality for technical documentation platform
 * Author: Anderson H. Silva
 * License: Proprietary - All rights reserved
 */

// MathJax Configuration
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
    }
};

// Initialize components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeDocumentation();
});

/**
 * Initialize the documentation system
 */
function initializeDocumentation() {
    console.log('🚀 Initializing Cidadão.AI Documentation System...');
    
    // Initialize theme system
    initializeTheme();
    
    // Initialize language system
    initializeLanguage();
    
    // Setup navigation
    setupNavigation();
    
    // Setup controls
    setupControls();
    
    // Setup mobile menu
    setupMobileMenu();
    
    // Setup credits modal
    setupCreditsModal();
    
    // Initialize mermaid diagrams
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ 
            startOnLoad: true,
            theme: getTheme() === 'dark' ? 'dark' : 'default'
        });
    }
    
    // Load default section
    const initialSection = 'overview';
    loadSectionWithRetry(initialSection);
    
    console.log('✅ Documentation system initialized successfully');
    
    // Track initialization
    trackEvent('documentation_initialized', {
        theme: getTheme(),
        language: getLanguage(),
        section: initialSection
    });
}

/**
 * Theme Management
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('cidadao-ai-theme') || 'light';
    setTheme(savedTheme);
}

function getTheme() {
    return document.getElementById('html-root').getAttribute('data-theme') || 'light';
}

function setTheme(theme) {
    document.getElementById('html-root').setAttribute('data-theme', theme);
    localStorage.setItem('cidadao-ai-theme', theme);
    
    // Update theme button
    const themeButton = document.getElementById('themeToggle');
    if (themeButton) {
        themeButton.textContent = theme === 'dark' ? '☀️' : '🌙';
        themeButton.setAttribute('data-title-pt', 
            theme === 'dark' ? 'Modo Claro' : 'Modo Escuro');
        themeButton.setAttribute('data-title-en', 
            theme === 'dark' ? 'Light Mode' : 'Dark Mode');
        
        // Update tooltip
        const currentLang = getLanguage();
        const tooltipText = theme === 'dark' 
            ? (currentLang === 'pt-BR' ? 'Modo Claro' : 'Light Mode')
            : (currentLang === 'pt-BR' ? 'Modo Escuro' : 'Dark Mode');
        themeButton.setAttribute('title', tooltipText);
    }
    
    // Update mermaid theme if it exists
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ 
            theme: theme === 'dark' ? 'dark' : 'default'
        });
    }
    
    trackEvent('theme_changed', { theme });
}

function toggleTheme() {
    const currentTheme = getTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

/**
 * Language Management
 */
function initializeLanguage() {
    const savedLang = localStorage.getItem('cidadao-ai-lang') || 'pt-BR';
    setLanguage(savedLang);
}

function getLanguage() {
    return document.documentElement.lang || 'pt-BR';
}

function setLanguage(lang) {
    document.documentElement.lang = lang;
    localStorage.setItem('cidadao-ai-lang', lang);
    
    // Update flag buttons
    document.querySelectorAll('.lang-flag').forEach(btn => btn.classList.remove('active'));
    if (lang === 'pt-BR') {
        const ptButton = document.getElementById('langPT');
        if (ptButton) ptButton.classList.add('active');
    } else {
        const enButton = document.getElementById('langEN');
        if (enButton) enButton.classList.add('active');
    }
    
    // Update text elements
    updateLanguageElements(lang);
    
    // Update navigation buttons for current section
    const currentSection = document.querySelector('.content-section.active');
    if (currentSection) {
        updateNavigationButtons(currentSection.id);
    }
    
    trackEvent('language_changed', { language: lang });
}

function updateLanguageElements(lang) {
    // Update text content
    document.querySelectorAll('[data-pt][data-en]').forEach(element => {
        if (lang === 'pt-BR') {
            element.textContent = element.getAttribute('data-pt');
        } else {
            element.textContent = element.getAttribute('data-en');
        }
    });
    
    // Update tooltips (title attribute)
    document.querySelectorAll('[data-title-pt][data-title-en]').forEach(element => {
        if (lang === 'pt-BR') {
            element.setAttribute('title', element.getAttribute('data-title-pt'));
        } else {
            element.setAttribute('title', element.getAttribute('data-title-en'));
        }
    });
}

/**
 * Navigation System
 */
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionName = this.getAttribute('data-section');
            if (sectionName) {
                // Add loading state
                this.classList.add('loading');
                
                // Load section
                loadSectionWithRetry(sectionName).finally(() => {
                    this.classList.remove('loading');
                });
                
                // Update active state
                setActiveNavLink(this);
                
                // Track navigation
                trackEvent('section_navigated', { 
                    section: sectionName,
                    method: 'sidebar'
                });
            }
        });
    });
}

function setActiveNavLink(activeLink) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

/**
 * Control Setup
 */
function setupControls() {
    // Theme toggle
    const themeButton = document.getElementById('themeToggle');
    if (themeButton) {
        themeButton.addEventListener('click', toggleTheme);
    }
    
    // Language toggles
    const ptButton = document.getElementById('langPT');
    const enButton = document.getElementById('langEN');
    
    if (ptButton) {
        ptButton.addEventListener('click', () => setLanguage('pt-BR'));
    }
    
    if (enButton) {
        enButton.addEventListener('click', () => setLanguage('en-US'));
    }
    
    // Print button
    const printButton = document.getElementById('printMode');
    if (printButton) {
        printButton.addEventListener('click', enterPrintMode);
    }
}

/**
 * Mobile Menu
 */
function setupMobileMenu() {
    const mobileButton = document.createElement('button');
    mobileButton.className = 'mobile-menu-button';
    mobileButton.innerHTML = '☰';
    mobileButton.onclick = toggleMobileMenu;
    
    document.body.appendChild(mobileButton);
}

function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

/**
 * Credits Modal
 */
function setupCreditsModal() {
    const creditsButton = document.getElementById('creditsButton');
    const creditsModal = document.getElementById('creditsModal');
    const creditsClose = document.getElementById('creditsClose');
    
    if (creditsButton && creditsModal) {
        creditsButton.addEventListener('click', () => {
            creditsModal.classList.toggle('open');
            trackEvent('credits_opened');
        });
    }
    
    if (creditsClose && creditsModal) {
        creditsClose.addEventListener('click', () => {
            creditsModal.classList.remove('open');
        });
    }
    
    // Close on outside click
    if (creditsModal) {
        document.addEventListener('click', (e) => {
            if (!creditsModal.contains(e.target) && !creditsButton?.contains(e.target)) {
                creditsModal.classList.remove('open');
            }
        });
    }
}

/**
 * Section Loading System
 */
async function loadSectionWithRetry(sectionName, maxRetries = 3) {
    console.log(`📄 Loading section: ${sectionName}`);
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            await loadSection(sectionName);
            updateProgress(sectionName);
            updateNavigationButtons(sectionName);
            
            // Update URL hash without triggering navigation
            if (history.replaceState) {
                history.replaceState(null, null, `#${sectionName}`);
            }
            
            console.log(`✅ Section loaded successfully: ${sectionName}`);
            
            trackEvent('section_loaded', { 
                section: sectionName, 
                attempt,
                success: true 
            });
            
            return;
            
        } catch (error) {
            console.warn(`⚠️ Attempt ${attempt} failed for section ${sectionName}:`, error);
            
            if (attempt === maxRetries) {
                console.error(`❌ All attempts failed for section ${sectionName}`);
                trackEvent('section_load_failed', { 
                    section: sectionName, 
                    attempts: maxRetries,
                    error: error.message 
                });
                throw error;
            }
            
            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
    }
}

async function loadSection(sectionName) {
    const section = document.getElementById(sectionName);
    if (!section) {
        throw new Error(`Section element not found: ${sectionName}`);
    }
    
    // Show loading state
    section.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
    
    // Show section
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    section.classList.add('active');
    
    try {
        // Determine base path for GitHub Pages
        const basePath = getBasePath();
        const response = await fetch(`${basePath}sections/${sectionName}.html`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const content = await response.text();
        section.innerHTML = content;
        
        // Reinitialize components
        reinitializeComponents(section);
        
    } catch (error) {
        console.error(`Failed to load section ${sectionName}:`, error);
        
        // Try fallback to overview if not already trying overview
        if (sectionName !== 'overview') {
            try {
                const basePath = getBasePath();
                const fallbackResponse = await fetch(`${basePath}sections/overview.html`);
                if (fallbackResponse.ok) {
                    const fallbackContent = await fallbackResponse.text();
                    section.innerHTML = `
                        <div class="error-message">
                            <h3>⚠️ Seção temporariamente indisponível</h3>
                            <p>A seção "${sectionName}" está sendo processada. Exibindo conteúdo alternativo.</p>
                            <p><small><strong>Debug:</strong> ${error.message}</small></p>
                            <br>
                            <button onclick="window.location.reload()" class="retry-button">🔄 Tentar novamente</button>
                        </div>
                        <hr>
                        ${fallbackContent}
                    `;
                    reinitializeComponents(section);
                    return;
                }
            } catch (fallbackError) {
                console.error('Fallback also failed:', fallbackError);
            }
        }
        
        // Show detailed error message
        section.innerHTML = createErrorMessage(sectionName, error);
    }
}

function createErrorMessage(sectionName, error) {
    return `
        <div class="error-message">
            <h3>❌ Erro ao carregar seção</h3>
            <p>Não foi possível carregar o conteúdo da seção "${sectionName}". Verifique se o arquivo existe.</p>
            <p><strong>Erro:</strong> ${error.message}</p>
            <div class="error-debug">
                <h4>🔍 Informações de Debug:</h4>
                <ul>
                    <li><strong>URL atual:</strong> <code>${window.location.href}</code></li>
                    <li><strong>Hostname:</strong> <code>${window.location.hostname}</code></li>
                    <li><strong>Protocolo:</strong> <code>${window.location.protocol}</code></li>
                    <li><strong>Caminho:</strong> <code>${window.location.pathname}</code></li>
                    <li><strong>URL da seção:</strong> <code>./sections/${sectionName}.html</code></li>
                    <li><strong>Timestamp:</strong> <code>${new Date().toISOString()}</code></li>
                </ul>
            </div>
            <div class="error-help">
                <h4>💡 Como resolver:</h4>
                <ul>
                    <li><strong>GitHub Pages:</strong> Aguarde alguns minutos para o deploy completar</li>
                    <li><strong>Para uso local:</strong> Execute <code>python -m http.server 8000</code></li>
                    <li><strong>Para desenvolvimento:</strong> Use extensão "Live Server" no VS Code</li>
                    <li><strong>Cache:</strong> Tente <kbd>Ctrl+F5</kbd> para forçar reload</li>
                </ul>
                <button onclick="window.location.reload()" class="retry-button" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--bg-accent); 
                               color: white; border: none; border-radius: 0.25rem; cursor: pointer;">
                    🔄 Recarregar Página
                </button>
            </div>
        </div>
    `;
}

function getBasePath() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // GitHub Pages detection
    if (hostname.includes('github.io')) {
        return pathname.endsWith('/') ? './' : './';
    }
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return './';
    }
    
    // Default
    return './';
}

function reinitializeComponents(container) {
    // Re-highlight code blocks
    if (typeof hljs !== 'undefined') {
        container.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }
    
    // Re-render math
    if (window.MathJax) {
        MathJax.typesetPromise([container]).catch(console.error);
    }
    
    // Re-render mermaid diagrams
    if (typeof mermaid !== 'undefined') {
        container.querySelectorAll('.mermaid').forEach(element => {
            mermaid.init(undefined, element);
        });
    }
}

/**
 * Progress and Navigation
 */
// Global sections array for navigation
const allSections = [
    'overview', 'theoretical-foundations', 'literature-review', 'methodology',
    'system-architecture', 'multi-agent-system', 'algorithms', 'data-pipeline',
    'technical-implementation', 'api-reference', 'security', 'performance',
    'experimental-design', 'benchmarks', 'case-studies', 'validation',
    'contributions', 'limitations', 'future-work', 'conclusion',
    'mathematical-proofs', 'code-examples', 'datasets', 'bibliography'
];

// Section titles for navigation
const sectionTitles = {
    'overview': { pt: 'Visão Geral e Introdução', en: 'Overview & Introduction' },
    'theoretical-foundations': { pt: 'Fundamentos Teóricos', en: 'Theoretical Foundations' },
    'literature-review': { pt: 'Revisão da Literatura', en: 'Literature Review' },
    'methodology': { pt: 'Metodologia de Pesquisa', en: 'Research Methodology' },
    'system-architecture': { pt: 'Arquitetura do Sistema', en: 'System Architecture' },
    'multi-agent-system': { pt: 'Sistema Multi-Agente', en: 'Multi-Agent System' },
    'algorithms': { pt: 'Algoritmos e Modelos', en: 'Algorithms & Models' },
    'data-pipeline': { pt: 'Pipeline de Dados', en: 'Data Pipeline' },
    'technical-implementation': { pt: 'Implementação Técnica', en: 'Technical Implementation' },
    'api-reference': { pt: 'Referência da API', en: 'API Reference' },
    'security': { pt: 'Framework de Segurança', en: 'Security Framework' },
    'performance': { pt: 'Análise de Performance', en: 'Performance Analysis' },
    'experimental-design': { pt: 'Design Experimental', en: 'Experimental Design' },
    'benchmarks': { pt: 'Benchmarks e Resultados', en: 'Benchmarks & Results' },
    'case-studies': { pt: 'Estudos de Caso', en: 'Case Studies' },
    'validation': { pt: 'Validação e Testes', en: 'Validation & Testing' },
    'contributions': { pt: 'Contribuições', en: 'Contributions' },
    'limitations': { pt: 'Limitações e Escopo', en: 'Limitations & Scope' },
    'future-work': { pt: 'Pesquisa Futura', en: 'Future Research' },
    'conclusion': { pt: 'Conclusão', en: 'Conclusion' },
    'mathematical-proofs': { pt: 'Provas Matemáticas', en: 'Mathematical Proofs' },
    'code-examples': { pt: 'Exemplos de Código', en: 'Code Examples' },
    'datasets': { pt: 'Datasets e Métricas', en: 'Datasets & Metrics' },
    'bibliography': { pt: 'Bibliografia', en: 'Bibliography' }
};

function updateProgress(sectionName) {
    const currentIndex = allSections.indexOf(sectionName);
    const progress = ((currentIndex + 1) / allSections.length) * 100;
    
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
}

function updateNavigationButtons(currentSection) {
    const currentIndex = allSections.indexOf(currentSection);
    const prevSection = currentIndex > 0 ? allSections[currentIndex - 1] : null;
    const nextSection = currentIndex < allSections.length - 1 ? allSections[currentIndex + 1] : null;
    
    // Remove existing navigation if any
    const existingNav = document.querySelector('.section-navigation');
    if (existingNav) {
        existingNav.remove();
    }
    
    // Create navigation container
    const navContainer = document.createElement('div');
    navContainer.className = 'section-navigation';
    navContainer.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        gap: 1rem;
    `;
    
    // Get current language
    const currentLang = getLanguage();
    const isPortuguese = currentLang === 'pt-BR';
    
    // Previous button
    if (prevSection) {
        const prevButton = document.createElement('a');
        prevButton.className = 'nav-button nav-button-prev';
        prevButton.href = '#';
        prevButton.style.cssText = `
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.5rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s;
            min-width: 200px;
        `;
        
        prevButton.onclick = (e) => {
            e.preventDefault();
            loadSectionWithRetry(prevSection);
            setActiveNavLink(document.querySelector(`[data-section="${prevSection}"]`));
        };
        
        prevButton.innerHTML = `
            <span style="font-size: 1.5rem;">←</span>
            <div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    ${isPortuguese ? 'Anterior' : 'Previous'}
                </div>
                <div style="font-weight: 500;">
                    ${sectionTitles[prevSection][isPortuguese ? 'pt' : 'en']}
                </div>
            </div>
        `;
        navContainer.appendChild(prevButton);
    }
    
    // Next button
    if (nextSection) {
        const nextButton = document.createElement('a');
        nextButton.className = 'nav-button nav-button-next';
        nextButton.href = '#';
        nextButton.style.cssText = `
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.5rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s;
            min-width: 200px;
            margin-left: auto;
        `;
        
        nextButton.onclick = (e) => {
            e.preventDefault();
            loadSectionWithRetry(nextSection);
            setActiveNavLink(document.querySelector(`[data-section="${nextSection}"]`));
        };
        
        nextButton.innerHTML = `
            <div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    ${isPortuguese ? 'Próxima' : 'Next'}
                </div>
                <div style="font-weight: 500;">
                    ${sectionTitles[nextSection][isPortuguese ? 'pt' : 'en']}
                </div>
            </div>
            <span style="font-size: 1.5rem;">→</span>
        `;
        navContainer.appendChild(nextButton);
    }
    
    // Add navigation to the current section
    const currentSectionElement = document.getElementById(currentSection);
    if (currentSectionElement && (prevSection || nextSection)) {
        currentSectionElement.appendChild(navContainer);
    }
}

/**
 * Utility Functions
 */
function enterPrintMode() {
    trackEvent('print_initiated');
    window.print();
}

/**
 * Analytics System
 */
function trackEvent(eventName, properties = {}) {
    console.log('📊 Event tracked:', eventName, properties);
    
    // Store in localStorage for basic analytics
    try {
        const events = JSON.parse(localStorage.getItem('cidadao-ai-events') || '[]');
        events.push({
            event: eventName,
            properties,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        });
        
        // Keep only last 100 events
        if (events.length > 100) {
            events.splice(0, events.length - 100);
        }
        
        localStorage.setItem('cidadao-ai-events', JSON.stringify(events));
    } catch (error) {
        console.warn('Failed to store analytics event:', error);
    }
}

/**
 * Hash Navigation Support
 */
window.addEventListener('hashchange', function() {
    const hash = window.location.hash.substring(1);
    if (hash && allSections.includes(hash)) {
        loadSectionWithRetry(hash);
        setActiveNavLink(document.querySelector(`[data-section="${hash}"]`));
    }
});

// Load section from URL hash on page load
window.addEventListener('load', function() {
    const hash = window.location.hash.substring(1);
    if (hash && allSections.includes(hash)) {
        setTimeout(() => {
            loadSectionWithRetry(hash);
            setActiveNavLink(document.querySelector(`[data-section="${hash}"]`));
        }, 100);
    }
});

/**
 * Keyboard Shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Alt + T: Toggle theme
    if (e.altKey && e.key === 't') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Alt + L: Toggle language
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        const currentLang = getLanguage();
        setLanguage(currentLang === 'pt-BR' ? 'en-US' : 'pt-BR');
    }
    
    // Alt + P: Print
    if (e.altKey && e.key === 'p') {
        e.preventDefault();
        enterPrintMode();
    }
});

// Track page load
trackEvent('documentation_loaded', {
    theme: getTheme(),
    language: getLanguage(),
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    viewport: `${window.innerWidth}x${window.innerHeight}`
});

console.log('📚 Cidadão.AI Documentation JavaScript loaded successfully');