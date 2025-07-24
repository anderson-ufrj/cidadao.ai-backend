/**
 * SmartAccordion - Sistema de Accordion Inteligente
 * 
 * Accordion com lazy loading, animações suaves e acessibilidade completa
 * 
 * @author Anderson Henrique da Silva
 * @version 1.0.0
 */

class SmartAccordion {
    constructor(options = {}) {
        this.config = {
            // Seletores
            container: options.container || '.accordion-container',
            triggers: options.triggers || '.accordion-trigger',
            contents: options.contents || '.accordion-content',
            
            // Comportamento
            allowMultiple: options.allowMultiple || false,
            defaultOpen: options.defaultOpen || null, // ID da seção padrão aberta
            animationDuration: options.animationDuration || 300,
            
            // Lazy loading
            enableLazyLoad: options.enableLazyLoad !== false,
            contentLoader: options.contentLoader || null,
            
            // Classes CSS
            activeClass: options.activeClass || 'active',
            openClass: options.openClass || 'open',
            loadingClass: options.loadingClass || 'loading',
            
            // Callbacks
            onOpen: options.onOpen || (() => {}),
            onClose: options.onClose || (() => {}),
            onToggle: options.onToggle || (() => {})
        };
        
        this.state = {
            openSections: new Set(),
            isAnimating: false
        };
        
        this.elements = {
            container: null,
            triggers: [],
            contents: []
        };
    }
    
    /**
     * Inicializa o accordion
     */
    init() {
        this.setupElements();
        this.setupEventListeners();
        this.setupAccessibility();
        this.openDefaultSection();
        
        console.log('🚀 SmartAccordion initialized successfully');
        return this;
    }
    
    /**
     * Configura elementos DOM
     */
    setupElements() {
        this.elements.container = document.querySelector(this.config.container);
        if (!this.elements.container) {
            throw new Error(`Accordion container not found: ${this.config.container}`);
        }
        
        this.elements.triggers = Array.from(
            this.elements.container.querySelectorAll(this.config.triggers)
        );
        
        this.elements.contents = Array.from(
            this.elements.container.querySelectorAll(this.config.contents)
        );
        
        // Associar triggers com contents
        this.elements.triggers.forEach(trigger => {
            const sectionId = trigger.dataset.sectionId || trigger.getAttribute('aria-controls');
            if (sectionId) {
                const content = this.elements.container.querySelector(`[data-section-id="${sectionId}"] ${this.config.contents}`);
                if (content) {
                    trigger._associatedContent = content;
                    content._associatedTrigger = trigger;
                }
            }
        });
    }
    
