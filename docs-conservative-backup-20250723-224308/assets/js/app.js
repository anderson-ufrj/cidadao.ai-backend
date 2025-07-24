/**
 * Cidadão.AI Documentation App - Main Orchestrator
 * 
 * Sistema principal que orquestra todos os módulos da documentação
 * Performance-optimized com lazy loading e modularização
 * 
 * @author Anderson Henrique da Silva
 * @version 1.0.0
 */

class CidadaoAIApp {
    constructor() {
        this.modules = {
            header: null,
            floatingButton: null,
            accordion: null,
            contentLoader: null
        };
        
        this.config = {
            loadingDelay: 800, // Tempo mínimo de loading screen
            animationDuration: 300,
            enableAnalytics: false, // Pode ser habilitado futuramente
            
            // Paths dos módulos
            modulePaths: {
                header: './assets/js/components/responsive-header.js',
                floatingButton: './assets/js/components/floating-button.js',
                accordion: './assets/js/components/accordion.js',
                contentLoader: './assets/js/components/content-loader.js'
            }
        };
        
        this.state = {
            isInitialized: false,
            loadingStartTime: Date.now(),
            currentTheme: 'light',
            currentLanguage: 'pt-BR'
        };
    }
    
    /**
     * Inicializa a aplicação
     */
    async init() {
        try {
            console.log('🚀 Initializing Cidadão.AI Documentation App...');
            
            // Detectar preferências do usuário
            this.detectUserPreferences();
            
            // Carregar módulos em paralelo para performance
            await this.loadModules();
            
            // Inicializar componentes
            await this.initializeComponents();
            
            // Configurar event listeners globais
            this.setupGlobalEventListeners();
            
            // Aplicar tema inicial
            this.applyInitialTheme();
            
            // Ocultar loading screen com delay mínimo
            await this.hideLoadingScreen();
            
            this.state.isInitialized = true;
            console.log('✅ Cidadão.AI App initialized successfully');
            
            // Trigger custom event para outros scripts
            document.dispatchEvent(new CustomEvent('appInitialized', {
                detail: { app: this }
            }));
            
        } catch (error) {
            console.error('❌ Failed to initialize app:', error);
            await this.handleInitializationError(error);
            throw error;
        }
    }
    
    /**
     * Detecta preferências do usuário
     */
    detectUserPreferences() {
        // Tema
        const savedTheme = localStorage.getItem('cidadao-ai-theme');
        if (savedTheme) {
            this.state.currentTheme = savedTheme;
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.state.currentTheme = 'dark';
        }
        
        // Idioma
        const savedLanguage = localStorage.getItem('cidadao-ai-language');
        if (savedLanguage) {
            this.state.currentLanguage = savedLanguage;
        } else {
            const browserLang = navigator.language || navigator.userLanguage;
            this.state.currentLanguage = browserLang.startsWith('pt') ? 'pt-BR' : 'en-US';
        }
        
        console.log(`🎨 User preferences: theme=${this.state.currentTheme}, lang=${this.state.currentLanguage}`);
    }
    
    /**
     * Carrega todos os módulos de forma assíncrona
     */
    async loadModules() {
        const startTime = Date.now();
        console.log('📦 Loading modules...');
        
        try {
            // Carregar módulos em paralelo para melhor performance
            const modulePromises = Object.entries(this.config.modulePaths).map(
                async ([name, path]) => {
                    try {
                        await this.loadScript(path);
                        console.log(`✅ Module ${name} loaded successfully`);
                        return { name, success: true };
                    } catch (error) {
                        console.warn(`⚠️ Failed to load module ${name}:`, error);
                        return { name, success: false, error };
                    }
                }
            );
            
            const results = await Promise.all(modulePromises);
            
            // Verificar se módulos críticos carregaram
            const criticalModules = ['accordion', 'contentLoader'];
            const failedCritical = results.filter(r => 
                criticalModules.includes(r.name) && !r.success
            );
            
            if (failedCritical.length > 0) {
                throw new Error(`Critical modules failed to load: ${failedCritical.map(m => m.name).join(', ')}`);
            }
            
            console.log(`📦 Modules loaded in ${Date.now() - startTime}ms`);
            
        } catch (error) {
            console.error('❌ Module loading failed:', error);
            throw error;
        }
    }
    
