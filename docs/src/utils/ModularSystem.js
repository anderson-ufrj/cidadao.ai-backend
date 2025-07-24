/**
 * Sistema Modular Principal
 * Integração com o JavaScript existente
 */

import ComponentLoader from './ComponentLoader.js';

class ModularSystem {
    constructor() {
        this.componentLoader = ComponentLoader;
        this.sectionsData = null;
        this.initialized = false;
        
        console.log('🎯 ModularSystem initialized');
    }

    /**
     * Inicialização do sistema modular
     */
    async init() {
        if (this.initialized) return;

        try {
            // Carregar dados das seções
            await this.loadSectionsData();
            
            // Inicializar ComponentLoader
            await this.componentLoader.init();
            
            // Integrar com sistema existente
            this.integrateWithExistingSystem();
            
            // Carregar componentes principais
            await this.loadMainComponents();
            
            this.initialized = true;
            console.log('✅ ModularSystem ready');
            
        } catch (error) {
            console.error('❌ ModularSystem initialization failed:', error);
            this.fallbackToOriginalSystem();
        }
    }

    /**
     * Carrega dados das seções
     */
    async loadSectionsData() {
        try {
            const response = await fetch('src/data/sections.json');
            if (!response.ok) {
                throw new Error('Failed to load sections data');
            }
            
            this.sectionsData = await response.json();
            console.log(`📊 Loaded ${this.sectionsData.metadata.totalSections} sections`);
            
        } catch (error) {
            console.error('❌ Error loading sections data:', error);
            throw error;
        }
    }

    /**
     * Integra com o sistema JavaScript existente
     */
    integrateWithExistingSystem() {
        // Verificar se o sistema original existe
        if (window.CidadaoAI) {
            console.log('🔗 Integrating with existing CidadaoAI system');
            
            // Estender funcionalidades existentes
            const originalSwitchTheme = window.CidadaoAI.switchTheme;
            window.CidadaoAI.switchTheme = (theme) => {
                originalSwitchTheme(theme);
                this.handleThemeChange(theme);
            };

            const originalSwitchLanguage = window.CidadaoAI.switchLanguage;
            window.CidadaoAI.switchLanguage = (language) => {
                originalSwitchLanguage(language);
                this.handleLanguageChange(language);
            };

            // Adicionar novas funcionalidades
            window.CidadaoAI.ModularSystem = this;
            window.CidadaoAI.ComponentLoader = this.componentLoader;
            
        } else {
            console.warn('⚠️ Original CidadaoAI system not found, creating basic integration');
            this.createBasicIntegration();
        }
    }

    /**
     * Cria integração básica se sistema original não existir
     */
    createBasicIntegration() {
        window.CidadaoAI = {
            ModularSystem: this,
            ComponentLoader: this.componentLoader,
            switchTheme: (theme) => this.handleThemeChange(theme),
            switchLanguage: (language) => this.handleLanguageChange(language)
        };
    }

    /**
     * Handle mudança de tema
     */
    handleThemeChange(theme) {
        // Atualizar componentes se necessário
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('cidadao-theme', theme);
        
        console.log(`🎨 Modular system theme updated: ${theme}`);
    }

    /**
     * Handle mudança de idioma
     */
    handleLanguageChange(language) {
        // Atualizar componentes se necessário
        localStorage.setItem('cidadao-language', language);
        
        console.log(`🌍 Modular system language updated: ${language}`);
    }

    /**
     * Carrega componentes principais
     */
    async loadMainComponents() {
        if (!this.sectionsData) return;

        try {
            // Carregar acordeão com dados reais
            await this.loadAccordionFromData();
            
            // Carregar modais se necessário
            await this.loadModalsFromData();
            
        } catch (error) {
            console.error('❌ Error loading main components:', error);
        }
    }

