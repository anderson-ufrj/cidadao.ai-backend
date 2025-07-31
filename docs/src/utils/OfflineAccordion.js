/**
 * OfflineAccordion.js
 * Versão do SuperAccordion que funciona sem servidor HTTP
 * Carrega dados diretamente dos arquivos existentes
 */

class OfflineAccordion {
    constructor(options = {}) {
        this.options = {
            containerSelector: '#documentationAccordion',
            searchMinLength: 2,
            debounceDelay: 300,
            animationDuration: 300,
            ...options
        };

        // Estado interno
        this.state = {
            initialized: false,
            currentLanguage: 'pt-BR',
            currentTheme: 'light',
            readingMode: false,
            searchActive: false,
            searchQuery: '',
            activeSection: null
        };

        // Dados das categorias e seções (hardcoded para funcionar offline)
        this.categories = new Map([
            ['fundamentacao', {
                id: 'fundamentacao',
                icon: '📚',
                title: { 'pt-BR': 'Fundamentação Teórica', 'en-US': 'Theoretical Foundation' },
                order: 1,
                files: [
                    { id: 'overview', title: 'Visão Geral do Sistema', preview: 'Visão geral do sistema multi-agente...', wordCount: 1200 },
                    { id: 'theoretical-foundations', title: 'Fundamentos Teóricos', preview: 'Base teórica do projeto...', wordCount: 980 },
                    { id: 'literature-review', title: 'Revisão da Literatura', preview: 'Revisão bibliográfica completa...', wordCount: 1500 },
                    { id: 'methodology', title: 'Metodologia', preview: 'Metodologia de pesquisa aplicada...', wordCount: 1100 }
                ]
            }],
            ['arquitetura', {
                id: 'arquitetura',
                icon: '🏗️',
                title: { 'pt-BR': 'Arquitetura & Implementação', 'en-US': 'Architecture & Implementation' },
                order: 2,
                files: [
                    { id: 'system-architecture', title: 'Arquitetura do Sistema', preview: 'Arquitetura geral do sistema...', wordCount: 1800 },
                    { id: 'multi-agent-system', title: 'Sistema Multi-Agente', preview: 'Implementação do sistema de agentes...', wordCount: 2200 },
                    { id: 'data-pipeline', title: 'Pipeline de Dados', preview: 'Processamento e fluxo de dados...', wordCount: 1400 },
                    { id: 'technical-implementation', title: 'Implementação Técnica', preview: 'Detalhes técnicos da implementação...', wordCount: 1900 }
                ]
            }],
            ['ia', {
                id: 'ia',
                icon: '🤖',
                title: { 'pt-BR': 'Inteligência Artificial & ML', 'en-US': 'Artificial Intelligence & ML' },
                order: 3,
                files: [
                    { id: 'algorithms', title: 'Algoritmos', preview: 'Algoritmos de ML implementados...', wordCount: 1600 },
                    { id: 'mathematical-proofs', title: 'Provas Matemáticas', preview: 'Demonstrações matemáticas...', wordCount: 1300 },
                    { id: 'math-foundations', title: 'Fundamentos Matemáticos', preview: 'Base matemática do sistema...', wordCount: 1700 },
                    { id: 'xai-algorithms', title: 'Algoritmos XAI', preview: 'Explicabilidade da IA...', wordCount: 1200 }
                ]
            }],
            ['api', {
                id: 'api',
                icon: '🔌',
                title: { 'pt-BR': 'API & Integração', 'en-US': 'API & Integration' },
                order: 4,
                files: [
                    { id: 'api-reference', title: 'Referência da API', preview: 'Documentação completa da API...', wordCount: 2100 },
                    { id: 'code-examples', title: 'Exemplos de Código', preview: 'Exemplos práticos de uso...', wordCount: 1500 },
                    { id: 'datasets', title: 'Conjuntos de Dados', preview: 'Datasets utilizados no projeto...', wordCount: 800 }
                ]
            }],
            ['validacao', {
                id: 'validacao',
                icon: '✅',
                title: { 'pt-BR': 'Validação & Resultados', 'en-US': 'Validation & Results' },
                order: 5,
                files: [
                    { id: 'validation', title: 'Validação', preview: 'Processo de validação do sistema...', wordCount: 1400 },
                    { id: 'benchmarks', title: 'Benchmarks', preview: 'Testes de performance...', wordCount: 1100 },
                    { id: 'experimental-design', title: 'Design Experimental', preview: 'Metodologia experimental...', wordCount: 1300 },
                    { id: 'performance', title: 'Performance', preview: 'Análise de performance...', wordCount: 900 },
                    { id: 'case-studies', title: 'Estudos de Caso', preview: 'Casos de uso reais...', wordCount: 1600 }
                ]
            }],
            ['conclusao', {
                id: 'conclusao',
                icon: '🎯',
                title: { 'pt-BR': 'Conclusão & Trabalhos Futuros', 'en-US': 'Conclusion & Future Work' },
                order: 6,
                files: [
                    { id: 'conclusion', title: 'Conclusão', preview: 'Conclusões do projeto...', wordCount: 1200 },
                    { id: 'contributions', title: 'Contribuições', preview: 'Contribuições científicas...', wordCount: 800 },
                    { id: 'future-work', title: 'Trabalhos Futuros', preview: 'Direções futuras...', wordCount: 700 },
                    { id: 'limitations', title: 'Limitações', preview: 'Limitações identificadas...', wordCount: 600 },
                    { id: 'bibliography', title: 'Bibliografia', preview: 'Referências bibliográficas...', wordCount: 400 },
                    { id: 'security', title: 'Segurança', preview: 'Aspectos de segurança...', wordCount: 1000 }
                ]
            }]
        ]);

        // Elementos DOM
        this.elements = {};
        
        // Debounced functions
        this.debouncedSearch = this.debounce(this.performSearch.bind(this), this.options.debounceDelay);
        
        console.log('🚀 OfflineAccordion initialized');
    }

