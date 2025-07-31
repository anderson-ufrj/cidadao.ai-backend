// Cidadão.AI Backend - JavaScript Principal

// ===== TRADUÇÕES ===== 
const translations = {
    'pt-BR': {
        'site.title': 'Cidadão.AI — Documentação Técnica Backend',
        'nav.theme.light': '☀️ Claro',
        'nav.theme.dark': '🌙 Escuro',
        'nav.lang.pt': '🇧🇷 PT',
        'nav.lang.en': '🇺🇸 EN',
        'nav.print': '🖨️ Imprimir',
        
        'hero.badge': '🇧🇷 Documentação Técnica Backend',
        'hero.title': 'Cidadão.AI Backend',
        'hero.subtitle': 'Documentação Técnica Completa',
        'hero.description': 'Sistema enterprise-grade multi-agente de IA para análise de transparência governamental brasileira. Documentação técnica de nível acadêmico com arquitetura, implementação e validação científica.',
        'hero.btn.about': '📚 Sobre o Sistema',
        'hero.btn.architecture': '🏗️ Arquitetura',
        
        'section.technical.title': 'Documentação Técnica',
        'section.links.title': 'Links do Projeto',
        
        'controls.expand-all': '📖 Expandir Todas',
        'controls.collapse-all': '📕 Recolher Todas',
        'controls.reading-mode': '📚 Modo Leitura',
        'controls.print': '🖨️ Imprimir',
        'search.placeholder': '🔍 Buscar na documentação...',
        
        'reading.toggle-sidebar': '☰',
        'reading.back-to-main': '← Voltar',
        'reading.close': '✕ Fechar',
        'reading.index': '📑 Índice',
        'reading.back-to-top': '↑',
        
        'category.fundamentacao.title': 'Fundamentação Teórica',
        'category.arquitetura.title': 'Arquitetura & Implementação',
        'category.ia.title': 'Inteligência Artificial & Machine Learning',
        'category.api.title': 'API & Integração',
        'category.validacao.title': 'Validação & Resultados',
        'category.conclusao.title': 'Conclusão & Trabalhos Futuros',
        
        'modal.about.title': 'Sobre o Cidadão.AI Backend',
        'modal.architecture.title': 'Arquitetura do Sistema',
        'modal.architecture.content': 'O Cidadão.AI Backend implementa uma arquitetura enterprise-grade com sistema multi-agente, API REST com 40+ endpoints, e infraestrutura containerizada para análise de transparência governamental brasileira.'
    },
    'en-US': {
        'site.title': 'Cidadão.AI — Backend Technical Documentation',
        'nav.theme.light': '☀️ Light',
        'nav.theme.dark': '🌙 Dark',
        'nav.lang.pt': '🇧🇷 PT',
        'nav.lang.en': '🇺🇸 EN',
        'nav.print': '🖨️ Print',
        
        'hero.badge': '🇧🇷 Backend Technical Documentation',
        'hero.title': 'Cidadão.AI Backend',
        'hero.subtitle': 'Complete Technical Documentation',
        'hero.description': 'Enterprise-grade multi-agent AI system for Brazilian government transparency analysis. Academic-level technical documentation with architecture, implementation and scientific validation.',
        'hero.btn.about': '📚 About the System',
        'hero.btn.architecture': '🏗️ Architecture',
        
        'section.technical.title': 'Technical Documentation',
        'section.links.title': 'Project Links',
        
        'controls.expand-all': '📖 Expand All',
        'controls.collapse-all': '📕 Collapse All',
        'controls.reading-mode': '📚 Reading Mode',
        'controls.print': '🖨️ Print',
        'search.placeholder': '🔍 Search documentation...',
        
        'reading.toggle-sidebar': '☰',
        'reading.back-to-main': '← Back',
        'reading.close': '✕ Close',
        'reading.index': '📑 Index',
        'reading.back-to-top': '↑',
        
        'category.fundamentacao.title': 'Theoretical Foundation',
        'category.arquitetura.title': 'Architecture & Implementation',
        'category.ia.title': 'Artificial Intelligence & Machine Learning',
        'category.api.title': 'API & Integration',
        'category.validacao.title': 'Validation & Results',
        'category.conclusao.title': 'Conclusion & Future Work',
        
        'modal.about.title': 'About Cidadão.AI Backend',
        'modal.architecture.title': 'System Architecture',
        'modal.architecture.content': 'Cidadão.AI Backend implements an enterprise-grade architecture with multi-agent system, REST API with 40+ endpoints, and containerized infrastructure for Brazilian government transparency analysis.'
    }
};

// ===== ESTADO GLOBAL =====
let currentLanguage = 'pt-BR';
let currentTheme = 'light';
let sectionsCache = {};

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Restaurar configurações salvas
    currentLanguage = localStorage.getItem('cidadao-language') || 'pt-BR';
    currentTheme = localStorage.getItem('cidadao-theme') || 'light';
    
    // Disponibilizar idioma globalmente para ContentManager
    window.currentLanguage = currentLanguage;
    
    // Aplicar configurações
    applyTheme(currentTheme);
    applyLanguage(currentLanguage);
    
    // Inicializar event listeners
    initializeThemeControls();
    initializeLanguageControls();
    initializePrintButton();
    initializeModals();
    initializeSectionNavigation();
    initializeProgressTracking();
    initReadingMode();
    
    console.log('🚀 Cidadão.AI Backend Documentation with Accordion initialized');
    console.log('📋 24 sections organized in 6 categories ready');
}

