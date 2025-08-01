import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'getting-started',
    {
      type: 'category',
      label: '🏗️ Arquitetura',
      collapsible: true,
      collapsed: false,
      items: [
        'architecture/overview',
        'architecture/system-architecture',
        'architecture/multi-agent-system',
        'architecture/data-pipeline',
        'architecture/literature-review',
        'architecture/theoretical-foundations',
      ],
    },
    {
      type: 'category',
      label: '🤖 Agentes Especializados',
      collapsible: true,
      collapsed: true,
      items: [
        'agents/overview',
        'agents/abaporu-master',
        'agents/zumbi',
        'agents/tiradentes',
        'agents/anita-garibaldi',
        'agents/machado-assis',
        'agents/dandara',
        'agents/drummond',
        'agents/niemeyer',
      ],
    },
    {
      type: 'category',
      label: '🧮 Matemática & Algoritmos',
      collapsible: true,
      collapsed: true,
      items: [
        'math/overview',
        'math/math-foundations',
        'math/algorithms',
        'math/mathematical-proofs',
        'math/xai-algorithms',
      ],
    },
    {
      type: 'category',
      label: '🔌 API & Integração',
      collapsible: true,
      collapsed: true,
      items: [
        'api/api-reference',
        'api/datasets',
        'api/code-examples',
      ],
    },
  ],
};

export default sidebars;