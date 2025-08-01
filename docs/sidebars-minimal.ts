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
        'architecture/overview-clean',
        'architecture/system-architecture',
        'architecture/data-pipeline',
      ],
    },
    {
      type: 'category',
      label: '🤖 Agentes',
      collapsible: true,
      collapsed: true,
      items: [
        'agents/overview',
      ],
    },
  ],
};

export default sidebars;