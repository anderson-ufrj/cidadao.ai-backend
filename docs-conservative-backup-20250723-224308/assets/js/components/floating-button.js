/**
 * FloatingButton - Módulo Reutilizável
 * 
 * Componente de botão flutuante configurável para qualquer projeto web
 * Zero dependencies - JavaScript puro
 * 
 * @author Anderson Henrique da Silva
 * @version 1.0.0
 */

class FloatingButton {
    constructor(options = {}) {
        // Configurações padrão
        this.config = {
            // Visual
            icon: options.icon || 'ℹ️',
            backgroundColor: options.backgroundColor || 'linear-gradient(135deg, #10b981, #059669)',
            color: options.color || 'white',
            size: options.size || 60,
            
            // Posicionamento
            position: options.position || 'bottom-right',
            margin: options.margin || '2rem',
            
            // Comportamento
            onClick: options.onClick || (() => console.log('FloatingButton clicked!')),
            zIndex: options.zIndex || 99999,
            
            // Animações
            enableHover: options.enableHover !== false,
            hoverScale: options.hoverScale || 1.1,
            
            // Acessibilidade
            ariaLabel: options.ariaLabel || 'Botão de ação flutuante',
            
            // CSS Classes
            className: options.className || 'floating-button-module',
            
            // Identificador único
            id: options.id || 'floating-btn-' + Date.now()
        };
        
        this.button = null;
        this.isVisible = true;
    }
    
    /**
     * Cria e renderiza o botão
     */
    render() {
        // Remover botão existente se houver
        this.destroy();
        
        // Criar elemento do botão
        this.button = document.createElement('button');
        this.button.id = this.config.id;
        this.button.className = this.config.className;
        this.button.innerHTML = this.config.icon;
        this.button.setAttribute('aria-label', this.config.ariaLabel);
        
        // Aplicar estilos
        this._applyStyles();
        
        // Adicionar event listeners
        this._attachEvents();
        
        // Adicionar ao DOM
        document.body.appendChild(this.button);
        
        return this;
    }
    
    /**
     * Aplica os estilos CSS ao botão
     */
    _applyStyles() {
        const { position, margin, size, backgroundColor, color, zIndex } = this.config;
        
        // Calcular posição
        const [vertical, horizontal] = position.split('-');
        
        this.button.style.cssText = `
            position: fixed !important;
            ${vertical}: ${margin} !important;
            ${horizontal}: ${margin} !important;
            width: ${size}px !important;
            height: ${size}px !important;
            border-radius: 50% !important;
            background: ${backgroundColor} !important;
            color: ${color} !important;
            border: none !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: ${size * 0.4}px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.3s ease !important;
            z-index: ${zIndex} !important;
            user-select: none !important;
            outline: none !important;
        `;
    }
    
    /**
     * Anexa event listeners
     */
    _attachEvents() {
        // Click handler
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            this.config.onClick(e, this);
        });
        
        // Hover effects (se habilitado)
        if (this.config.enableHover) {
            this.button.addEventListener('mouseenter', () => {
                this.button.style.transform = `scale(${this.config.hoverScale})`;
                this.button.style.boxShadow = '0 6px 25px rgba(0, 0, 0, 0.2)';
            });
            
            this.button.addEventListener('mouseleave', () => {
                this.button.style.transform = 'scale(1)';
                this.button.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
            });
        }
        
        // Keyboard accessibility
        this.button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.config.onClick(e, this);
            }
        });
    }
    
    /**
     * Atualiza configurações do botão
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        if (this.button) {
            this._applyStyles();
        }
        return this;
    }
    
    /**
     * Mostra o botão
     */
    show() {
        if (this.button) {
            this.button.style.display = 'flex';
            this.isVisible = true;
        }
        return this;
    }
    
    /**
     * Esconde o botão
     */
    hide() {
        if (this.button) {
            this.button.style.display = 'none';
            this.isVisible = false;
        }
        return this;
    }
    
    /**
     * Toggle visibilidade
     */
    toggle() {
        return this.isVisible ? this.hide() : this.show();
    }
    
    /**
     * Remove o botão do DOM
     */
    destroy() {
        if (this.button && this.button.parentNode) {
            this.button.parentNode.removeChild(this.button);
            this.button = null;
        }
        return this;
    }
    
    /**
     * Verifica se o botão está renderizado
     */
    isRendered() {
        return this.button && document.body.contains(this.button);
    }
}

/**
 * Factory function para criação rápida
 */
function createFloatingButton(options) {
    return new FloatingButton(options).render();
}

/**
 * Função utilitária para compatibilidade com código legado
 */
function recreateFloatingButton(options = {}) {
    // Configuração padrão para compatibilidade
    const defaultOptions = {
        icon: 'ℹ️',
        onClick: () => {
            if (window.CidadaoAI && window.CidadaoAI.openModal) {
                window.CidadaoAI.openModal('aboutModal');
            } else {
                console.log('Modal system not available');
            }
        },
        ariaLabel: 'Abrir informações sobre o projeto'
    };
    
    return createFloatingButton({ ...defaultOptions, ...options });
}

// Exportações para diferentes ambientes
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = { FloatingButton, createFloatingButton, recreateFloatingButton };
} else if (typeof define === 'function' && define.amd) {
    // AMD
    define([], () => ({ FloatingButton, createFloatingButton, recreateFloatingButton }));
} else {
    // Browser global
    window.FloatingButton = FloatingButton;
    window.createFloatingButton = createFloatingButton;
    window.recreateFloatingButton = recreateFloatingButton;
}

console.log('🚀 FloatingButton Module v1.0.0 loaded!');