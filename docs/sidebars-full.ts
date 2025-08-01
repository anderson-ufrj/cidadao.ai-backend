import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Configuração dos sidebars da documentação técnica do Cidadão.AI Backend
 * 
 * Estrutura hierárquica baseada na arquitetura do sistema:
 * - Fundamentos e introdução
 * - Arquitetura do sistema multi-agente
 * - Fundamentos matemáticos e algoritmos
 * - API e integração
 * - Contribuição e desenvolvimento
 */
const sidebars: SidebarsConfig = {
  // Sidebar principal da documentação (apenas arquivos migrados)
  tutorialSidebar: [
    // ============================================
    // 🚀 FUNDAMENTOS
    // ============================================
    {
      type: 'doc',
      id: 'intro',
      label: '🏠 Introdução',
    },
    {
      type: 'doc',
      id: 'getting-started',
      label: '⚡ Início Rápido',
    },

    // ============================================
    // 🏗️ ARQUITETURA DO SISTEMA (MIGRADO)
    // ============================================
    {
      type: 'category',
      label: '🏗️ Arquitetura',
      collapsible: true,
      collapsed: false,
      items: [
        'architecture/overview-clean',
        'architecture/system-architecture',
        'architecture/multi-agent-system',
        'architecture/data-pipeline',
      ],
    },

    // ============================================
    // 🧮 MATEMÁTICA (SIMPLIFICADO)
    // ============================================
    {
      type: 'category',
      label: '🧮 Matemática & Algoritmos',
      collapsible: true,
      collapsed: true,
      items: [
        'math/overview',
      ],
    },

    // ============================================
    // 🤖 AGENTES (SIMPLIFICADO)
    // ============================================
    {
      type: 'category',
      label: '🤖 Agentes Especializados',
      collapsible: true,
      collapsed: true,
      items: [
        'agents/overview',
      ],
    },
  ],

};

export default sidebars;