// ===== CONTROLE DE TEMA =====
function initializeThemeControls() {
    const themeButtons = document.querySelectorAll('[data-theme-btn]');
    
    themeButtons.forEach(button => {
        // Marcar botão ativo
        if (button.dataset.themeBtn === currentTheme) {
            button.classList.add('active');
        }
        
        // Adicionar event listener
        button.addEventListener('click', () => {
            const theme = button.dataset.themeBtn;
            switchTheme(theme);
        });
    });
}

function switchTheme(theme) {
    if (theme === currentTheme) return;
    
    currentTheme = theme;
    applyTheme(theme);
    
    // Salvar no localStorage
    localStorage.setItem('cidadao-theme', theme);
    
    // Atualizar botões
    updateThemeButtons();
    
    console.log(`🎨 Theme switched to: ${theme}`);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

function updateThemeButtons() {
    const themeButtons = document.querySelectorAll('[data-theme-btn]');
    
    themeButtons.forEach(button => {
        if (button.dataset.themeBtn === currentTheme) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// ===== CONTROLE DE IDIOMA =====
function initializeLanguageControls() {
    const languageButtons = document.querySelectorAll('[data-lang-btn]');
    
    languageButtons.forEach(button => {
        // Marcar botão ativo
        if (button.dataset.langBtn === currentLanguage) {
            button.classList.add('active');
        }
        
        // Adicionar event listener
        button.addEventListener('click', async () => {
            const language = button.dataset.langBtn;
            await switchLanguage(language);
        });
    });
}

async function switchLanguage(language) {
    if (language === currentLanguage) return;
    
    currentLanguage = language;
    window.currentLanguage = language; // Disponibilizar globalmente para ContentManager
    
    applyLanguage(language);
    
    // Salvar no localStorage
    localStorage.setItem('cidadao-language', language);
    
    // Atualizar botões
    updateLanguageButtons();
    
    // Recarregar conteúdo modular no idioma correto
    if (window.contentManager) {
        await window.contentManager.reloadModularContent();
    }
    
    // Se estamos no modo leitura, recarregar o conteúdo
    if (document.body.classList.contains('reading-mode')) {
        console.log(`🔄 Reloading reading mode content for ${language}`);
        await refreshReadingModeContent();
    }
    
    console.log(`🌍 Language switched to: ${language}`);
}

function applyLanguage(language) {
    const elementsWithI18n = document.querySelectorAll('[data-i18n]');
    
    elementsWithI18n.forEach(element => {
        const key = element.dataset.i18n;
        const translation = translations[language]?.[key];
        
        if (translation) {
            // Atualizar text content ou title baseado no elemento
            if (element.tagName === 'TITLE') {
                element.textContent = translation;
            } else if (element.hasAttribute('aria-label')) {
                element.setAttribute('aria-label', translation);
            } else {
                element.textContent = translation;
            }
        }
    });
    
    // Atualizar placeholders com data-i18n-placeholder
    const elementsWithI18nPlaceholder = document.querySelectorAll('[data-i18n-placeholder]');
    elementsWithI18nPlaceholder.forEach(element => {
        const key = element.dataset.i18nPlaceholder;
        const translation = translations[language]?.[key];
        
        if (translation && element.hasAttribute('placeholder')) {
            element.setAttribute('placeholder', translation);
        }
    });
    
    // Atualizar document title
    document.title = translations[language]?.['site.title'] || 'Cidadão.AI — Documentação Técnica Backend';
}

function updateLanguageButtons() {
    const languageButtons = document.querySelectorAll('[data-lang-btn]');
    
    languageButtons.forEach(button => {
        if (button.dataset.langBtn === currentLanguage) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// ===== BOTÃO DE IMPRESSÃO =====
function initializePrintButton() {
    const printButton = document.getElementById('printBtn');
    
    if (printButton) {
        printButton.addEventListener('click', () => {
            handlePrint();
        });
    }
}

function handlePrint() {
    // Mostrar conteúdo das seções para impressão
    const sectionContent = document.getElementById('section-content');
    const wasVisible = sectionContent.style.display !== 'none';
    
    if (!wasVisible) {
        // Se não há seção carregada, mostrar accordion
        console.log('📄 Print: usando accordion atual');
        
        // Aguardar um pouco para carregamento
        setTimeout(() => {
            window.print();
        }, 500);
    } else {
        window.print();
    }
    
    console.log('🖨️ Print initiated');
}

// ===== SISTEMA DE MODAIS =====
function initializeModals() {
    // Botões para abrir modais
    const modalTriggers = document.querySelectorAll('[data-modal-open]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.dataset.modalOpen;
            openModal(modalId);
        });
    });
    
    // Botões para fechar modais
    const modalCloses = document.querySelectorAll('[data-modal-close]');
    modalCloses.forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = closeBtn.dataset.modalClose;
            closeModal(modalId);
        });
    });
    
    // Fechar modal clicando no overlay
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Fechar modal com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal.id);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus no modal para acessibilidade
        modal.focus();
        
        console.log(`📖 Modal opened: ${modalId}`);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        
        console.log(`❌ Modal closed: ${modalId}`);
    }
}

