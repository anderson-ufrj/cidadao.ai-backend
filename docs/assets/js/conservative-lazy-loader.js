/**
 * Conservative Lazy Loader - Performance Otimizada
 * 
 * Sistema de lazy loading que preserva 100% da estrutura visual existente
 * Implementa carregamento progressivo sem alterar HTML/CSS
 * 
 * @author Anderson Henrique da Silva
 * @version 1.0.0
 */

class ConservativeLazyLoader {
    constructor(options = {}) {
        this.config = {
            // Seletores da estrutura existente
            accordionItems: options.accordionItems || '.accordion-item',
            itemContents: options.itemContents || '.item-content',
            categoryContents: options.categoryContents || '.category-content',
            
            // Performance settings
            rootMargin: options.rootMargin || '100px',
            threshold: options.threshold || 0.1,
            loadDelay: options.loadDelay || 50,
            
            // Visual preservation
            preserveInitialHeight: options.preserveInitialHeight !== false,
            enablePlaceholders: options.enablePlaceholders !== false,
            enableProgressiveImages: options.enableProgressiveImages !== false,
            
            // Analytics
            enableTracking: options.enableTracking || false,
            
            // Debug
            debug: options.debug || false
        };
        
        this.state = {
            isInitialized: false,
            loadedSections: new Set(),
            observedElements: new Map(),
            totalSections: 0,
            loadedCount: 0
        };
        
        this.observer = null;
        this.performanceMetrics = {
            initTime: 0,
            loadTimes: new Map(),
            totalSavings: 0
        };
    }
    
    /**
     * Inicializa o sistema de lazy loading
     */
    async init() {
        const startTime = performance.now();
        
        try {
            this.log('🚀 Initializing Conservative Lazy Loader...');
            
            // Detectar e preparar elementos
            await this.discoverElements();
            
            // Configurar Intersection Observer
            this.setupIntersectionObserver();
            
            // Aplicar otimizações conservadoras
            await this.applyConservativeOptimizations();
            
            // Configurar event listeners para accordion existente
            this.enhanceExistingAccordion();
            
            // Carregar seção inicial visível
            await this.loadInitialVisibleContent();
            
            this.state.isInitialized = true;
            this.performanceMetrics.initTime = performance.now() - startTime;
            
            this.log(`✅ Conservative Lazy Loader initialized in ${this.performanceMetrics.initTime.toFixed(2)}ms`);
            this.log(`📊 Found ${this.state.totalSections} sections for optimization`);
            
            return this;
            
        } catch (error) {
            console.error('❌ Failed to initialize Conservative Lazy Loader:', error);
            throw error;
        }
    }
    
    /**
     * Descobre elementos na estrutura existente
     */
    async discoverElements() {
        const accordionItems = document.querySelectorAll(this.config.accordionItems);
        this.state.totalSections = accordionItems.length;
        
        accordionItems.forEach((item, index) => {
            const content = item.querySelector(this.config.itemContents);
            if (content) {
                const sectionId = item.dataset.section || `section-${index}`;
                
                this.state.observedElements.set(sectionId, {
                    element: item,
                    content: content,
                    isLoaded: false,
                    originalHeight: null,
                    hasVisualElements: this.detectVisualElements(content)
                });
                
                // Marcar elemento para observação
                item.dataset.lazySection = sectionId;
            }
        });
        
        this.log(`🔍 Discovered ${this.state.observedElements.size} sections`);
    }
    
    /**
     * Detecta elementos visuais críticos (ASCII, math, etc.)
     */
    detectVisualElements(content) {
        const visualIndicators = [
            '┌', '┐', '└', '┘', '├', '┤', '│', '─', // ASCII boxes
            '∑', 'σ', 'α', 'β', 'γ', 'δ', 'λ', 'μ', // Math symbols
            '.math-formula',
            'style="font-family: \'Computer Modern\'',
            'F1-Score',
            '<table',
            '<svg',
            '<canvas'
        ];
        
        const contentHTML = content.innerHTML;
        return visualIndicators.some(indicator => contentHTML.includes(indicator));
    }
    
