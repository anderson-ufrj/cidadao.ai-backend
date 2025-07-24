/**
 * ComponentLoader - Engine de Carregamento de Componentes Modular
 * Cidadão.AI Backend Documentation - Modular System
 */

class ComponentLoader {
    constructor() {
        this.cache = new Map();
        this.templates = new Map();
        this.initialized = false;
        
        console.log('🚀 ComponentLoader initialized');
    }

    /**
     * Inicializa o sistema de componentes
     */
    async init() {
        if (this.initialized) return;
        
        try {
            await this.loadBaseComponents();
            this.setupEventDelegation();
            this.initialized = true;
            
            console.log('✅ ComponentLoader ready');
        } catch (error) {
            console.error('❌ ComponentLoader initialization failed:', error);
        }
    }

    /**
     * Carrega um componente
     */
    async loadComponent(name, container, data = {}) {
        try {
            // Check cache first
            if (this.cache.has(name)) {
                const template = this.cache.get(name);
                return this.renderComponent(template, container, data);
            }

            // Load from file
            const response = await fetch(`src/components/${name}.html`);
            if (!response.ok) {
                throw new Error(`Component ${name} not found`);
            }

            const template = await response.text();
            this.cache.set(name, template);

            return this.renderComponent(template, container, data);

        } catch (error) {
            console.error(`❌ Error loading component ${name}:`, error);
            return this.renderFallback(container, name);
        }
    }

    /**
     * Renderiza um componente com dados
     */
    renderComponent(template, container, data) {
        // Simple template replacement
        let rendered = template;
        
        for (const [key, value] of Object.entries(data)) {
            const regex = new RegExp(`{{${key}}}`, 'g');
            rendered = rendered.replace(regex, value);
        }

        // Render to container
        if (typeof container === 'string') {
            const element = document.querySelector(container);
            if (element) {
                element.innerHTML = rendered;
            }
        } else if (container instanceof Element) {
            container.innerHTML = rendered;
        }

        return rendered;
    }

    /**
     * Carrega múltiplos componentes de acordeão
     */
    async loadAccordionItems(sections) {
        const container = document.getElementById('documentationAccordion');
        if (!container) return;

        const promises = sections.map(section => 
            this.loadComponent('accordion/AccordionItem', null, {
                section: section.id,
                title: section.title,
                category: section.category,
                icon: section.icon || '📄'
            })
        );

        try {
            const renderedItems = await Promise.all(promises);
            container.innerHTML = renderedItems.join('');
            
            // Re-initialize accordion functionality
            if (window.CidadaoAI && window.CidadaoAI.initAccordion) {
                window.CidadaoAI.initAccordion();
            }

            console.log(`✅ Loaded ${sections.length} accordion items`);
        } catch (error) {
            console.error('❌ Error loading accordion items:', error);
        }
    }

    /**
     * Carrega componentes base necessários
     */
    async loadBaseComponents() {
        const baseComponents = [
            'navigation/Navbar',
            'search/SearchBar'
        ];

        for (const component of baseComponents) {
            await this.preloadComponent(component);
        }
    }

    /**
     * Pre-carrega um componente no cache
     */
    async preloadComponent(name) {
        if (this.cache.has(name)) return;

        try {
            const response = await fetch(`src/components/${name}.html`);
            if (response.ok) {
                const template = await response.text();
                this.cache.set(name, template);
            }
        } catch (error) {
            console.warn(`⚠️ Could not preload component ${name}:`, error);
        }
    }

    /**
     * Renderiza fallback para componentes que falharam
     */
    renderFallback(container, componentName) {
        const fallback = `
            <div class="component-fallback">
                <div style="padding: 1rem; border: 1px dashed var(--border); border-radius: 8px;">
                    <p>⚠️ Componente <code>${componentName}</code> não pôde ser carregado.</p>
                    <small>Fallback ativo - funcionalidade básica preservada</small>
                </div>
            </div>
        `;

        if (typeof container === 'string') {
            const element = document.querySelector(container);
            if (element) {
                element.innerHTML = fallback;
            }
        } else if (container instanceof Element) {
            container.innerHTML = fallback;
        }

        return fallback;
    }

    /**
     * Setup de event delegation para componentes dinâmicos
     */
    setupEventDelegation() {
        document.addEventListener('click', (e) => {
            // Handle component-specific clicks
            const target = e.target.closest('[data-component-action]');
            if (target) {
                const action = target.dataset.componentAction;
                const component = target.dataset.component;
                
                this.handleComponentAction(action, component, target, e);
            }
        });
    }

    /**
     * Handle ações de componentes
     */
    handleComponentAction(action, component, element, event) {
        switch (action) {
            case 'toggle-accordion':
                this.handleAccordionToggle(element, event);
                break;
            case 'open-modal':
                this.handleModalOpen(element, event);
                break;
            case 'close-modal':
                this.handleModalClose(element, event);
                break;
            default:
                console.log(`🔧 Component action: ${action} on ${component}`);
        }
    }

    /**
     * Handle accordion toggle
     */
    handleAccordionToggle(element, event) {
        event.preventDefault();
        
        const item = element.closest('.accordion-item');
        const content = item.querySelector('.item-content');
        const isExpanded = element.getAttribute('aria-expanded') === 'true';

        if (isExpanded) {
            element.setAttribute('aria-expanded', 'false');
            content.classList.remove('expanded');
        } else {
            element.setAttribute('aria-expanded', 'true');
            content.classList.add('expanded');
        }

        console.log(`🎯 Accordion toggled: ${item.dataset.section}`);
    }

    /**
     * Handle modal open
     */
    handleModalOpen(element, event) {
        event.preventDefault();
        
        const modalId = element.dataset.modalTarget;
        const modal = document.getElementById(modalId);
        
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            console.log(`📖 Modal opened: ${modalId}`);
        }
    }

    /**
     * Handle modal close
     */
    handleModalClose(element, event) {
        event.preventDefault();
        
        const modal = element.closest('.modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
            console.log(`❌ Modal closed: ${modal.id}`);
        }
    }

    /**
     * Utilitário para limpar cache
     */
    clearCache() {
        this.cache.clear();
        console.log('🧹 Component cache cleared');
    }

    /**
     * Estatísticas do sistema
     */
    getStats() {
        return {
            cachedComponents: this.cache.size,
            initialized: this.initialized,
            cacheKeys: Array.from(this.cache.keys())
        };
    }
}

// Instância global
window.ComponentLoader = new ComponentLoader();

// Auto-inicialização quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.ComponentLoader.init();
    });
} else {
    window.ComponentLoader.init();
}

export default ComponentLoader;