// ===== ACCORDION SYSTEM =====
function initializeSectionNavigation() {
    initializeAccordion();
    initializeAccordionControls();
    initializeSearchSystem();
    initializeDeepLinking();
}

// ===== ACCORDION CORE =====
function initializeAccordion() {
    // Category toggles
    const categoryToggles = document.querySelectorAll('.category-toggle');
    categoryToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            toggleCategory(toggle);
        });
    });
    
    // Item toggles
    const itemToggles = document.querySelectorAll('.item-toggle');
    itemToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            toggleAccordionItem(toggle);
        });
    });
    
    console.log('🎯 Accordion system initialized with 24 sections');
}

function toggleCategory(toggle) {
    const category = toggle.closest('.accordion-category');
    const content = category.querySelector('.category-content');
    const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
    
    if (isExpanded) {
        // Collapse category
        toggle.setAttribute('aria-expanded', 'false');
        content.classList.remove('expanded');
        
        // Collapse all items inside
        const itemToggles = category.querySelectorAll('.item-toggle');
        itemToggles.forEach(itemToggle => {
            itemToggle.setAttribute('aria-expanded', 'false');
            const itemContent = itemToggle.closest('.accordion-item').querySelector('.item-content');
            itemContent.classList.remove('expanded');
        });
        
    } else {
        // Expand category
        toggle.setAttribute('aria-expanded', 'true');
        content.classList.add('expanded');
    }
    
    logEvent('category_toggle', {
        category: category.dataset.category,
        expanded: !isExpanded
    });
}

async function toggleAccordionItem(toggle) {
    const item = toggle.closest('.accordion-item');
    const content = item.querySelector('.item-content');
    const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
    const sectionName = item.dataset.section;
    
    if (isExpanded) {
        // Collapse item
        toggle.setAttribute('aria-expanded', 'false');
        content.classList.remove('expanded');
        
    } else {
        // Expand item
        toggle.setAttribute('aria-expanded', 'true');
        content.classList.add('expanded');
        
        // Load content if not loaded
        if (content.querySelector('.content-loading')) {
            // loadSectionContent substituído pelo OfflineAccordion
            console.log(`📄 Content loading handled by OfflineAccordion: ${sectionName}`);
        }
        
        // Force height recalculation for expanded content
        setTimeout(() => {
            content.style.maxHeight = 'none';
            content.style.overflow = 'visible';
            content.offsetHeight; // Force reflow
        }, 100);
        
        // Scroll to item
        setTimeout(() => {
            item.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start',
                inline: 'nearest'
            });
        }, 300);
    }
    
    // Update URL hash
    if (!isExpanded) {
        updateURLHash(sectionName);
    }
    
    logEvent('section_toggle', {
        section: sectionName,
        expanded: !isExpanded
    });
}

// ===== CONTENT LOADING =====
async function loadSectionContent(sectionName, contentElement) {
    console.log(`📄 Loading section content: ${sectionName}`);
    
    try {
        // Check cache first
        if (sectionsCache[sectionName]) {
            console.log(`💾 Loading ${sectionName} from cache`);
            contentElement.innerHTML = sectionsCache[sectionName];
            return;
        }
        
        // Show loading state
        contentElement.innerHTML = `
            <div class="content-loading">
                <div style="font-size: 1.5rem;">⏳</div>
                <p>Carregando conteúdo da seção...</p>
            </div>
        `;
        
        // Load from backup
        const response = await fetch(`../backup-docs-original/sections/${sectionName}.html`);
        
        if (!response.ok) {
            throw new Error(`Failed to load section: ${response.status}`);
        }
        
        const html = await response.text();
        
        // Process and clean HTML
        const cleanHtml = processSectionHtml(html);
        
        // Cache and display
        sectionsCache[sectionName] = cleanHtml;
        contentElement.innerHTML = cleanHtml;
        
        console.log(`✅ Section ${sectionName} loaded successfully`);
        
    } catch (error) {
        console.error(`❌ Error loading section ${sectionName}:`, error);
        
        // Fallback content
        contentElement.innerHTML = `
            <div class="content-loading">
                <div style="font-size: 1.5rem; color: var(--text-accent);">⚠️</div>
                <h3>Seção em Desenvolvimento</h3>
                <p>Esta seção da documentação está sendo preparada.</p>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">Seção: ${sectionName}</p>
            </div>
        `;
    }
}

function processSectionHtml(html) {
    // Remove scripts and problematic inline styles
    let processed = html
        .replace(/<script[^>]*>.*?<\/script>/gis, '')
        .replace(/<style[^>]*>.*?<\/style>/gis, '')
        .replace(/style="[^"]*"/gi, '');
    
    // Clean up and format
    processed = processed
        .replace(/data-pt="[^"]*"/gi, '')
        .replace(/data-en="[^"]*"/gi, '')
        .trim();
    
    return processed;
}