    /**
     * Inicialização principal
     */
    async init() {
        if (this.state.initialized) return;
        
        console.log('🔄 Inicializando OfflineAccordion...');
        
        try {
            // 1. Detectar estado inicial
            this.detectInitialState();
            
            // 2. Criar estrutura DOM
            await this.createDOMStructure();
            
            // 3. Renderizar accordion
            await this.renderAccordion();
            
            // 4. Configurar event listeners
            this.setupEventListeners();
            
            // 5. Sincronizar com controles existentes
            this.syncWithHeaderControls();
            
            this.state.initialized = true;
            console.log('✅ OfflineAccordion inicializado com sucesso!');
            
        } catch (error) {
            console.error('❌ Erro ao inicializar OfflineAccordion:', error);
            this.showErrorState();
        }
    }

    /**
     * Detecta estado inicial do sistema
     */
    detectInitialState() {
        // Detectar tema atual
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark' ||
                      document.body.classList.contains('dark-theme') ||
                      window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        this.state.currentTheme = isDark ? 'dark' : 'light';
        
        // Detectar idioma atual
        const htmlLang = document.documentElement.lang;
        const savedLang = localStorage.getItem('preferred-language');
        
        this.state.currentLanguage = savedLang || htmlLang || 'pt-BR';
        
        console.log(`🎨 Estado inicial: tema=${this.state.currentTheme}, idioma=${this.state.currentLanguage}`);
    }

