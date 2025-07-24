/**
 * ContentLoader - Sistema de Carregamento Dinâmico
 * 
 * Gerencia carregamento lazy de seções de conteúdo para performance otimizada
 * 
 * @author Anderson Henrique da Silva
 * @version 1.0.0
 */

class ContentLoader {
    constructor(options = {}) {
        this.config = {
            // Container principal
            container: options.container || '#technical-sections',
            
            // Configurações de carregamento
            loadingDelay: options.loadingDelay || 200,
            animationDuration: options.animationDuration || 300,
            
            // Configurações de cache
            enableCache: options.enableCache !== false,
            cacheTimeout: options.cacheTimeout || 300000, // 5 minutos
            
            // URLs dos dados
            dataUrl: options.dataUrl || './data/sections.json',
            
            // Callbacks
            onSectionLoad: options.onSectionLoad || (() => {}),
            onError: options.onError || console.error
        };
        
        this.state = {
            loadedSections: new Set(),
            cache: new Map(),
            isLoading: false
        };
    }
    
    /**
     * Inicializa o sistema de carregamento
     */
    async init() {
        try {
            // Carregar metadados das seções
            await this.loadSectionMetadata();
            
            // Configurar observers para lazy loading
            this.setupIntersectionObserver();
            
            console.log('🚀 ContentLoader initialized successfully');
            return this;
        } catch (error) {
            this.config.onError('Failed to initialize ContentLoader:', error);
            throw error;
        }
    }
    