    /**
     * Configura event listeners
     */
    setupEventListeners() {
        this.elements.triggers.forEach(trigger => {
            // Click handler
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleTriggerClick(trigger);
            });
            
            // Keyboard handler
            trigger.addEventListener('keydown', (e) => {
                this.handleKeyDown(e, trigger);
            });
            
            // Focus management
            trigger.addEventListener('focus', () => {
                trigger.classList.add('focused');
            });
            
            trigger.addEventListener('blur', () => {
                trigger.classList.remove('focused');
            });
        });
        
        // Escape key para fechar tudo
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAll();
            }
        });
    }
    
    /**
     * Configura acessibilidade ARIA
     */
    setupAccessibility() {
        this.elements.triggers.forEach((trigger, index) => {
            const sectionId = trigger.dataset.sectionId || `accordion-section-${index}`;
            const content = trigger._associatedContent;
            
            if (content) {
                // IDs únicos
                if (!trigger.id) trigger.id = `trigger-${sectionId}`;
                if (!content.id) content.id = `content-${sectionId}`;
                
                // ARIA attributes
                trigger.setAttribute('aria-expanded', 'false');
                trigger.setAttribute('aria-controls', content.id);
                trigger.setAttribute('role', 'button');
                trigger.setAttribute('tabindex', '0');
                
                content.setAttribute('aria-labelledby', trigger.id);
                content.setAttribute('role', 'region');
                content.setAttribute('aria-hidden', 'true');
                
                // Estado inicial
                content.style.display = 'none';
                content.style.height = '0';
                content.style.overflow = 'hidden';
            }
        });
    }
    
    /**
     * Abre seção padrão
     */
    openDefaultSection() {
        if (this.config.defaultOpen) {
            const defaultTrigger = this.elements.triggers.find(
                trigger => trigger.dataset.sectionId === this.config.defaultOpen
            );
            if (defaultTrigger) {
                this.openSection(defaultTrigger, false); // Sem animação inicial
            }
        }
    }
    
    /**
     * Manipula clique no trigger
     */
    async handleTriggerClick(trigger) {
        if (this.state.isAnimating) return;
        
        const sectionId = trigger.dataset.sectionId;
        const isOpen = this.state.openSections.has(sectionId);
        
        if (isOpen) {
            await this.closeSection(trigger);
        } else {
            // Fechar outras seções se não permitir múltiplas
            if (!this.config.allowMultiple) {
                await this.closeAll();
            }
            
            await this.openSection(trigger);
            
            // Lazy load se habilitado
            if (this.config.enableLazyLoad && this.config.contentLoader) {
                this.config.contentLoader.loadSection(sectionId);
            }
        }
        
        this.config.onToggle(sectionId, !isOpen);
    }
    
    /**
     * Manipula teclas
     */
    handleKeyDown(e, trigger) {
        switch (e.key) {
            case 'Enter':
            case ' ':
                e.preventDefault();
                this.handleTriggerClick(trigger);
                break;
                
            case 'ArrowDown':
                e.preventDefault();
                this.focusNext(trigger);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.focusPrevious(trigger);
                break;
                
            case 'Home':
                e.preventDefault();
                this.focusFirst();
                break;
                
            case 'End':
                e.preventDefault();
                this.focusLast();
                break;
        }
    }
    
    /**
     * Abre uma seção
     */
    async openSection(trigger, animate = true) {
        const sectionId = trigger.dataset.sectionId;
        const content = trigger._associatedContent;
        
        if (!content || this.state.openSections.has(sectionId)) return;
        
        this.state.isAnimating = true;
        
        try {
            // Atualizar estado
            this.state.openSections.add(sectionId);
            
            // Atualizar classes e ARIA
            trigger.classList.add(this.config.activeClass);
            trigger.setAttribute('aria-expanded', 'true');
            
            content.classList.add(this.config.openClass);
            content.setAttribute('aria-hidden', 'false');
            
            if (animate) {
                // Animar abertura
                await this.animateOpen(content);
            } else {
                // Abrir instantaneamente
                content.style.display = 'block';
                content.style.height = 'auto';
            }
            
            // Callback
            this.config.onOpen(sectionId, trigger, content);
            
            // Scroll suave para a seção se necessário
            if (animate) {
                this.scrollToSection(trigger);
            }
            
        } finally {
            this.state.isAnimating = false;
        }
    }
    
    /**
     * Fecha uma seção
     */
    async closeSection(trigger) {
        const sectionId = trigger.dataset.sectionId;
        const content = trigger._associatedContent;
        
        if (!content || !this.state.openSections.has(sectionId)) return;
        
        this.state.isAnimating = true;
        
        try {
            // Atualizar estado
            this.state.openSections.delete(sectionId);
            
            // Atualizar classes e ARIA
            trigger.classList.remove(this.config.activeClass);
            trigger.setAttribute('aria-expanded', 'false');
            
            content.classList.remove(this.config.openClass);
            content.setAttribute('aria-hidden', 'true');
            
            // Animar fechamento
            await this.animateClose(content);
            
            // Callback
            this.config.onClose(sectionId, trigger, content);
            
        } finally {
            this.state.isAnimating = false;
        }
    }
    
    /**
     * Animação de abertura
     */
    async animateOpen(content) {
        // Preparar para animação
        content.style.display = 'block';
        content.style.height = '0';
        content.style.opacity = '0';
        
        // Calcular altura real
        const realHeight = content.scrollHeight;
        
        // Animar
        content.style.transition = `height ${this.config.animationDuration}ms ease, opacity ${this.config.animationDuration}ms ease`;
        
        await new Promise(resolve => {
            requestAnimationFrame(() => {
                content.style.height = realHeight + 'px';
                content.style.opacity = '1';
                
                setTimeout(() => {
                    content.style.height = 'auto';
                    content.style.transition = '';
                    resolve();
                }, this.config.animationDuration);
            });
        });
    }
    
    /**
     * Animação de fechamento
     */
    async animateClose(content) {
        // Altura atual
        const currentHeight = content.scrollHeight;
        content.style.height = currentHeight + 'px';
        
        // Animar
        content.style.transition = `height ${this.config.animationDuration}ms ease, opacity ${this.config.animationDuration}ms ease`;
        
        await new Promise(resolve => {
            requestAnimationFrame(() => {
                content.style.height = '0';
                content.style.opacity = '0';
                
                setTimeout(() => {
                    content.style.display = 'none';
                    content.style.transition = '';
                    resolve();
                }, this.config.animationDuration);
            });
        });
    }
    
    /**
     * Scroll suave para seção
     */
    scrollToSection(trigger) {
        const rect = trigger.getBoundingClientRect();
        const scrollTop = window.pageYOffset + rect.top - 100; // 100px offset
        
        window.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
        });
    }
    
    /**
     * Navegação por teclado
     */
    focusNext(currentTrigger) {
        const currentIndex = this.elements.triggers.indexOf(currentTrigger);
        const nextIndex = (currentIndex + 1) % this.elements.triggers.length;
        this.elements.triggers[nextIndex].focus();
    }
    
    focusPrevious(currentTrigger) {
        const currentIndex = this.elements.triggers.indexOf(currentTrigger);
        const prevIndex = currentIndex === 0 ? this.elements.triggers.length - 1 : currentIndex - 1;
        this.elements.triggers[prevIndex].focus();
    }
    
    focusFirst() {
        this.elements.triggers[0]?.focus();
    }
    
    focusLast() {
        this.elements.triggers[this.elements.triggers.length - 1]?.focus();
    }
    
    /**
     * Métodos públicos
     */
    async openAll() {
        for (const trigger of this.elements.triggers) {
            if (!this.state.openSections.has(trigger.dataset.sectionId)) {
                await this.openSection(trigger);
            }
        }
    }
    
    async closeAll() {
        for (const trigger of this.elements.triggers) {
            if (this.state.openSections.has(trigger.dataset.sectionId)) {
                await this.closeSection(trigger);
            }
        }
    }
    
    async toggle(sectionId) {
        const trigger = this.elements.triggers.find(t => t.dataset.sectionId === sectionId);
        if (trigger) {
            await this.handleTriggerClick(trigger);
        }
    }
    
    isOpen(sectionId) {
        return this.state.openSections.has(sectionId);
    }
    
    getOpenSections() {
        return Array.from(this.state.openSections);
    }
    
    destroy() {
        // Remover event listeners
        this.elements.triggers.forEach(trigger => {
            trigger.replaceWith(trigger.cloneNode(true));
        });
        
        console.log('SmartAccordion destroyed');
    }
}

// Factory function
function createSmartAccordion(options) {
    return new SmartAccordion(options).init();
}

// Exportação para diferentes ambientes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SmartAccordion, createSmartAccordion };
} else if (typeof define === 'function' && define.amd) {
    define([], () => ({ SmartAccordion, createSmartAccordion }));
} else {
    window.SmartAccordion = SmartAccordion;
    window.createSmartAccordion = createSmartAccordion;
}

console.log('🚀 SmartAccordion Module v1.0.0 loaded!');