    /**
     * Cria estrutura DOM do accordion
     */
    async createDOMStructure() {
        const container = document.querySelector(this.options.containerSelector);
        if (!container) {
            throw new Error(`Container ${this.options.containerSelector} não encontrado`);
        }

        container.innerHTML = `
            <!-- Container do Accordion (usa controles existentes do HTML) -->
            <div class="offline-accordion-container">
                <!-- Loading state -->
                <div class="accordion-loading">
                    <div class="loading-spinner"></div>
                    <p>Carregando documentação...</p>
                </div>
            </div>

            <!-- Modo Leitura -->
            <div class="reading-mode-container" style="display: none;">
                <div class="reading-mode-header">
                    <button class="reading-mode-close">✕</button>
                    <div class="reading-mode-navigation">
                        <button class="reading-nav-btn reading-prev">⬅️</button>
                        <span class="reading-mode-title"></span>
                        <button class="reading-nav-btn reading-next">➡️</button>
                    </div>
                    <div class="reading-mode-progress">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <span class="progress-text">0%</span>
                    </div>
                </div>
                <div class="reading-mode-content">
                    <!-- Conteúdo será carregado aqui -->
                </div>
            </div>
        `;

        // Armazenar referências dos elementos (usa controles existentes do HTML)
        this.elements = {
            container: container,
            accordionContainer: container.querySelector('.offline-accordion-container'),
            // Controles existentes no HTML
            searchInput: document.getElementById('searchInput'),
            searchClear: document.getElementById('searchClear'),
            expandAll: document.querySelector('.expand-all'),
            collapseAll: document.querySelector('.collapse-all'),
            readingModeToggle: document.getElementById('readingModeBtn'),
            printBtn: document.getElementById('printBtn'),
            // Elementos do accordion
            readingModeContainer: container.querySelector('.reading-mode-container'),
            readingModeContent: container.querySelector('.reading-mode-content'),
            readingModeTitle: container.querySelector('.reading-mode-title'),
            readingPrev: container.querySelector('.reading-prev'),
            readingNext: container.querySelector('.reading-next'),
            readingModeClose: container.querySelector('.reading-mode-close'),
            progressFill: container.querySelector('.progress-fill'),
            progressText: container.querySelector('.progress-text'),
            loading: container.querySelector('.accordion-loading')
        };
    }

    /**
     * Renderiza o accordion completo
     */
    async renderAccordion() {
        console.log('🎨 Renderizando accordion...');
        
        const container = this.elements.accordionContainer;
        container.innerHTML = '';
        
        // Criar categorias ordenadas
        const sortedCategories = Array.from(this.categories.values())
            .sort((a, b) => a.order - b.order);
        
        for (const category of sortedCategories) {
            const categoryElement = this.createCategoryElement(category);
            container.appendChild(categoryElement);
        }
        
        // Esconder loading
        this.elements.loading.style.display = 'none';
        
        console.log('✅ Accordion renderizado com sucesso!');
    }

    /**
     * Cria elemento de categoria
     */
    createCategoryElement(category) {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'accordion-category';
        categoryDiv.setAttribute('data-category', category.id);
        
        const categoryTitle = category.title[this.state.currentLanguage] || category.title['pt-BR'];
        
        categoryDiv.innerHTML = `
            <div class="category-header" role="button" tabindex="0" aria-expanded="false">
                <span class="category-icon">${category.icon}</span>
                <span class="category-title">${categoryTitle}</span>
                <span class="category-count">(${category.files.length})</span>
                <span class="category-arrow">▶</span>
            </div>
            <div class="category-content" style="display: none;">
                ${category.files.map(file => this.createSectionElement(file)).join('')}
            </div>
        `;
        
        return categoryDiv;
    }

    /**
     * Cria elemento de seção
     */
    createSectionElement(file) {
        return `
            <div class="accordion-section" data-section="${file.id}" data-category="${file.category || 'unknown'}">
                <div class="section-header" role="button" tabindex="0" aria-expanded="false">
                    <span class="section-title">${file.title}</span>
                    <div class="section-meta">
                        <span class="section-words">${file.wordCount} palavras</span>
                    </div>
                    <span class="section-toggle">▼</span>
                </div>
                <div class="section-content" style="display: none;">
                    <div class="section-demo-content">
                        <h3>${file.title}</h3>
                        <p><strong>Preview:</strong> ${file.preview}</p>
                        <p><em>Esta é uma versão de demonstração. O conteúdo completo seria carregado de ${file.id}.mdx</em></p>
                        <div class="demo-actions">
                            <button class="demo-btn" onclick="alert('Modo leitura para: ${file.title}')">📖 Ler Completo</button>
                            <button class="demo-btn" onclick="alert('Exportar: ${file.title}')">📄 Exportar</button>
                        </div>
                    </div>
                </div>
                <div class="section-preview">
                    <p class="preview-text">${file.preview}</p>
                    <button class="preview-read-more">Ler mais</button>
                </div>
            </div>
        `;
    }

