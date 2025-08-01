import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'getting-started',
    {
      type: 'category',
      label: '🏗️ Arquitetura',
      collapsible: true,
      collapsed: true,
      items: [
        'architecture/overview',
        'architecture/design-sistema',
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
        'agents/multi-agent-overview',
        'agents/abaporu-master',
        'agents/ayrton-senna',
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
      label: '🔌 API & Integração',
      collapsible: true,
      collapsed: true,
      items: [
        'api/visao-geral',
        'api/autenticacao',
        {
          type: 'category',
          label: 'Endpoints',
          items: [
            'api/endpoints/visao-geral',
            'api/endpoints/investigacoes',
          ],
        },
        'api/api-reference',
        'api/datasets',
        'api/code-examples',
        'api/swagger-ui',
      ],
    },
    {
      type: 'category',
      label: '🤖 Machine Learning',
      collapsible: true,
      collapsed: true,
      items: [
        'ml/visao-geral-pipeline',
      ],
    },
    {
      type: 'category',
      label: '🧮 Matemática & Algoritmos',
      collapsible: true,
      collapsed: true,
      items: [
        'math/overview',
        'math/fundamentos-teoricos',
        'math/math-foundations',
        'math/algorithms',
        'math/mathematical-proofs',
        'math/xai-algorithms',
      ],
    },
  ],
};

export default sidebars;