// ===== ACCORDION CONTROLS =====
function initializeAccordionControls() {
    // Expand All button
    const expandAllBtn = document.querySelector('.expand-all');
    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', expandAllSections);
    }
    
    // Collapse All button
    const collapseAllBtn = document.querySelector('.collapse-all');
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', collapseAllSections);
    }
}

function expandAllSections() {
    const categoryToggles = document.querySelectorAll('.category-toggle');
    const itemToggles = document.querySelectorAll('.item-toggle');
    
    // Expand all categories
    categoryToggles.forEach(toggle => {
        if (toggle.getAttribute('aria-expanded') !== 'true') {
            toggle.setAttribute('aria-expanded', 'true');
            const content = toggle.closest('.accordion-category').querySelector('.category-content');
            content.classList.add('expanded');
        }
    });
    
    // Expand all items
    itemToggles.forEach(toggle => {
        if (toggle.getAttribute('aria-expanded') !== 'true') {
            toggle.setAttribute('aria-expanded', 'true');
            const content = toggle.closest('.accordion-item').querySelector('.item-content');
            content.classList.add('expanded');
            
            // Load content if needed
            const sectionName = toggle.closest('.accordion-item').dataset.section;
            if (content.querySelector('.content-loading')) {
                console.log(`📄 Content loading handled by OfflineAccordion: ${sectionName}`);
            }
        }
    });
    
    logEvent('expand_all_sections');
    console.log('📖 All sections expanded');
}

function collapseAllSections() {
    const categoryToggles = document.querySelectorAll('.category-toggle');
    const itemToggles = document.querySelectorAll('.item-toggle');
    
    // Collapse all items first
    itemToggles.forEach(toggle => {
        toggle.setAttribute('aria-expanded', 'false');
        const content = toggle.closest('.accordion-item').querySelector('.item-content');
        content.classList.remove('expanded');
    });
    
    // Then collapse all categories
    categoryToggles.forEach(toggle => {
        toggle.setAttribute('aria-expanded', 'false');
        const content = toggle.closest('.accordion-category').querySelector('.category-content');
        content.classList.remove('expanded');
    });
    
    logEvent('collapse_all_sections');
    console.log('📕 All sections collapsed');
}

// ===== SEARCH SYSTEM =====
function initializeSearchSystem() {
    const searchInput = document.getElementById('searchInput');
    const searchClear = document.getElementById('searchClear');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(async (e) => {
            await handleSearch(e);
        }, 300));
        searchInput.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                await handleSearch(e);
            }
        });
    }
    
    if (searchClear) {
        searchClear.addEventListener('click', clearSearch);
    }
}

async function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    const accordion = document.getElementById('documentationAccordion');
    
    if (query === '') {
        clearSearch();
        return;
    }
    
    console.log(`🔍 Searching for: "${query}"`);
    
    let foundResults = false;
    let resultsCount = 0;
    
    // Search through categories and items
    const categories = accordion.querySelectorAll('.accordion-category');
    
    for (const category of categories) {
        let categoryHasResults = false;
        const items = category.querySelectorAll('.accordion-item');
        
        for (const item of items) {
            const title = item.querySelector('.item-title').textContent.toLowerCase();
            const sectionName = item.dataset.section.toLowerCase();
            const content = item.querySelector('.item-content');
            
            // Ensure modular content is loaded before searching
            if (content.querySelector('.content-loading')) {
                const sectionId = item.dataset.section;
                console.log(`📄 Loading content for search: ${sectionId}`);
                
                // ContentManager removido - usando OfflineAccordion
                console.log(`📄 Search: section ${sectionId} handled by OfflineAccordion`);
            }
            
            // Get all text content from the section
            let contentText = '';
            try {
                // Get text content excluding loading messages
                const contentNodes = content.querySelectorAll('*:not(.content-loading)');
                contentText = Array.from(contentNodes)
                    .map(node => node.textContent || '')
                    .join(' ')
                    .toLowerCase();
                
                // Also get direct text content
                const directText = content.textContent || '';
                contentText += ' ' + directText.toLowerCase();
            } catch (error) {
                console.warn(`Error getting content for search in ${sectionName}:`, error);
                contentText = content.textContent?.toLowerCase() || '';
            }
            
            // Search in title, section name, and content
            const titleMatch = title.includes(query);
            const sectionMatch = sectionName.includes(query);
            const contentMatch = contentText.includes(query);
            
            if (titleMatch || sectionMatch || contentMatch) {
                item.classList.remove('filtered-out');
                categoryHasResults = true;
                foundResults = true;
                resultsCount++;
                
                // Highlight the match in title
                if (titleMatch) {
                    highlightSearchTerm(item.querySelector('.item-title'), query);
                } else {
                    // If match is in content, show normal title but mark as content match
                    removeHighlight(item.querySelector('.item-title'));
                    const titleElement = item.querySelector('.item-title');
                    titleElement.setAttribute('data-content-match', 'true');
                }
                
                // Auto-expand category and potentially the item
                const categoryToggle = category.querySelector('.category-toggle');
                const itemToggle = item.querySelector('.item-toggle');
                
                if (categoryToggle.getAttribute('aria-expanded') !== 'true') {
                    toggleCategory(categoryToggle);
                }
                
                // If match is in content (not just title), expand the item to show content
                if (contentMatch && !titleMatch) {
                    if (itemToggle.getAttribute('aria-expanded') !== 'true') {
                        await toggleAccordionItem(itemToggle);
                    }
                    
                    // Highlight matches in content
                    setTimeout(() => {
                        highlightContentMatches(content, query);
                    }, 300);
                }
                
            } else {
                item.classList.add('filtered-out');
                removeHighlight(item.querySelector('.item-title'));
                item.querySelector('.item-title').removeAttribute('data-content-match');
            }
        }
        
        // Show/hide category based on results
        if (categoryHasResults) {
            category.classList.remove('filtered-out');
        } else {
            category.classList.add('filtered-out');
        }
    }
    
    // Show no results message
    showSearchResults(foundResults, resultsCount, query);
    
    logEvent('search_performed', {
        query: query,
        results: resultsCount
    });
}