    /**
     * Carrega um script de forma assíncrona
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            // Verificar se já foi carregado
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.async = true;
            
            script.onload = () => resolve();
            script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
            
            document.head.appendChild(script);
        });
    }
    
    /**
     * Inicializa os componentes
     */
    async initializeComponents() {
        console.log('🔧 Initializing components...');
        
        try {
            // 1. Header responsivo
            await this.initializeHeader();
            
            // 2. Content loader
            await this.initializeContentLoader();
            
            // 3. Accordion inteligente
            await this.initializeAccordion();
            
            // 4. Floating button
            await this.initializeFloatingButton();
            
            console.log('🔧 Components initialized successfully');
            
        } catch (error) {
            console.error('❌ Component initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Inicializa o header responsivo
     */
    async initializeHeader() {
        if (typeof ResponsiveHeader !== 'undefined') {
            this.modules.header = new ResponsiveHeader({
                container: document.getElementById('header-container'),
                logo: {
                    icon: '🏛️',
                    text: 'Cidadão.AI',
                    href: '#',
                    ariaLabel: 'Cidadão.AI - Página inicial'
                },
                theme: {
                    enabled: true,
                    default: this.state.currentTheme,
                    storageKey: 'cidadao-ai-theme'
                },
                language: {
                    enabled: true,
                    default: this.state.currentLanguage,
                    available: ['pt-BR', 'en-US'],
                    storageKey: 'cidadao-ai-language'
                },
                actions: {
                    about: {
                        label: 'Sobre',
                        icon: 'ℹ️',
                        onClick: () => this.showAboutModal()
                    }
                }
            }).init();
            
            // Listen for theme/language changes
            document.addEventListener('languageChange', (e) => {
                this.state.currentLanguage = e.detail.language;
                this.handleLanguageChange(e.detail.language);
            });
            
            console.log('✅ Header initialized');
        } else {
            console.warn('⚠️ ResponsiveHeader not available, using fallback');
        }
    }
    
    /**
     * Inicializa o content loader
     */
    async initializeContentLoader() {
        if (typeof ContentLoader !== 'undefined') {
            this.modules.contentLoader = new ContentLoader({
                container: '#technical-sections',
                loadingDelay: 200,
                enableCache: true,
                onSectionLoad: (sectionId, content) => {
                    console.log(`📄 Section ${sectionId} loaded`);
                    this.trackSectionLoad(sectionId);
                },
                onError: (error) => {
                    console.error('ContentLoader error:', error);
                }
            });
            
            await this.modules.contentLoader.init();
            console.log('✅ ContentLoader initialized');
        } else {
            console.warn('⚠️ ContentLoader not available');
        }
    }
    
    /**
     * Inicializa o accordion inteligente
     */
    async initializeAccordion() {
        if (typeof SmartAccordion !== 'undefined') {
            this.modules.accordion = new SmartAccordion({
                container: '.accordion-container',
                triggers: '.accordion-trigger',
                contents: '.accordion-content',
                allowMultiple: true,
                defaultOpen: 'overview', // Abrir visão geral por padrão
                enableLazyLoad: true,
                contentLoader: this.modules.contentLoader,
                onOpen: (sectionId) => {
                    console.log(`📖 Section ${sectionId} opened`);
                    this.trackSectionOpen(sectionId);
                },
                onClose: (sectionId) => {
                    console.log(`📕 Section ${sectionId} closed`);
                }
            }).init();
            
            // Configurar controles do accordion
            this.setupAccordionControls();
            
            console.log('✅ SmartAccordion initialized');
        } else {
            console.warn('⚠️ SmartAccordion not available');
        }
    }
    
    /**
     * Inicializa o floating button
     */
    async initializeFloatingButton() {
        if (typeof FloatingButton !== 'undefined') {
            this.modules.floatingButton = new FloatingButton({
                icon: 'ℹ️',
                position: 'bottom-right',
                onClick: () => this.showAboutModal(),
                ariaLabel: 'Informações sobre o projeto'
            }).render();
            
            console.log('✅ FloatingButton initialized');
        } else {
            console.warn('⚠️ FloatingButton not available');
        }
    }
    
    /**
     * Configura controles do accordion
     */
    setupAccordionControls() {
        // Botão expandir todas
        const expandAllBtn = document.querySelector('.expand-all');
        if (expandAllBtn) {
            expandAllBtn.addEventListener('click', () => {
                if (this.modules.accordion) {
                    this.modules.accordion.openAll();
                }
            });
        }
        
        // Botão recolher todas
        const collapseAllBtn = document.querySelector('.collapse-all');
        if (collapseAllBtn) {
            collapseAllBtn.addEventListener('click', () => {
                if (this.modules.accordion) {
                    this.modules.accordion.closeAll();
                }
            });
        }
        
        // Search functionality (placeholder)
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
    }
    
    /**
     * Configura event listeners globais
     */
    setupGlobalEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K para busca
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Escape para fechar tudo
            if (e.key === 'Escape') {
                if (this.modules.accordion) {
                    this.modules.accordion.closeAll();
                }
            }
        });
        
        // Performance monitoring
        window.addEventListener('load', () => {
            const loadTime = Date.now() - performance.timing.navigationStart;
            console.log(`⚡ Total page load time: ${loadTime}ms`);
        });
        
        // Error handling
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.handleGlobalError(e.error);
        });
        
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.handleGlobalError(e.reason);
        });
    }
    
    /**
     * Aplica tema inicial
     */
    applyInitialTheme() {
        document.documentElement.setAttribute('data-theme', this.state.currentTheme);
        console.log(`🎨 Applied initial theme: ${this.state.currentTheme}`);
    }
    
    /**
     * Oculta loading screen
     */
    async hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (!loadingScreen) return;
        
        // Garantir tempo mínimo de loading para UX
        const elapsedTime = Date.now() - this.state.loadingStartTime;
        const minimumTime = this.config.loadingDelay;
        
        if (elapsedTime < minimumTime) {
            await new Promise(resolve => 
                setTimeout(resolve, minimumTime - elapsedTime)
            );
        }
        
        // Fade out
        loadingScreen.style.opacity = '0';
        
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            console.log('👋 Loading screen hidden');
        }, 500);
    }
    
    /**
     * Manipula erros de inicialização
     */
    async handleInitializationError(error) {
        console.error('💥 Initialization error:', error);
        
        // Ocultar loading screen mesmo com erro
        await this.hideLoadingScreen();
        
        // Mostrar mensagem de erro amigável
        this.showErrorMessage('Ocorreu um erro ao carregar a documentação. Alguns recursos podem não funcionar corretamente.');
    }
    
    /**
     * Métodos utilitários
     */
    showAboutModal() {
        alert('Cidadão.AI Backend\n\nSistema multi-agente para transparência pública\nVersão 1.0.0\n\nDesenvolvido por Anderson Henrique');
    }
    
    handleLanguageChange(language) {
        console.log(`🌐 Language changed to: ${language}`);
        // Implementar lógica de mudança de idioma
    }
    
    handleSearch(query) {
        console.log(`🔍 Search query: ${query}`);
        // Implementar lógica de busca
    }
    
    trackSectionLoad(sectionId) {
        if (this.config.enableAnalytics) {
            // Enviar evento para analytics
            console.log(`📊 Analytics: section ${sectionId} loaded`);
        }
    }
    
    trackSectionOpen(sectionId) {
        if (this.config.enableAnalytics) {
            // Enviar evento para analytics
            console.log(`📊 Analytics: section ${sectionId} opened`);
        }
    }
    
    handleGlobalError(error) {
        // Log para monitoramento em produção
        console.error('🚨 Global error logged:', error);
    }
    
    showErrorMessage(message) {
        // Criar toast ou modal de erro
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            z-index: 10000;
            max-width: 300px;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    /**
     * API pública para outros scripts
     */
    getModule(name) {
        return this.modules[name];
    }
    
    getState() {
        return { ...this.state };
    }
    
    isInitialized() {
        return this.state.isInitialized;
    }
}

// Criar instância global
window.CidadaoAIApp = new CidadaoAIApp();

// Export para módulos ES6 se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CidadaoAIApp };
}

console.log('🚀 Cidadão.AI App Module v1.0.0 loaded!');