    /**
     * Carrega metadados das seções
     */
    async loadSectionMetadata() {
        try {
            const response = await fetch(this.config.dataUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            this.metadata = await response.json();
            return this.metadata;
        } catch (error) {
            console.warn('Failed to load section metadata, using fallback');
            this.metadata = this.getFallbackMetadata();
            return this.metadata;
        }
    }
    
    /**
     * Metadados de fallback caso o JSON não carregue
     */
    getFallbackMetadata() {
        return {
            sections: {
                'overview': {
                    title: 'Visão Geral',
                    priority: 'high',
                    size: 'small'
                },
                'architecture': {
                    title: 'Arquitetura',
                    priority: 'high', 
                    size: 'large'
                },
                'agents': {
                    title: 'Sistema Multi-Agente',
                    priority: 'medium',
                    size: 'large'
                },
                'deployment': {
                    title: 'Deploy e Infraestrutura',
                    priority: 'medium',
                    size: 'medium'
                }
            }
        };
    }
    
    /**
     * Configura intersection observer para lazy loading
     */
    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };
        
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.dataset.sectionId;
                    if (sectionId && !this.state.loadedSections.has(sectionId)) {
                        this.loadSection(sectionId);
                    }
                }
            });
        }, options);
        
        // Observar elementos com data-section-id
        document.querySelectorAll('[data-section-id]').forEach(el => {
            this.observer.observe(el);
        });
    }
    
    /**
     * Carrega uma seção específica
     */
    async loadSection(sectionId) {
        if (this.state.loadedSections.has(sectionId) || this.state.isLoading) {
            return;
        }
        
        this.state.isLoading = true;
        
        try {
            // Verificar cache primeiro
            let content = this.getFromCache(sectionId);
            
            if (!content) {
                // Simular carregamento (em produção, viria de API ou chunks)
                content = await this.fetchSectionContent(sectionId);
                
                // Armazenar no cache
                if (this.config.enableCache) {
                    this.setCache(sectionId, content);
                }
            }
            
            // Renderizar conteúdo
            await this.renderSection(sectionId, content);
            
            // Marcar como carregado
            this.state.loadedSections.add(sectionId);
            
            // Callback
            this.config.onSectionLoad(sectionId, content);
            
        } catch (error) {
            this.config.onError(`Failed to load section ${sectionId}:`, error);
        } finally {
            this.state.isLoading = false;
        }
    }
    
    /**
     * Busca conteúdo da seção (simulado)
     */
    async fetchSectionContent(sectionId) {
        // Simular delay de rede
        await new Promise(resolve => setTimeout(resolve, this.config.loadingDelay));
        
        // Em produção, isso viria de uma API ou chunks separados
        const contentMap = {
            'overview': this.generateOverviewContent(),
            'architecture': this.generateArchitectureContent(),
            'agents': this.generateAgentsContent(),
            'deployment': this.generateDeploymentContent()
        };
        
        return contentMap[sectionId] || `<p>Conteúdo da seção ${sectionId} não encontrado.</p>`;
    }
    
    /**
     * Renderiza seção no DOM
     */
    async renderSection(sectionId, content) {
        const container = document.querySelector(`[data-section-id="${sectionId}"] .accordion-content`);
        if (!container) return;
        
        // Adicionar loading state
        container.innerHTML = '<div class="loading">Carregando...</div>';
        
        // Simular processamento
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Renderizar conteúdo real
        container.innerHTML = content;
        
        // Animar entrada
        container.style.opacity = '0';
        setTimeout(() => {
            container.style.transition = `opacity ${this.config.animationDuration}ms ease`;
            container.style.opacity = '1';
        }, 50);
    }
    
    /**
     * Gerenciamento de cache
     */
    getFromCache(sectionId) {
        if (!this.config.enableCache) return null;
        
        const cached = this.state.cache.get(sectionId);
        if (!cached) return null;
        
        // Verificar expiração
        if (Date.now() - cached.timestamp > this.config.cacheTimeout) {
            this.state.cache.delete(sectionId);
            return null;
        }
        
        return cached.content;
    }
    
    setCache(sectionId, content) {
        if (!this.config.enableCache) return;
        
        this.state.cache.set(sectionId, {
            content,
            timestamp: Date.now()
        });
    }
    
    /**
     * Generators de conteúdo (placeholders para desenvolvimento)
     */
    generateOverviewContent() {
        return `
            <div class="content-section">
                <h3>🎯 Visão Geral do Sistema</h3>
                <p>O Cidadão.AI Backend representa uma implementação de classe enterprise...</p>
                <ul>
                    <li>Score Técnico: 9.4/10</li>
                    <li>17 Agentes Especializados</li>
                    <li>Arquitetura Production-Ready</li>
                </ul>
            </div>
        `;
    }
    
    generateArchitectureContent() {
        return `
            <div class="content-section">
                <h3>🏗️ Arquitetura do Sistema</h3>
                <p>Arquitetura multi-agente com separação clara de responsabilidades...</p>
                <div class="tech-stack">
                    <h4>Stack Tecnológica:</h4>
                    <p><strong>Backend:</strong> FastAPI + Python 3.11+ + PostgreSQL</p>
                    <p><strong>IA:</strong> LangChain + Transformers + OpenAI/Groq</p>
                    <p><strong>Infraestrutura:</strong> Docker + Kubernetes + Redis</p>
                </div>
            </div>
        `;
    }
    
    generateAgentsContent() {
        return `
            <div class="content-section">
                <h3>🤖 Sistema Multi-Agente</h3>
                <p>17 agentes especializados com identidade brasileira...</p>
                <div class="agents-grid">
                    <div class="agent-card">
                        <h4>MasterAgent (Abaporu)</h4>
                        <p>Orquestração central com auto-reflexão</p>
                    </div>
                    <div class="agent-card">
                        <h4>InvestigatorAgent</h4>
                        <p>Detecção de anomalias em dados públicos</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    generateDeploymentContent() {
        return `
            <div class="content-section">
                <h3>🚀 Deploy e Infraestrutura</h3>
                <p>Sistema containerizado pronto para produção...</p>
                <div class="deployment-info">
                    <h4>Opções de Deploy:</h4>
                    <ul>
                        <li>Docker Compose (desenvolvimento)</li>
                        <li>Kubernetes (produção)</li>
                        <li>Railway/Render (cloud)</li>
                    </ul>
                </div>
            </div>
        `;
    }
    
    /**
     * Utilitários públicos
     */
    preloadSection(sectionId) {
        if (!this.state.loadedSections.has(sectionId)) {
            this.loadSection(sectionId);
        }
    }
    
    clearCache() {
        this.state.cache.clear();
        console.log('ContentLoader cache cleared');
    }
    
    getLoadedSections() {
        return Array.from(this.state.loadedSections);
    }
}

// Exportação para diferentes ambientes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ContentLoader };
} else if (typeof define === 'function' && define.amd) {
    define([], () => ({ ContentLoader }));
} else {
    window.ContentLoader = ContentLoader;
}

console.log('🚀 ContentLoader Module v1.0.0 loaded!');