    /**
     * Configura todos os event listeners
     */
    setupEventListeners() {
        console.log('🎧 Configurando event listeners...');
        
        // Controles existentes do HTML
        this.elements.searchInput?.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });
        
        this.elements.searchClear?.addEventListener('click', () => {
            this.clearSearch();
        });
        
        this.elements.expandAll?.addEventListener('click', () => {
            this.expandAllSections();
        });
        
        this.elements.collapseAll?.addEventListener('click', () => {
            this.collapseAllSections();
        });
        
        this.elements.readingModeToggle?.addEventListener('click', () => {
            this.toggleReadingMode();
        });
        
        this.elements.printBtn?.addEventListener('click', () => {
            this.handlePrint();
        });
        
        // Modo leitura
        this.elements.readingModeClose?.addEventListener('click', () => {
            this.exitReadingMode();
        });
        
        this.elements.readingPrev?.addEventListener('click', () => {
            this.navigateReading('prev');
        });
        
        this.elements.readingNext?.addEventListener('click', () => {
            this.navigateReading('next');
        });
        
        // Event delegation para accordion
        this.elements.accordionContainer?.addEventListener('click', (e) => {
            this.handleAccordionClick(e);
        });
        
        // Teclado
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
        
        console.log('✅ Event listeners configurados!');
    }

    /**
     * Sincroniza com controles do header existente
     */
    syncWithHeaderControls() {
        console.log('🔗 Sincronizando com controles do header...');
        
        // Observar mudanças de tema
        const themeObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    this.handleThemeChange();
                }
            });
        });
        
        themeObserver.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
        
        console.log('✅ Sincronização configurada!');
    }

    /**
     * Manipula cliques no accordion
     */
    handleAccordionClick(e) {
        const target = e.target.closest('[role="button"]');
        if (!target) return;
        
        if (target.classList.contains('category-header')) {
            this.toggleCategory(target.parentElement);
        } else if (target.classList.contains('section-header')) {
            this.toggleSection(target.parentElement);
        } else if (target.classList.contains('preview-read-more')) {
            const section = target.closest('.accordion-section');
            this.openSectionInReadingMode(section);
        }
    }

    /**
     * Alterna categoria
     */
    toggleCategory(categoryEl) {
        const content = categoryEl.querySelector('.category-content');
        const header = categoryEl.querySelector('.category-header');
        const arrow = categoryEl.querySelector('.category-arrow');
        
        const isExpanded = header.getAttribute('aria-expanded') === 'true';
        
        if (isExpanded) {
            this.collapseCategory(categoryEl);
        } else {
            this.expandCategory(categoryEl);
        }
    }

    /**
     * Expande categoria
     */
    expandCategory(categoryEl) {
        const content = categoryEl.querySelector('.category-content');
        const header = categoryEl.querySelector('.category-header');
        const arrow = categoryEl.querySelector('.category-arrow');
        
        header.setAttribute('aria-expanded', 'true');
        content.style.display = 'block';
        arrow.textContent = '▼';
        
        // Auto-expandir todas as seções desta categoria
        const sections = categoryEl.querySelectorAll('.accordion-section');
        sections.forEach(async (sectionEl) => {
            await this.expandSection(sectionEl);
        });
        
        // Animação suave
        setTimeout(() => {
            content.style.maxHeight = content.scrollHeight + 'px';
        }, 100); // Pequeno delay para calcular altura correta após expandir seções
    }

    /**
     * Colapsa categoria
     */
    collapseCategory(categoryEl) {
        const content = categoryEl.querySelector('.category-content');
        const header = categoryEl.querySelector('.category-header');
        const arrow = categoryEl.querySelector('.category-arrow');
        
        // Colapsar todas as seções desta categoria primeiro
        const sections = categoryEl.querySelectorAll('.accordion-section');
        sections.forEach((sectionEl) => {
            this.collapseSection(sectionEl);
        });
        
        header.setAttribute('aria-expanded', 'false');
        arrow.textContent = '▶';
        
        // Animação suave
        content.style.maxHeight = '0px';
        setTimeout(() => {
            if (header.getAttribute('aria-expanded') === 'false') {
                content.style.display = 'none';
            }
        }, this.options.animationDuration);
    }

    /**
     * Alterna seção
     */
    async toggleSection(sectionEl) {
        const content = sectionEl.querySelector('.section-content');
        const header = sectionEl.querySelector('.section-header');
        const toggle = sectionEl.querySelector('.section-toggle');
        
        const isExpanded = header.getAttribute('aria-expanded') === 'true';
        
        if (isExpanded) {
            this.collapseSection(sectionEl);
        } else {
            await this.expandSection(sectionEl);
        }
    }

    /**
     * Expande seção
     */
    async expandSection(sectionEl) {
        const content = sectionEl.querySelector('.section-content');
        const header = sectionEl.querySelector('.section-header');
        const toggle = sectionEl.querySelector('.section-toggle');
        
        header.setAttribute('aria-expanded', 'true');
        content.style.display = 'block';
        toggle.textContent = '▲';
        
        // Animação suave
        content.style.maxHeight = content.scrollHeight + 'px';
    }

    /**
     * Colapsa seção
     */
    collapseSection(sectionEl) {
        const content = sectionEl.querySelector('.section-content');
        const header = sectionEl.querySelector('.section-header');
        const toggle = sectionEl.querySelector('.section-toggle');
        
        header.setAttribute('aria-expanded', 'false');
        toggle.textContent = '▼';
        
        // Animação suave
        content.style.maxHeight = '0px';
        setTimeout(() => {
            if (header.getAttribute('aria-expanded') === 'false') {
                content.style.display = 'none';
            }
        }, this.options.animationDuration);
    }

    /**
     * Manipula entrada de pesquisa (integração com search existente)
     */
    handleSearchInput(query) {
        this.state.searchQuery = query.trim().toLowerCase();
        
        if (this.state.searchQuery.length >= this.options.searchMinLength) {
            this.state.searchActive = true;
            this.debouncedSearch(this.state.searchQuery);
        } else {
            this.clearSearchResults();
        }
    }

    /**
     * Realiza a pesquisa
     */
    async performSearch(query) {
        console.log(`🔍 Pesquisando: "${query}"`);
        
        const categories = this.elements.accordionContainer.querySelectorAll('.accordion-category');
        let totalResults = 0;
        
        categories.forEach(categoryEl => {
            const categoryId = categoryEl.getAttribute('data-category');
            const sections = categoryEl.querySelectorAll('.accordion-section');
            let categoryHasResults = false;
            
            sections.forEach(sectionEl => {
                const title = sectionEl.querySelector('.section-title').textContent.toLowerCase();
                const preview = sectionEl.querySelector('.preview-text').textContent.toLowerCase();
                
                const hasMatch = title.includes(query) || preview.includes(query);
                
                if (hasMatch) {
                    sectionEl.style.display = 'block';
                    this.highlightSearchText(sectionEl, query);
                    categoryHasResults = true;
                    totalResults++;
                } else {
                    sectionEl.style.display = 'none';
                }
            });
            
            if (categoryHasResults) {
                categoryEl.style.display = 'block';
                this.expandCategory(categoryEl);
            } else {
                categoryEl.style.display = 'none';
            }
        });
        
        console.log(`✅ Pesquisa concluída: ${totalResults} resultados para "${query}"`);
    }

    /**
     * Destaca texto da pesquisa
     */
    highlightSearchText(element, query) {
        const textElements = element.querySelectorAll('.section-title, .preview-text');
        
        textElements.forEach(textEl => {
            const text = textEl.textContent;
            const highlightedText = text.replace(
                new RegExp(`(${query})`, 'gi'),
                '<mark class="search-highlight">$1</mark>'
            );
            textEl.innerHTML = highlightedText;
        });
    }

    /**
     * Limpa pesquisa completamente
     */
    clearSearch() {
        if (this.elements.searchInput) {
            this.elements.searchInput.value = '';
        }
        this.clearSearchResults();
    }

    /**
     * Manipula impressão
     */
    handlePrint() {
        // Expandir tudo antes de imprimir
        this.expandAllSections();
        
        // Aguardar animações e imprimir
        setTimeout(() => {
            window.print();
        }, 500);
    }

    /**
     * Limpa resultados da pesquisa
     */
    clearSearchResults() {
        this.state.searchActive = false;
        this.state.searchQuery = '';
        
        // Restaurar visibilidade completa
        const categories = this.elements.accordionContainer.querySelectorAll('.accordion-category');
        categories.forEach(categoryEl => {
            categoryEl.style.display = 'block';
            
            const sections = categoryEl.querySelectorAll('.accordion-section');
            sections.forEach(sectionEl => {
                sectionEl.style.display = 'block';
                
                // Remover highlights
                const highlighted = sectionEl.querySelectorAll('.search-highlight');
                highlighted.forEach(mark => {
                    mark.outerHTML = mark.innerHTML;
                });
            });
        });
    }

    /**
     * Modo leitura
     */
    toggleReadingMode() {
        if (this.state.readingMode) {
            this.exitReadingMode();
        } else {
            this.enterReadingMode();
        }
    }

    /**
     * Entra no modo leitura
     */
    enterReadingMode() {
        this.state.readingMode = true;
        this.elements.readingModeContainer.style.display = 'block';
        document.body.classList.add('reading-mode-active');
        
        // Esconder accordion principal
        this.elements.accordionContainer.style.display = 'none';
        
        // Carregar primeira seção
        this.loadFirstSectionInReadingMode();
        
        console.log('📖 Modo leitura ativado');
    }

    /**
     * Sai do modo leitura
     */
    exitReadingMode() {
        this.state.readingMode = false;
        this.elements.readingModeContainer.style.display = 'none';
        document.body.classList.remove('reading-mode-active');
        
        // Mostrar accordion principal
        this.elements.accordionContainer.style.display = 'block';
        
        console.log('📖 Modo leitura desativado');
    }

    /**
     * Carrega primeira seção no modo leitura
     */
    async loadFirstSectionInReadingMode() {
        const firstSection = this.elements.accordionContainer.querySelector('.accordion-section');
        if (firstSection) {
            await this.openSectionInReadingMode(firstSection);
        }
    }

    /**
     * Abre seção no modo leitura
     */
    async openSectionInReadingMode(sectionEl) {
        if (!this.state.readingMode) {
            this.enterReadingMode();
        }
        
        const sectionId = sectionEl.getAttribute('data-section');
        const sectionTitle = sectionEl.querySelector('.section-title').textContent;
        
        // Atualizar estado
        this.state.activeSection = sectionId;
        
        // Atualizar título
        this.elements.readingModeTitle.textContent = sectionTitle;
        
        // Conteúdo de demonstração
        const content = `
            <div class="reading-content-demo">
                <h1>${sectionTitle}</h1>
                <p>📄 <strong>Esta é uma versão de demonstração do modo leitura.</strong></p>
                <p>O conteúdo completo seria carregado do arquivo <code>${sectionId}.mdx</code></p>
                
                <h2>Funcionalidades do Modo Leitura:</h2>
                <ul>
                    <li>✅ Interface limpa e focada</li>
                    <li>✅ Navegação entre seções</li>
                    <li>✅ Barra de progresso</li>
                    <li>✅ Suporte a teclado (setas)</li>
                    <li>✅ Tema sincronizado</li>
                </ul>
                
                <h2>Como usar:</h2>
                <p>Use as setas ⬅️ ➡️ para navegar entre seções ou as teclas do teclado.</p>
                <p>Pressione <kbd>ESC</kbd> para sair do modo leitura.</p>
                
                <div style="background: var(--bg-secondary, #f8fafc); padding: 2rem; border-radius: 0.5rem; margin: 2rem 0;">
                    <h3>💡 Integração Completa</h3>
                    <p>Este accordion se integra perfeitamente com:</p>
                    <ul>
                        <li>🎨 Sistema de temas claro/escuro</li>
                        <li>🌐 Internacionalização pt-BR/en-US</li>
                        <li>🔍 Sistema de busca</li>
                        <li>📱 Design responsivo</li>
                    </ul>
                </div>
            </div>
        `;
        
        // Inserir conteúdo
        this.elements.readingModeContent.innerHTML = content;
        
        // Atualizar navegação
        this.updateReadingNavigation();
        
        // Scroll para o topo
        this.elements.readingModeContent.scrollTop = 0;
        
        console.log(`📖 Seção carregada no modo leitura: ${sectionId}`);
    }

    /**
     * Atualiza navegação do modo leitura
     */
    updateReadingNavigation() {
        const allSections = Array.from(this.elements.accordionContainer.querySelectorAll('.accordion-section'));
        const currentIndex = allSections.findIndex(el => el.getAttribute('data-section') === this.state.activeSection);
        
        // Habilitar/desabilitar botões
        this.elements.readingPrev.disabled = currentIndex <= 0;
        this.elements.readingNext.disabled = currentIndex >= allSections.length - 1;
        
        // Atualizar progresso
        const progress = ((currentIndex + 1) / allSections.length) * 100;
        this.elements.progressFill.style.width = `${progress}%`;
        this.elements.progressText.textContent = `${Math.round(progress)}%`;
    }

    /**
     * Navega no modo leitura
     */
    async navigateReading(direction) {
        const allSections = Array.from(this.elements.accordionContainer.querySelectorAll('.accordion-section'));
        const currentIndex = allSections.findIndex(el => el.getAttribute('data-section') === this.state.activeSection);
        
        let newIndex;
        if (direction === 'prev' && currentIndex > 0) {
            newIndex = currentIndex - 1;
        } else if (direction === 'next' && currentIndex < allSections.length - 1) {
            newIndex = currentIndex + 1;
        } else {
            return; // Não pode navegar
        }
        
        await this.openSectionInReadingMode(allSections[newIndex]);
    }

    /**
     * Expande todas as seções
     */
    async expandAllSections() {
        const categories = this.elements.accordionContainer.querySelectorAll('.accordion-category');
        
        // Expandir categorias uma por uma com pequeno delay para animação suave
        for (let i = 0; i < categories.length; i++) {
            const categoryEl = categories[i];
            this.expandCategory(categoryEl);
            
            // Pequeno delay entre categorias para efeito visual
            if (i < categories.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 150));
            }
        }
        
        console.log('📂 Todas as seções expandidas');
    }

    /**
     * Colapsa todas as seções
     */
    collapseAllSections() {
        const categories = this.elements.accordionContainer.querySelectorAll('.accordion-category');
        
        categories.forEach(categoryEl => {
            this.collapseCategory(categoryEl);
            
            const sections = categoryEl.querySelectorAll('.accordion-section');
            sections.forEach(sectionEl => {
                this.collapseSection(sectionEl);
            });
        });
        
        console.log('📁 Todas as seções colapsadas');
    }

    /**
     * Manipula mudanças de tema
     */
    handleThemeChange() {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        if (newTheme !== this.state.currentTheme) {
            this.state.currentTheme = newTheme;
            this.applyTheme();
        }
    }

    /**
     * Aplica tema
     */
    applyTheme() {
        this.elements.container.setAttribute('data-theme', this.state.currentTheme);
        console.log(`🎨 Tema aplicado: ${this.state.currentTheme}`);
    }

    /**
     * Manipula teclado
     */
    handleKeyboard(e) {
        // Escape: sair do modo leitura ou limpar pesquisa
        if (e.key === 'Escape') {
            if (this.state.readingMode) {
                this.exitReadingMode();
            } else if (this.state.searchActive) {
                this.clearSearchResults();
            }
        }
        
        // Setas no modo leitura
        if (this.state.readingMode) {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateReading('prev');
            } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateReading('next');
            }
        }
    }

    /**
     * Utility: debounce
     */
    debounce(func, wait) {
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

    /**
     * Mostra estado de erro
     */
    showErrorState() {
        const container = this.elements.accordionContainer;
        container.innerHTML = `
            <div class="accordion-error">
                <div class="error-icon">❌</div>
                <h3>Erro no Sistema de Documentação</h3>
                <p>Não foi possível inicializar o accordion.</p>
                <button class="retry-btn" onclick="location.reload()">🔄 Recarregar Página</button>
            </div>
        `;
    }

    /**
     * Obtém contagem total de seções
     */
    getTotalSectionsCount() {
        return Array.from(this.categories.values()).reduce((sum, cat) => sum + cat.files.length, 0);
    }

    /**
     * API pública para debug
     */
    getDebugInfo() {
        return {
            state: this.state,
            categories: Array.from(this.categories.keys()),
            totalSections: this.getTotalSectionsCount(),
            version: 'OfflineAccordion v1.0'
        };
    }
}

// Exportar para uso global
window.OfflineAccordion = OfflineAccordion;