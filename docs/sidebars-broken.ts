import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
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
    {
      type: 'category',
      label: '🏗️ Arquitetura',
      collapsible: true,
      collapsed: false,
      items: [
        'architecture/overview-clean',
      ],
    },
  ],
};

export default sidebars;