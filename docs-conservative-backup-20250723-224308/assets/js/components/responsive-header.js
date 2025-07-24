/**
 * ResponsiveHeader JavaScript Module
 * 
 * Módulo completo para header responsivo reutilizável
 * Inclui: temas, i18n, mobile menu, localStorage, acessibilidade
 * 
 * @author Anderson Henrique da Silva
 * @version 1.0.0
 */

class ResponsiveHeader {
    constructor(options = {}) {
        // Configurações padrão
        this.config = {
            // Logo configuration
            logo: {
                icon: options.logo?.icon || '🏛️',
                text: options.logo?.text || 'MyApp',
                href: options.logo?.href || '#',
                ariaLabel: options.logo?.ariaLabel || 'Página inicial'
            },
            
            // Theme configuration
            theme: {
                enabled: options.theme?.enabled !== false,
                default: options.theme?.default || 'light',
                storageKey: options.theme?.storageKey || 'app-theme'
            },
            
            // Language configuration
            language: {
                enabled: options.language?.enabled !== false,
                default: options.language?.default || 'pt-BR',
                available: options.language?.available || ['pt-BR', 'en-US'],
                storageKey: options.language?.storageKey || 'app-language'
            },
            
            // Action buttons
            actions: options.actions || {},
            
            // Mobile behavior
            mobile: {
                breakpoint: options.mobile?.breakpoint || 768,
                autoClose: options.mobile?.autoClose !== false
            },
            
            // CSS classes
            classes: {
                container: options.classes?.container || 'responsive-navbar',
                ...options.classes
            },
            
            // Container element
            container: options.container || null,
            
            // Translations
            translations: options.translations || this.getDefaultTranslations()
        };
        
        // Estado interno
        this.state = {
            currentTheme: this.config.theme.default,
            currentLanguage: this.config.language.default,
            mobileMenuOpen: false,
            isInitialized: false
        };
        
        // Elementos DOM
        this.elements = {};
    }
    
    /**
     * Tradução padrão
     */
    getDefaultTranslations() {
        return {
            'pt-BR': {
                'theme.light': '☀️ Claro',
                'theme.dark': '🌙 Escuro',
                'language.pt': '🇧🇷 PT',
                'language.en': '🇺🇸 EN',
                'menu.toggle': 'Alternar menu',
                'action.default': '⚙️ Ação'
            },
            'en-US': {
                'theme.light': '☀️ Light',
                'theme.dark': '🌙 Dark',
                'language.pt': '🇧🇷 PT',
                'language.en': '🇺🇸 EN',
                'menu.toggle': 'Toggle menu',
                'action.default': '⚙️ Action'
            }
        };
    }
    
    /**
     * Inicializa o header
     */
    init() {
        if (this.state.isInitialized) {
            console.warn('ResponsiveHeader already initialized');
            return this;
        }
        
        // Detectar preferências do usuário
        this.detectUserPreferences();
        
        // Renderizar HTML
        this.render();
        
        // Aplicar tema inicial
        this.applyTheme(this.state.currentTheme);
        
        // Aplicar idioma inicial
        this.updateLanguage(this.state.currentLanguage);
        
        // Inicializar event listeners
        this.initializeEventListeners();
        
        this.state.isInitialized = true;
        console.log('🚀 ResponsiveHeader initialized successfully');
        
        return this;
    }
    
    /**
     * Detecta preferências do usuário
     */
    detectUserPreferences() {
        // Detectar tema
        const savedTheme = localStorage.getItem(this.config.theme.storageKey);
        if (savedTheme) {
            this.state.currentTheme = savedTheme;
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.state.currentTheme = 'dark';
        }
        
        // Detectar idioma
        const savedLanguage = localStorage.getItem(this.config.language.storageKey);
        if (savedLanguage && this.config.language.available.includes(savedLanguage)) {
            this.state.currentLanguage = savedLanguage;
        } else {
            const browserLang = navigator.language || navigator.userLanguage;
            const detectedLang = this.config.language.available.find(lang => 
                browserLang.startsWith(lang.split('-')[0])
            );
            this.state.currentLanguage = detectedLang || this.config.language.default;
        }
    }
    