function highlightSearchTerm(element, term) {
    const text = element.textContent;
    const regex = new RegExp(`(${term})`, 'gi');
    const highlightedText = text.replace(regex, '<span class="search-highlight">$1</span>');
    element.innerHTML = highlightedText;
}

function highlightContentMatches(container, term) {
    // Remove previous highlights
    removeAllHighlights(container);
    
    const regex = new RegExp(`(${term})`, 'gi');
    const walker = document.createTreeWalker(
        container,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                // Skip script, style, and already highlighted content
                const parent = node.parentElement;
                if (parent.tagName === 'SCRIPT' || 
                    parent.tagName === 'STYLE' || 
                    parent.classList.contains('search-highlight') ||
                    parent.classList.contains('content-loading')) {
                    return NodeFilter.FILTER_REJECT;
                }
                
                // Only process text nodes that contain the search term
                if (node.textContent.toLowerCase().includes(term)) {
                    return NodeFilter.FILTER_ACCEPT;
                }
                return NodeFilter.FILTER_REJECT;
            }
        }
    );
    
    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    // Process text nodes in reverse to avoid DOM position issues
    textNodes.reverse().forEach(textNode => {
        const text = textNode.textContent;
        if (regex.test(text)) {
            const parent = textNode.parentNode;
            const highlightedHTML = text.replace(regex, '<span class="search-highlight">$1</span>');
            
            // Create a temporary container to hold the highlighted content
            const temp = document.createElement('div');
            temp.innerHTML = highlightedHTML;
            
            // Replace the text node with highlighted content
            while (temp.firstChild) {
                parent.insertBefore(temp.firstChild, textNode);
            }
            parent.removeChild(textNode);
        }
    });
    
    console.log(`✨ Highlighted ${textNodes.length} matches for "${term}" in content`);
}

function removeHighlight(element) {
    const text = element.textContent;
    element.innerHTML = text;
}

function removeAllHighlights(container) {
    const highlights = container.querySelectorAll('.search-highlight');
    highlights.forEach(highlight => {
        const parent = highlight.parentNode;
        parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        parent.normalize(); // Merge adjacent text nodes
    });
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    const accordion = document.getElementById('documentationAccordion');
    
    searchInput.value = '';
    
    // Show all items and categories
    const items = accordion.querySelectorAll('.accordion-item');
    const categories = accordion.querySelectorAll('.accordion-category');
    
    items.forEach(item => {
        item.classList.remove('filtered-out');
        removeHighlight(item.querySelector('.item-title'));
        item.querySelector('.item-title').removeAttribute('data-content-match');
        
        // Remove content highlights
        const content = item.querySelector('.item-content');
        if (content) {
            removeAllHighlights(content);
        }
    });
    
    categories.forEach(category => {
        category.classList.remove('filtered-out');
    });
    
    // Remove search results message
    const existingMessage = document.querySelector('.search-no-results');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    console.log('🧹 Search cleared');
}

function showSearchResults(found, count, query) {
    // Remove existing message
    const existingMessage = document.querySelector('.search-no-results');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    if (!found) {
        const accordion = document.getElementById('documentationAccordion');
        const message = document.createElement('div');
        message.className = 'search-no-results';
        message.innerHTML = `
            <h3>Nenhum resultado encontrado</h3>
            <p>Não foi possível encontrar seções relacionadas a "${query}"</p>
            <p><small>Tente termos como "api", "algoritmo", "arquitetura", "segurança"</small></p>
        `;
        accordion.appendChild(message);
    }
}

// ===== DEEP LINKING =====
function initializeDeepLinking() {
    // Handle hash on page load
    if (window.location.hash) {
        const hash = window.location.hash.substring(1);
        setTimeout(() => {
            navigateToSection(hash);
        }, 500);
    }
    
    // Handle hash changes
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.substring(1);
        if (hash) {
            navigateToSection(hash);
        }
    });
}

function navigateToSection(sectionName) {
    const item = document.querySelector(`[data-section="${sectionName}"]`);
    if (!item) return;
    
    const category = item.closest('.accordion-category');
    const categoryToggle = category.querySelector('.category-toggle');
    const itemToggle = item.querySelector('.item-toggle');
    
    // Expand category if needed
    if (categoryToggle.getAttribute('aria-expanded') !== 'true') {
        toggleCategory(categoryToggle);
    }
    
    // Expand item
    setTimeout(() => {
        if (itemToggle.getAttribute('aria-expanded') !== 'true') {
            toggleAccordionItem(itemToggle);
        }
    }, 300);
    
    console.log(`🔗 Navigated to section: ${sectionName}`);
}

