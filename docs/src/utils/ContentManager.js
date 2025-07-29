/**
 * ContentManager.js
 * Sistema modular de carregamento de conteúdo para GitHub Pages
 * Mantém 100% de compatibilidade com sistema existente
 */

class ContentManager {
    constructor() {
        this.contentPath = 'content/sections/';
        this.cache = new Map();
        this.loadingPromises = new Map();
        this.initialized = false;
        
        console.log('📦 ContentManager initialized');
    }

    /**
     * Inicialização automática quando DOM estiver pronto
     */
    async init() {
        if (this.initialized) return;

        try {
            // Aguardar sistema existente estar pronto
            await this.waitForExistingSystem();
            
            // Carregar seções modulares (apenas novas)
            await this.loadModularSections();
            
            this.initialized = true;
            console.log('✅ ContentManager ready');
            
        } catch (error) {
            console.log('ℹ️ ContentManager fallback mode (using inline content)');
            // Fallback silencioso - não quebra nada
        }
    }

    /**
     * Aguarda o sistema JavaScript existente estar pronto
     */
    async waitForExistingSystem() {
        return new Promise(resolve => {
            // Aguardar main.js e accordion system estarem prontos
            const checkReady = () => {
                const accordions = document.querySelectorAll('.accordion-item');
                if (accordions.length > 0) {
                    // Dar mais um pouco de tempo para event listeners
                    setTimeout(resolve, 100);
                } else {
                    setTimeout(checkReady, 50);
                }
            };
            checkReady();
        });
    }

    /**
     * Carrega apenas seções que foram marcadas como modulares
     */
    async loadModularSections() {
        // Lista de seções que usam sistema modular
        const modularSections = [
            'math-foundations',   // Fundamentos matemáticos
            'xai-algorithms'      // Algoritmos XAI avançados
        ];

        // Carregar cada seção modular
        for (const sectionId of modularSections) {
            await this.loadSection(sectionId);
        }
    }

    /**
     * Carrega uma seção específica
     */
    async loadSection(sectionId) {
        // Evitar múltiplas requisições para mesma seção
        if (this.loadingPromises.has(sectionId)) {
            return await this.loadingPromises.get(sectionId);
        }

        const loadingPromise = this._loadSectionInternal(sectionId);
        this.loadingPromises.set(sectionId, loadingPromise);
        
        try {
            const result = await loadingPromise;
            return result;
        } finally {
            this.loadingPromises.delete(sectionId);
        }
    }

    /**
     * Implementação interna do carregamento
     */
    async _loadSectionInternal(sectionId) {
        try {
            // Encontrar container da seção
            const container = document.querySelector(`[data-section="${sectionId}"] .item-content`);
            if (!container) {
                console.log(`Container for ${sectionId} not found`);
                return false;
            }

            // Verificar se já tem conteúdo (evitar sobrescrever)
            if (this.hasContent(container)) {
                console.log(`Section ${sectionId} already has content`);
                return true;
            }

            // Verificar cache (incluindo idioma na chave)
            const currentLanguage = window.currentLanguage || 'pt-BR';
            const cacheKey = `${sectionId}-${currentLanguage}`;
            
            if (this.cache.has(cacheKey)) {
                this.insertContent(container, this.cache.get(cacheKey));
                return true;
            }

            // Buscar conteúdo externo baseado no idioma atual
            const suffix = currentLanguage === 'en-US' ? '-en' : '';
            const url = `${this.contentPath}${sectionId}${suffix}.html`;
            const response = await fetch(url);
            
            if (!response.ok) {
                console.log(`Section ${sectionId} not found (${response.status}), using fallback`);
                return false;
            }

            const content = await response.text();
            
            // Validar conteúdo
            if (!content.trim()) {
                console.log(`Section ${sectionId} is empty`);
                return false;
            }

            // Cache e inserir
            this.cache.set(cacheKey, content);
            this.insertContent(container, content);
            
            console.log(`✅ Loaded section: ${sectionId}`);
            return true;

        } catch (error) {
            console.log(`Failed to load ${sectionId}:`, error.message);
            return false;
        }
    }