    /**
     * Renderiza o HTML do header
     */
    render() {
        const container = this.config.container || document.body;
        
        const headerHTML = `
            <nav class="${this.config.classes.container}" role="navigation" aria-label="Navegação principal">
                <div class="responsive-navbar-container">
                    <!-- Logo -->
                    <a href="${this.config.logo.href}" class="responsive-logo" aria-label="${this.config.logo.ariaLabel}">
                        <div class="responsive-logo-icon">${this.config.logo.icon}</div>
                        <span class="responsive-logo-text">${this.config.logo.text}</span>
                    </a>
                    
                    <!-- Mobile Toggle -->
                    <button class="responsive-mobile-toggle" aria-label="${this.translate('menu.toggle')}" data-mobile-toggle>
                        <span></span>
                        <span></span>
                        <span></span>
                    </button>
                    
                    <!-- Navigation Controls -->
                    <div class="responsive-nav-controls" data-nav-controls>
                        ${this.renderActionButtons()}
                        ${this.renderThemeControls()}
                        ${this.renderLanguageControls()}
                    </div>
                </div>
            </nav>
        `;
        
        // Inserir no DOM
        if (this.config.container) {
            container.innerHTML = headerHTML;
        } else {
            const headerElement = document.createElement('div');
            headerElement.innerHTML = headerHTML;
            document.body.insertBefore(headerElement.firstElementChild, document.body.firstChild);
        }
        
        // Capturar referências dos elementos
        this.elements.navbar = document.querySelector(`.${this.config.classes.container}`);
        this.elements.mobileToggle = this.elements.navbar.querySelector('[data-mobile-toggle]');
        this.elements.navControls = this.elements.navbar.querySelector('[data-nav-controls]');
    }
    
    /**
     * Renderiza botões de ação personalizados
     */
    renderActionButtons() {
        return Object.entries(this.config.actions).map(([key, action]) => {
            const label = action.label || this.translate('action.default');
            const icon = action.icon || '';
            return `
                <button class="responsive-action-btn" data-action="${key}" aria-label="${label}">
                    ${icon} ${label}
                </button>
            `;
        }).join('');
    }
    
    /**
     * Renderiza controles de tema
     */
    renderThemeControls() {
        if (!this.config.theme.enabled) return '';
        
        return `
            <div class="responsive-control-group" role="group" aria-label="Seletor de tema">
                <button class="responsive-control-button" data-theme-btn="light" aria-label="Tema claro">
                    ${this.translate('theme.light')}
                </button>
                <button class="responsive-control-button" data-theme-btn="dark" aria-label="Tema escuro">
                    ${this.translate('theme.dark')}
                </button>
            </div>
        `;
    }
    
    /**
     * Renderiza controles de idioma
     */
    renderLanguageControls() {
        if (!this.config.language.enabled || this.config.language.available.length < 2) return '';
        
        const buttons = this.config.language.available.map(lang => {
            const key = lang === 'pt-BR' ? 'language.pt' : 'language.en';
            return `
                <button class="responsive-control-button" data-lang-btn="${lang}" aria-label="${lang}">
                    ${this.translate(key)}
                </button>
            `;
        }).join('');
        
        return `
            <div class="responsive-control-group" role="group" aria-label="Seletor de idioma">
                ${buttons}
            </div>
        `;
    }
    