    /**
     * Configura Intersection Observer
     */
    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: this.config.rootMargin,
            threshold: this.config.threshold
        };
        
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.dataset.lazySection;
                    if (sectionId && !this.state.loadedSections.has(sectionId)) {
                        this.loadSection(sectionId);
                    }
                }
            });
        }, options);
        
        // Observar todos os elementos descobertos
        this.state.observedElements.forEach(({ element }) => {
            this.observer.observe(element);
        });
        
        this.log(`👁️ Intersection Observer setup complete`);
    }
    
    /**
     * Aplica otimizações conservadoras
     */
    async applyConservativeOptimizations() {
        this.state.observedElements.forEach(({ content, hasVisualElements }, sectionId) => {
            if (this.config.preserveInitialHeight) {
                // Preservar altura original para elementos visuais
                if (hasVisualElements) {
                    const rect = content.getBoundingClientRect();
                    this.state.observedElements.get(sectionId).originalHeight = rect.height;
                }
            }
            
            if (this.config.enablePlaceholders && !hasVisualElements) {
                // Adicionar placeholder apenas para seções sem elementos visuais críticos
                this.addLoadingPlaceholder(content, sectionId);
            }
        });
        
        this.log(`🎨 Applied conservative optimizations`);
    }
    
    /**
     * Adiciona placeholder de carregamento
     */
    addLoadingPlaceholder(content, sectionId) {
        const placeholder = document.createElement('div');
        placeholder.className = 'lazy-placeholder';
        placeholder.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            background: var(--bg-secondary);
            border-radius: 8px;
            color: var(--text-secondary);
            font-style: italic;
            transition: opacity 0.3s ease;
        `;
        placeholder.innerHTML = `
            <div style="text-align: center;">
                <div style="width: 24px; height: 24px; border: 2px solid var(--text-tertiary); border-top: 2px solid var(--text-accent); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px;"></div>
                <div>Carregando conteúdo...</div>
            </div>
        `;
        
        // Armazenar conteúdo original
        const originalContent = content.innerHTML;
        content.dataset.originalContent = originalContent;
        
        // Substituir por placeholder
        content.innerHTML = '';
        content.appendChild(placeholder);
        
        this.log(`📦 Added placeholder for section ${sectionId}`);
    }
    
    /**
     * Melhora accordion existente com lazy loading
     */
    enhanceExistingAccordion() {
        // Interceptar cliques nos toggles existentes
        document.querySelectorAll('.item-toggle, .category-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                // Permitir comportamento original
                setTimeout(() => {
                    // Verificar se uma seção foi expandida e precisa ser carregada
                    const accordionItem = toggle.closest('.accordion-item');
                    if (accordionItem) {
                        const sectionId = accordionItem.dataset.lazySection;
                        if (sectionId && !this.state.loadedSections.has(sectionId)) {
                            this.loadSection(sectionId);
                        }
                    }
                }, 100);
            });
        });
        
        this.log(`🔧 Enhanced existing accordion with lazy loading`);
    }
    
    /**
     * Carrega conteúdo inicial visível
     */
    async loadInitialVisibleContent() {
        const viewportHeight = window.innerHeight;
        
        this.state.observedElements.forEach(({ element }, sectionId) => {
            const rect = element.getBoundingClientRect();
            
            // Carregar se estiver na viewport ou próximo
            if (rect.top < viewportHeight + 200) {
                this.loadSection(sectionId);
            }
        });
        
        this.log(`👁️ Loaded initial visible content`);
    }
    
    /**
     * Carrega uma seção específica
     */
    async loadSection(sectionId) {
        if (this.state.loadedSections.has(sectionId)) return;
        
        const startTime = performance.now();
        const sectionData = this.state.observedElements.get(sectionId);
        
        if (!sectionData) {
            this.log(`⚠️ Section ${sectionId} not found`);
            return;
        }
        
        try {
            this.log(`🔄 Loading section ${sectionId}...`);
            
            const { content, hasVisualElements } = sectionData;
            
            // Simular delay para UX suave
            if (this.config.loadDelay > 0) {
                await new Promise(resolve => setTimeout(resolve, this.config.loadDelay));
            }
            
            // Restaurar conteúdo original se havia placeholder
            if (content.dataset.originalContent) {
                content.innerHTML = content.dataset.originalContent;
                delete content.dataset.originalContent;
            }
            
            // Marcar como carregado
            this.state.loadedSections.add(sectionId);
            sectionData.isLoaded = true;
            this.state.loadedCount++;
            
            // Aplicar animação suave
            content.style.opacity = '0';
            setTimeout(() => {
                content.style.transition = 'opacity 0.3s ease';
                content.style.opacity = '1';
            }, 10);
            
            // Métricas de performance
            const loadTime = performance.now() - startTime;
            this.performanceMetrics.loadTimes.set(sectionId, loadTime);
            
            this.log(`✅ Section ${sectionId} loaded in ${loadTime.toFixed(2)}ms`);
            
            // Analytics
            if (this.config.enableTracking) {
                this.trackSectionLoad(sectionId, loadTime, hasVisualElements);
            }
            
            // Parar de observar este elemento
            this.observer.unobserve(sectionData.element);
            
        } catch (error) {
            console.error(`❌ Failed to load section ${sectionId}:`, error);
        }
    }
    
    /**
     * Tracking de analytics
     */
    trackSectionLoad(sectionId, loadTime, hasVisualElements) {
        // Placeholder para integração futura com analytics
        const event = {
            action: 'section_loaded',
            section: sectionId,
            loadTime: loadTime,
            hasVisualElements: hasVisualElements,
            timestamp: Date.now()
        };
        
        this.log(`📊 Analytics:`, event);
    }
    
    /**
     * Utilitários e API pública
     */
    getMetrics() {
        return {
            ...this.performanceMetrics,
            sectionsTotal: this.state.totalSections,
            sectionsLoaded: this.state.loadedCount,
            loadProgress: (this.state.loadedCount / this.state.totalSections * 100).toFixed(1)
        };
    }
    
    preloadSection(sectionId) {
        this.loadSection(sectionId);
    }
    
    preloadAllSections() {
        this.state.observedElements.forEach((_, sectionId) => {
            if (!this.state.loadedSections.has(sectionId)) {
                setTimeout(() => this.loadSection(sectionId), Math.random() * 1000);
            }
        });
    }
    
    isLoaded(sectionId) {
        return this.state.loadedSections.has(sectionId);
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        this.log(`🛑 Conservative Lazy Loader destroyed`);
    }
    
    /**
     * Logging com debug
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[ConservativeLazyLoader]', ...args);
        }
    }
}

// Adicionar CSS para animações de carregamento
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .lazy-placeholder {
        transition: opacity 0.3s ease;
    }
    
    .lazy-placeholder.loading {
        opacity: 0.7;
    }
`;
document.head.appendChild(style);

// Exportação para diferentes ambientes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ConservativeLazyLoader };
} else if (typeof define === 'function' && define.amd) {
    define([], () => ({ ConservativeLazyLoader }));
} else {
    window.ConservativeLazyLoader = ConservativeLazyLoader;
}

console.log('🚀 Conservative Lazy Loader v1.0.0 loaded!');