    /**
     * Verifica se container já tem conteúdo relevante
     */
    hasContent(container) {
        // Considerar vazio se só tem loading divs ou whitespace
        const children = Array.from(container.children);
        const meaningfulContent = children.filter(child => {
            return !child.classList.contains('content-loading') &&
                   child.textContent.trim().length > 0;
        });
        
        return meaningfulContent.length > 0;
    }

    /**
     * Insere conteúdo preservando event listeners e estrutura
     */
    insertContent(container, htmlContent) {
        try {
            // Criar elemento temporário para parsing
            const temp = document.createElement('div');
            temp.innerHTML = htmlContent;

            // Limpar apenas loading elements
            const loadingElements = container.querySelectorAll('.content-loading');
            loadingElements.forEach(el => el.remove());

            // Inserir novo conteúdo preservando eventos
            while (temp.firstChild) {
                container.appendChild(temp.firstChild);
            }

            // Trigger eventos personalizados se necessário
            this.triggerContentLoaded(container);
            
            // Force accordion height recalculation if expanded
            this.recalculateAccordionHeight(container);

        } catch (error) {
            console.error('Error inserting content:', error);
        }
    }

    /**
     * Dispara eventos após carregamento do conteúdo
     */
    triggerContentLoaded(container) {
        // Evento customizado para outros scripts
        const event = new CustomEvent('contentLoaded', {
            detail: { container, source: 'ContentManager' }
        });
        container.dispatchEvent(event);
    }

    /**
     * Recalcula altura do accordion após inserção de conteúdo
     */
    recalculateAccordionHeight(container) {
        try {
            const accordionItem = container.closest('.accordion-item');
            if (!accordionItem) return;
            
            const toggle = accordionItem.querySelector('.item-toggle');
            const isExpanded = toggle && toggle.getAttribute('aria-expanded') === 'true';
            
            if (isExpanded && container.classList.contains('expanded')) {
                // Since we now use max-height: none, ensure proper overflow handling
                container.style.maxHeight = 'none';
                container.style.overflow = 'visible';
                
                // Force a reflow to ensure content is properly displayed
                const contentHeight = container.scrollHeight;
                
                // Trigger any layout recalculations
                container.offsetHeight; // Force reflow
                
                console.log(`📏 Accordion height recalculated - content fully visible: ${contentHeight}px`);
            }
        } catch (error) {
            console.error('Error recalculating accordion height:', error);
        }
    }

    /**
     * API pública para recarregar conteúdo modular (usado na mudança de idioma)
     */
    async reloadModularContent() {
        if (!this.initialized) return;
        
        console.log('🔄 Reloading modular content for language change...');
        
        // Forçar recarregamento removendo conteúdo existente
        const modularSections = ['math-foundations', 'xai-algorithms'];
        
        for (const sectionId of modularSections) {
            const container = document.querySelector(`[data-section="${sectionId}"] .item-content`);
            if (container) {
                // Limpar conteúdo existente exceto loading placeholders
                const children = Array.from(container.children);
                children.forEach(child => {
                    if (!child.classList.contains('content-loading')) {
                        child.remove();
                    }
                });
                
                // Recarregar seção
                await this.loadSection(sectionId);
            }
        }
        
        console.log('✅ Modular content reloaded');
    }

    /**
     * API pública para adicionar novas seções modulares
     */
    static addModularSection(sectionId) {
        // Para uso futuro - adicionar seções dinamicamente
        if (window.contentManager && window.contentManager.initialized) {
            return window.contentManager.loadSection(sectionId);
        }
        return Promise.resolve(false);
    }
    
    /**
     * API pública para recarregar conteúdo na mudança de idioma
     */
    static async reloadForLanguageChange() {
        if (window.contentManager && window.contentManager.initialized) {
            return await window.contentManager.reloadModularContent();
        }
        return Promise.resolve();
    }
}

// Auto-inicialização quando DOM estiver pronto
(function() {
    // Criar instância global
    window.contentManager = new ContentManager();

    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.contentManager.init();
        });
    } else {
        // DOM já está pronto
        setTimeout(() => window.contentManager.init(), 100);
    }
})();

// Exportar para uso em outros módulos se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContentManager;
}