    /**
     * Inicializa event listeners
     */
    initializeEventListeners() {
        // Botões de tema
        if (this.config.theme.enabled) {
            this.elements.navbar.querySelectorAll('[data-theme-btn]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const theme = btn.getAttribute('data-theme-btn');
                    this.setTheme(theme);
                });
            });
        }
        
        // Botões de idioma
        if (this.config.language.enabled) {
            this.elements.navbar.querySelectorAll('[data-lang-btn]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const lang = btn.getAttribute('data-lang-btn');
                    this.setLanguage(lang);
                });
            });
        }
        
        // Botões de ação
        this.elements.navbar.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', () => {
                const actionKey = btn.getAttribute('data-action');
                const action = this.config.actions[actionKey];
                if (action && typeof action.onClick === 'function') {
                    action.onClick();
                }
            });
        });
        
        // Mobile toggle
        if (this.elements.mobileToggle) {
            this.elements.mobileToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }
        
        // Fechar menu mobile ao redimensionar
        window.addEventListener('resize', () => {
            if (window.innerWidth > this.config.mobile.breakpoint && this.state.mobileMenuOpen) {
                this.closeMobileMenu();
            }
        });
        
        // Fechar menu mobile ao clicar fora
        if (this.config.mobile.autoClose) {
            document.addEventListener('click', (e) => {
                if (!this.elements.navbar.contains(e.target) && this.state.mobileMenuOpen) {
                    this.closeMobileMenu();
                }
            });
        }
    }
    
    /**
     * Define o tema
     */
    setTheme(theme) {
        if (theme === this.state.currentTheme) return;
        
        this.state.currentTheme = theme;
        this.applyTheme(theme);
        localStorage.setItem(this.config.theme.storageKey, theme);
        
        console.log(`🎨 Tema alterado para: ${theme}`);
    }
    
    /**
     * Aplica o tema
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Atualizar botões de tema
        this.elements.navbar.querySelectorAll('[data-theme-btn]').forEach(btn => {
            const btnTheme = btn.getAttribute('data-theme-btn');
            btn.classList.toggle('active', btnTheme === theme);
        });
    }
    
    /**
     * Define o idioma
     */
    setLanguage(language) {
        if (language === this.state.currentLanguage) return;
        
        this.state.currentLanguage = language;
        this.updateLanguage(language);
        localStorage.setItem(this.config.language.storageKey, language);
        
        console.log(`🌐 Idioma alterado para: ${language}`);
    }
    
    /**
     * Atualiza textos do idioma
     */
    updateLanguage(language) {
        // Atualizar botões de idioma
        this.elements.navbar.querySelectorAll('[data-lang-btn]').forEach(btn => {
            const btnLang = btn.getAttribute('data-lang-btn');
            btn.classList.toggle('active', btnLang === language);
        });
        
        // Aqui você pode adicionar lógica para atualizar outros textos da página
        // Disparar evento customizado para que a aplicação possa reagir
        document.dispatchEvent(new CustomEvent('languageChange', {
            detail: { language, translations: this.config.translations[language] }
        }));
    }
    
    /**
     * Toggle do menu mobile
     */
    toggleMobileMenu() {
        this.state.mobileMenuOpen = !this.state.mobileMenuOpen;
        
        this.elements.mobileToggle.classList.toggle('active', this.state.mobileMenuOpen);
        this.elements.navControls.classList.toggle('mobile-open', this.state.mobileMenuOpen);
        
        // Acessibilidade
        this.elements.mobileToggle.setAttribute('aria-expanded', this.state.mobileMenuOpen.toString());
    }
    
    /**
     * Fecha o menu mobile
     */
    closeMobileMenu() {
        this.state.mobileMenuOpen = false;
        this.elements.mobileToggle.classList.remove('active');
        this.elements.navControls.classList.remove('mobile-open');
        this.elements.mobileToggle.setAttribute('aria-expanded', 'false');
    }
    
    /**
     * Função de tradução
     */
    translate(key) {
        return this.config.translations[this.state.currentLanguage]?.[key] || key;
    }
    
    /**
     * Atualiza configurações
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        return this;
    }
    
    /**
     * Destrói o header
     */
    destroy() {
        if (this.elements.navbar) {
            this.elements.navbar.remove();
        }
        this.state.isInitialized = false;
        return this;
    }
    
    /**
     * Obtém estado atual
     */
    getState() {
        return { ...this.state };
    }
}

// Factory function para criação rápida
function createResponsiveHeader(options) {
    return new ResponsiveHeader(options).init();
}

// Exportações para diferentes ambientes
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = { ResponsiveHeader, createResponsiveHeader };
} else if (typeof define === 'function' && define.amd) {
    // AMD
    define([], () => ({ ResponsiveHeader, createResponsiveHeader }));
} else {
    // Browser global
    window.ResponsiveHeader = ResponsiveHeader;
    window.createResponsiveHeader = createResponsiveHeader;
}

console.log('🚀 ResponsiveHeader Module v1.0.0 loaded!');