    /**
     * Carrega acordeão com dados estruturados
     */
    async loadAccordionFromData() {
        const accordion = document.getElementById('documentationAccordion');
        if (!accordion) return;

        // Verificar se já tem conteúdo (sistema original)
        if (accordion.children.length > 0) {
            console.log('📋 Accordion already has content, enhancing existing structure');
            this.enhanceExistingAccordion();
            return;
        }

        // Carregar com dados JSON
        console.log('🔄 Loading accordion from modular data');
        
        let accordionHTML = '';
        
        for (const category of this.sectionsData.categories) {
            // Carregar template de categoria
            let sectionsHTML = '';
            
            for (const section of category.sections) {
                const sectionTemplate = await this.componentLoader.loadComponent(
                    'accordion/AccordionItem', 
                    null, 
                    section
                );
                sectionsHTML += sectionTemplate;
            }
            
            const categoryTemplate = await this.componentLoader.loadComponent(
                'accordion/AccordionCategory',
                null,
                {
                    ...category,
                    sections: sectionsHTML
                }
            );
            
            accordionHTML += categoryTemplate;
        }
        
        accordion.innerHTML = accordionHTML;
        console.log('✅ Accordion loaded with modular system');
    }

    /**
     * Melhora acordeão existente
     */
    enhanceExistingAccordion() {
        // Adicionar data attributes para compatibilidade
        const categories = document.querySelectorAll('.accordion-category');
        const items = document.querySelectorAll('.accordion-item');
        
        categories.forEach((category, index) => {
            if (!category.dataset.category && this.sectionsData.categories[index]) {
                category.dataset.category = this.sectionsData.categories[index].id;
            }
        });
        
        items.forEach((item, index) => {
            if (!item.dataset.section) {
                // Tentar encontrar seção correspondente
                const section = this.findSectionByIndex(index);
                if (section) {
                    item.dataset.section = section.id;
                }
            }
        });
        
        console.log('✅ Enhanced existing accordion with modular attributes');
    }

    /**
     * Encontra seção por índice
     */
    findSectionByIndex(index) {
        let currentIndex = 0;
        
        for (const category of this.sectionsData.categories) {
            for (const section of category.sections) {
                if (currentIndex === index) {
                    return section;
                }
                currentIndex++;
            }
        }
        
        return null;
    }

    /**
     * Carrega modais com dados
     */
    async loadModalsFromData() {
        // Lista de modais para carregar
        const modalsToLoad = [
            { id: 'aboutModal', title: 'Sobre o Cidadão.AI Backend', size: 'modal-large' },
            { id: 'architectureModal', title: 'Arquitetura do Sistema', size: 'modal-extra-large' },
            { id: 'readingModal', title: 'Modo Leitura', size: 'modal-full-width', class: 'reading-modal' }
        ];

        for (const modal of modalsToLoad) {
            const existingModal = document.getElementById(modal.id);
            if (!existingModal) {
                // Criar modal se não existir
                const modalHTML = await this.componentLoader.loadComponent(
                    'modals/BaseModal',
                    null,
                    {
                        modalId: modal.id,
                        title: modal.title,
                        modalSize: modal.size,
                        content: '<p>Conteúdo será carregado dinamicamente...</p>'
                    }
                );
                
                document.body.insertAdjacentHTML('beforeend', modalHTML);
            }
        }
        
        console.log('✅ Modals loaded/enhanced');
    }

    /**
     * Fallback para sistema original
     */
    fallbackToOriginalSystem() {
        console.log('🔄 Falling back to original system');
        
        // Remover indicador modular
        const statusIndicator = document.querySelector('[style*="Sistema Modular Ativo"]');
        if (statusIndicator) {
            statusIndicator.textContent = '⚠️ Modo Compatibilidade';
            statusIndicator.style.background = '#f59e0b';
        }
        
        // Garantir que sistema original funcione
        if (window.CidadaoAI && window.CidadaoAI.initializeApp) {
            window.CidadaoAI.initializeApp();
        }
    }

    /**
     * Estatísticas do sistema
     */
    getStats() {
        return {
            initialized: this.initialized,
            sectionsLoaded: this.sectionsData ? this.sectionsData.metadata.totalSections : 0,
            categoriesLoaded: this.sectionsData ? this.sectionsData.metadata.totalCategories : 0,
            componentLoader: this.componentLoader.getStats()
        };
    }

    /**
     * Recarregar sistema
     */
    async reload() {
        this.initialized = false;
        await this.init();
    }
}

// Instância global
const modularSystem = new ModularSystem();

// Auto-inicialização
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        modularSystem.init();
    });
} else {
    modularSystem.init();
}

// Exportar para uso global
window.ModularSystem = modularSystem;

export default modularSystem;