function updateURLHash(sectionName) {
    const newHash = `#${sectionName}`;
    if (window.location.hash !== newHash) {
        history.replaceState(null, null, newHash);
    }
}

// ===== KEYBOARD NAVIGATION =====
document.addEventListener('keydown', (e) => {
    // ESC to close all sections
    if (e.key === 'Escape') {
        collapseAllSections();
    }
    
    // Ctrl+F to focus search
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// ===== PRINT OPTIMIZATION =====
function handlePrint() {
    console.log('🖨️ Preparing for print...');
    
    // Expand all sections for printing
    expandAllSections();
    
    // Wait for content to load, then print
    setTimeout(() => {
        window.print();
    }, 1000);
    
    logEvent('print_initiated');
}

// ===== READING MODE =====
function initReadingMode() {
    const readingBtn = document.getElementById('readingModeBtn');
    const readingModal = document.getElementById('readingModal');
    const readingContent = document.getElementById('readingContent');
    const readingNavList = document.getElementById('readingNavList');
    const readingModalBody = document.getElementById('readingModalBody');
    const backToTopBtn = document.getElementById('backToTopBtn');
    const readingProgress = document.getElementById('readingProgress');
    const readingProgressText = document.getElementById('readingProgressText');
    const toggleSidebar = document.getElementById('toggleSidebar');
    const readingSidebar = document.getElementById('readingSidebar');
    
    if (!readingBtn || !readingModal) return;
    
    // Open reading mode
    readingBtn.addEventListener('click', () => {
        console.log('📚 Opening reading mode...');
        openReadingMode();
    });
    
    // Toggle sidebar on mobile
    if (toggleSidebar && readingSidebar) {
        toggleSidebar.addEventListener('click', () => {
            readingSidebar.classList.toggle('show-mobile');
            toggleSidebar.textContent = readingSidebar.classList.contains('show-mobile') ? '✕' : '☰';
        });
    }
    
    // Setup sidebar toggle in header
    const headerSidebarToggle = document.getElementById('readingSidebarToggle');
    if (headerSidebarToggle && readingSidebar) {
        headerSidebarToggle.addEventListener('click', () => {
            readingSidebar.classList.toggle('show-mobile');
            headerSidebarToggle.textContent = readingSidebar.classList.contains('show-mobile') ? '✕' : '☰';
        });
    }
    
    // Setup close button
    const closeButton = document.getElementById('readingCloseButton');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            exitReadingMode();
        });
    }
    
    // Setup back to main button
    const backToMainButton = document.getElementById('readingBackToMainHeader');
    if (backToMainButton) {
        backToMainButton.addEventListener('click', () => {
            exitReadingMode();
        });
    }
    
    // Initialize reading mode controls
    initReadingModeControls();
    
    function exitReadingMode() {
        // Disable reading mode
        document.body.classList.remove('reading-mode');
        
        // Hide reading mode elements in header
        document.getElementById('readingProgressIndicator').style.display = 'none';
        document.getElementById('readingCloseButton').style.display = 'none';
        document.getElementById('readingSidebarToggle').style.display = 'none';
        document.getElementById('readingBackToMainHeader').style.display = 'none';
        
        // Close modal
        closeModal('readingModal');
    }
    
    async function ensureModularContentLoaded() {
        // Ensure ContentManager is initialized
        if (!window.contentManager || !window.contentManager.initialized) {
            console.log('⏳ Waiting for ContentManager initialization...');
            await new Promise(resolve => {
                const checkInit = () => {
                    if (window.contentManager && window.contentManager.initialized) {
                        resolve();
                    } else {
                        setTimeout(checkInit, 100);
                    }
                };
                checkInit();
            });
        }
        
        // Ensure current language is available globally for ContentManager
        window.currentLanguage = currentLanguage;
        
        // Load all modular sections in the current language
        const modularSections = ['math-foundations', 'xai-algorithms'];
        const loadPromises = modularSections.map(sectionId => {
            const container = document.querySelector(`[data-section="${sectionId}"] .item-content`);
            if (container) {
                // Always reload to ensure correct language content
                const children = Array.from(container.children);
                children.forEach(child => {
                    if (!child.classList.contains('content-loading')) {
                        child.remove();
                    }
                });
                
                console.log(`📄 Reading mode: section ${sectionId} handled by OfflineAccordion`);
                return Promise.resolve();
            }
            return Promise.resolve();
        });
        
        await Promise.all(loadPromises);
        console.log(`✅ All modular content loaded for reading mode in ${currentLanguage}`);
    }
    
    function buildReadingContent(sectionData) {
        let sectionCounter = 0; // For main sections (1, 2, 3...)
        
        sectionData.forEach((section, index) => {
            sectionCounter++;
            const mainNumber = sectionCounter;
            
            // Add section to content with hierarchical numbering
            const sectionDiv = document.createElement('div');
            sectionDiv.id = section.id;
            sectionDiv.className = 'reading-section';
            
            // Process content to add numbering to internal headers
            const processedContent = addHierarchicalNumbering(section.content, mainNumber);
            
            sectionDiv.innerHTML = `
                <h2>${mainNumber}. ${section.title}</h2>
                ${processedContent}
            `;
            readingContent.appendChild(sectionDiv);
            
            // Add navigation link
            const navLink = document.createElement('a');
            navLink.href = `#${section.id}`;
            navLink.className = 'reading-nav-item';
            navLink.innerHTML = `<span class="nav-number">${mainNumber}.</span> ${section.title}`;
            navLink.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.getElementById(section.id);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
            readingNavList.appendChild(navLink);
        });
        
        // Open modal
        openModal('readingModal');
        
        // Setup scroll tracking
        setupScrollTracking();
        
        logEvent('reading_mode_opened', { sections: sectionData.length });
    }

    function addHierarchicalNumbering(content, mainNumber) {
        // Create a temporary div to parse HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        
        let h3Counter = 0;
        let h4Counter = 0;
        let currentH3 = 0;
        
        // Process H3 headers (1.1, 1.2, 1.3...)
        const h3Elements = tempDiv.querySelectorAll('h3');
        h3Elements.forEach((h3, index) => {
            h3Counter++;
            currentH3 = h3Counter;
            h4Counter = 0; // Reset h4 counter when new h3
            h3.innerHTML = `${mainNumber}.${h3Counter}. ${h3.textContent}`;
        });
        
        // Process H4 headers (1.1.1, 1.1.2, 1.2.1...)
        const h4Elements = tempDiv.querySelectorAll('h4');
        h4Elements.forEach((h4, index) => {
            // Find which h3 this h4 belongs to
            let belongsToH3 = 1;
            const prevH3 = h4.previousElementSibling;
            if (prevH3) {
                const h3Before = tempDiv.querySelector('h3');
                if (h3Before) {
                    const h3Text = h3Before.textContent;
                    const match = h3Text.match(/(\d+)\.(\d+)\./);
                    if (match) {
                        belongsToH3 = parseInt(match[2]);
                    }
                }
            }
            
            h4Counter++;
            h4.innerHTML = `${mainNumber}.${belongsToH3}.${h4Counter}. ${h4.textContent}`;
        });
        
        return tempDiv.innerHTML;
    }

    async function refreshReadingModeContent() {
        // This function refreshes reading mode content when language changes
        if (!document.body.classList.contains('reading-mode')) return;
        
        console.log(`🔄 Refreshing reading mode content for ${currentLanguage}`);
        
        // Clear previous content
        readingContent.innerHTML = '';
        readingNavList.innerHTML = '';
        
        // Wait for ContentManager to load all modular sections
        await ensureModularContentLoaded();
        
        // Get all sections content again with updated language
        const sections = document.querySelectorAll('.accordion-item');
        const sectionData = [];
        
        sections.forEach((section, index) => {
            const sectionName = section.dataset.section;
            const title = section.querySelector('.item-title').textContent;
            const content = section.querySelector('.item-content').innerHTML;
            
            if (content && content.trim() !== '') {
                sectionData.push({
                    id: `reading-section-${index}`,
                    name: sectionName,
                    title: title,
                    content: content
                });
            }
        });
        
        // Rebuild reading content (but don't reopen modal or setup tracking)
        let sectionCounter = 0;
        sectionData.forEach((section, index) => {
            sectionCounter++;
            const mainNumber = sectionCounter;
            
            const sectionDiv = document.createElement('div');
            sectionDiv.id = section.id;
            sectionDiv.className = 'reading-section';
            
            const processedContent = addHierarchicalNumbering(section.content, mainNumber);
            
            sectionDiv.innerHTML = `
                <h2>${mainNumber}. ${section.title}</h2>
                ${processedContent}
            `;
            readingContent.appendChild(sectionDiv);
            
            const navLink = document.createElement('a');
            navLink.href = `#${section.id}`;
            navLink.className = 'reading-nav-item';
            navLink.innerHTML = `<span class="nav-number">${mainNumber}.</span> ${section.title}`;
            navLink.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.getElementById(section.id);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
            readingNavList.appendChild(navLink);
        });
        
        console.log(`✅ Reading mode content refreshed for ${currentLanguage}`);
    }

    async function openReadingMode() {
        // Enable reading mode
        document.body.classList.add('reading-mode');
        
        // Show reading mode elements in header
        document.getElementById('readingProgressIndicator').style.display = 'block';
        document.getElementById('readingCloseButton').style.display = 'block';
        document.getElementById('readingBackToMainHeader').style.display = 'block';
        
        // Show sidebar toggle on mobile
        const sidebarToggle = document.getElementById('readingSidebarToggle');
        if (window.innerWidth <= 768) {
            sidebarToggle.style.display = 'block';
        }
        
        // Clear previous content
        readingContent.innerHTML = '';
        readingNavList.innerHTML = '';
        
        // Wait for ContentManager to load all modular sections
        await ensureModularContentLoaded();
        
        // Get all sections content
        const sections = document.querySelectorAll('.accordion-item');
        const sectionData = [];
        
        sections.forEach((section, index) => {
            const sectionName = section.dataset.section;
            const title = section.querySelector('.item-title').textContent;
            const content = section.querySelector('.item-content').innerHTML;
            
            if (content && content.trim() !== '') {
                sectionData.push({
                    id: `reading-section-${index}`,
                    name: sectionName,
                    title: title,
                    content: content
                });
            }
        });
        
        // Build reading content
        buildReadingContent(sectionData);
    }
    
    function setupScrollTracking() {
        let ticking = false;
        
        function updateProgress() {
            const scrollTop = readingModalBody.scrollTop;
            const scrollHeight = readingModalBody.scrollHeight - readingModalBody.clientHeight;
            const scrollPercentage = Math.round((scrollTop / scrollHeight) * 100);
            
            // Update progress bar
            readingProgress.style.width = `${scrollPercentage}%`;
            const progressSuffix = currentLanguage === 'en-US' ? '% read' : '% lido';
            readingProgressText.textContent = `${scrollPercentage}${progressSuffix}`;
            
            // Update active nav item
            updateActiveNavItem(scrollTop);
            
            // Show/hide back to top button
            if (scrollTop > 500) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
            
            ticking = false;
        }
        
        function updateActiveNavItem(scrollTop) {
            const sections = readingContent.querySelectorAll('.reading-section');
            const navItems = readingNavList.querySelectorAll('.reading-nav-item');
            
            sections.forEach((section, index) => {
                const rect = section.getBoundingClientRect();
                const top = rect.top + scrollTop - 100;
                const bottom = top + rect.height;
                
                if (scrollTop >= top && scrollTop < bottom) {
                    navItems.forEach(item => item.classList.remove('active'));
                    if (navItems[index]) {
                        navItems[index].classList.add('active');
                    }
                }
            });
        }
        
        // Scroll event
        readingModalBody.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateProgress);
                ticking = true;
            }
        });
        
        // Back to top button
        backToTopBtn.addEventListener('click', () => {
            readingModalBody.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        // Initial update
        updateProgress();
    }
    
    function initReadingModeControls() {
        // Theme controls for reading mode
        const readingThemeButtons = document.querySelectorAll('[data-reading-theme-btn]');
        readingThemeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const theme = button.dataset.readingThemeBtn;
                switchTheme(theme);
                updateReadingThemeButtons(theme);
            });
        });
        
        // Language controls for reading mode
        const readingLangButtons = document.querySelectorAll('[data-reading-lang-btn]');
        readingLangButtons.forEach(button => {
            button.addEventListener('click', () => {
                const lang = button.dataset.readingLangBtn;
                switchLanguage(lang);
                updateReadingLanguageButtons(lang);
            });
        });
        
        // Initialize with current theme and language
        updateReadingThemeButtons(currentTheme);
        updateReadingLanguageButtons(currentLanguage);
    }
    
    function updateReadingThemeButtons(activeTheme) {
        const buttons = document.querySelectorAll('[data-reading-theme-btn]');
        buttons.forEach(button => {
            if (button.dataset.readingThemeBtn === activeTheme) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }
    
    function updateReadingLanguageButtons(activeLang) {
        const buttons = document.querySelectorAll('[data-reading-lang-btn]');
        buttons.forEach(button => {
            if (button.dataset.readingLangBtn === activeLang) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }
}

// ===== PROGRESS TRACKING =====
let readSections = new Set();

function markSectionAsRead(sectionName) {
    readSections.add(sectionName);
    localStorage.setItem('cidadao-read-sections', JSON.stringify([...readSections]));
    updateProgressIndicator();
}

function updateProgressIndicator() {
    const totalSections = 24;
    const readCount = readSections.size;
    const percentage = Math.round((readCount / totalSections) * 100);
    
    // Update progress in title or create indicator
    console.log(`📊 Reading progress: ${readCount}/${totalSections} (${percentage}%)`);
}

// Initialize read sections from localStorage
function initializeProgressTracking() {
    const saved = localStorage.getItem('cidadao-read-sections');
    if (saved) {
        readSections = new Set(JSON.parse(saved));
        updateProgressIndicator();
    }
}

// ===== UTILITÁRIOS =====
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

// ===== ANALYTICS & LOGGING =====
function logEvent(event, data = {}) {
    console.log(`📊 Event: ${event}`, data);
    
    // Aqui poderia integrar com analytics reais
    // analytics.track(event, data);
}

// ===== ACESSIBILIDADE =====
document.addEventListener('keydown', function(e) {
    // Tab navigation melhorada
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});

// ===== PERFORMANCE =====
// Lazy loading de imagens (se houver)
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => imageObserver.observe(img));
}

// ===== SERVICE WORKER (opcional) =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Registrar service worker apenas em produção
        if (location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('🔧 SW registered:', registration);
                })
                .catch(error => {
                    console.log('❌ SW registration failed:', error);
                });
        }
    });
}

// ===== EXPORTAR FUNÇÕES GLOBAIS =====
window.CidadaoAI = {
    switchTheme,
    switchLanguage,
    openModal,
    closeModal,
    logEvent
};

console.log('✅ Cidadão.AI Backend Documentation JS loaded successfully');