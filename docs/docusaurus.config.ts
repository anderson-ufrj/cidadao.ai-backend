import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const config: Config = {
  title: 'Cidadão.AI Backend',
  tagline: 'Sistema Multi-Agente para Transparência Pública Brasileira',
  favicon: 'img/favicon.ico',

  // Configurações de produção
  url: 'https://anderson-ufrj.github.io',
  baseUrl: '/cidadao.ai-docs/',
  organizationName: 'anderson-ufrj',
  projectName: 'cidadao.ai-docs',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Internacionalização
  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR', 'en-US'],
    localeConfigs: {
      'pt-BR': {
        label: '🇧🇷 Português',
        direction: 'ltr',
        htmlLang: 'pt-BR',
      },
      'en-US': {
        label: '🇺🇸 English',
        direction: 'ltr',
        htmlLang: 'en-US',
      },
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/anderson-ufrj/cidadao.ai-backend/tree/main/docs/',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          breadcrumbs: true,
          routeBasePath: 'docs',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: 'all',
            copyright: `Copyright © ${new Date().getFullYear()} Anderson Henrique da Silva`,
          },
          editUrl: 'https://github.com/anderson-ufrj/cidadao.ai-backend/tree/main/docs/',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
        },
        theme: {
          customCss: './src/css/custom.css',
        },
        gtag: {
          trackingID: 'G-XXXXX', // Substituir por GA real se necessário
          anonymizeIP: true,
        },
      } satisfies Preset.Options,
    ],
  ],

  // Plugin para Mermaid (diagramas)
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
  ],

  themeConfig: {
    // SEO e metadados
    image: 'img/cidadao-ai-social-card.jpg',
    metadata: [
      {name: 'keywords', content: 'cidadao-ai, transparencia-publica, ia-etica, multi-agente, fastapi, python'},
      {name: 'description', content: 'Documentação técnica completa do Cidadão.AI Backend - Sistema multi-agente de IA para análise de transparência governamental brasileira'},
      {property: 'og:type', content: 'website'},
      {property: 'og:site_name', content: 'Cidadão.AI Backend Documentation'},
    ],

    // Navbar
    navbar: {
      title: 'Cidadão.AI',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: '📚 Documentação',
        },
        {
          to: '/blog',
          label: '📰 Blog',
          position: 'left'
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/anderson-ufrj/cidadao.ai-backend',
          label: '⚡ GitHub',
          position: 'right',
        },
        {
          href: 'https://cidadao-ai-frontend.vercel.app',
          label: '🌐 Demo',
          position: 'right',
        },
      ],
    },

    // Footer
    footer: {
      style: 'dark',
      links: [
        {
          title: '📖 Documentação',
          items: [
            {
              label: 'Introdução',
              to: '/docs/intro',
            },
            {
              label: 'Arquitetura',
              to: '/docs/architecture/overview',
            },
            {
              label: 'API Reference',
              to: '/docs/api/endpoints',
            },
            {
              label: 'Fundamentos Matemáticos',
              to: '/docs/math/theorems',
            },
          ],
        },
        {
          title: '🤖 Sistema Multi-Agente',
          items: [
            {
              label: 'Agentes Especializados',
              to: '/docs/architecture/agents',
            },
            {
              label: 'Roteamento Semântico',
              to: '/docs/architecture/routing',
            },
            {
              label: 'Memória Contextual',
              to: '/docs/architecture/memory',
            },
          ],
        },
        {
          title: '🔗 Links Oficiais',
          items: [
            {
              label: 'Frontend Demo',
              href: 'https://cidadao-ai-frontend.vercel.app',
            },
            {
              label: 'GitHub Backend',
              href: 'https://github.com/anderson-ufrj/cidadao.ai-backend',
            },
            {
              label: 'GitHub Frontend',
              href: 'https://github.com/anderson-ufrj/cidadao.ai-frontend',
            },
            {
              label: 'Hugging Face',
              href: 'https://huggingface.co/neural-thinker',
            },
          ],
        },
        {
          title: '📬 Contato & Suporte',
          items: [
            {
              label: 'Issues GitHub',
              href: 'https://github.com/anderson-ufrj/cidadao.ai-backend/issues',
            },
            {
              label: 'Discussões',
              href: 'https://github.com/anderson-ufrj/cidadao.ai-backend/discussions',
            },
            {
              label: 'LinkedIn',
              href: 'https://linkedin.com/in/anderson-h-silva95',
            },
            {
              label: 'Email',
              href: 'mailto:andersonhs27@gmail.com',
            },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} <strong>Anderson Henrique da Silva</strong> — Instituto Federal do Sul de Minas Gerais.<br/>
                  Licenciado sob <a href="https://opensource.org/licenses/Apache-2.0" target="_blank">Apache License 2.0</a>. 
                  Construído com ❤️ e <a href="https://docusaurus.io/" target="_blank">Docusaurus</a>.`,
    },

    // Configurações do tema
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'python', 'typescript', 'yaml', 'docker', 'sql'],
    },

    // Configurações de busca (Algolia - opcional)
    // algolia: {
    //   appId: 'YOUR_APP_ID',
    //   apiKey: 'YOUR_SEARCH_API_KEY',
    //   indexName: 'cidadao-ai-docs',
    //   contextualSearch: true,
    //   searchParameters: {},
    //   searchPagePath: 'search',
    // },

    // Configurações de acessibilidade
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    // Anúncios (opcional)
    announcementBar: {
      id: 'alpha_version',
      content: '🚧 <strong>Documentação em construção</strong> — Esta é uma versão alpha. Contribua no <a target="_blank" rel="noopener noreferrer" href="https://github.com/anderson-ufrj/cidadao.ai-backend">GitHub</a>!',
      backgroundColor: '#ffeaa7',
      textColor: '#2d3436',
      isCloseable: true,
    },

  } satisfies Preset.ThemeConfig,

  // Plugins adicionais
  plugins: [
    // Plugin para análise de bundle (opcional)
    // [
    //   '@docusaurus/plugin-pwa',
    //   {
    //     debug: true,
    //     offlineModeActivationStrategies: [
    //       'appInstalled',
    //       'standalone',
    //       'queryString',
    //     ],
    //     pwaHead: [
    //       {
    //         tagName: 'link',
    //         rel: 'icon',
    //         href: '/img/logo.png',
    //       },
    //       {
    //         tagName: 'link',
    //         rel: 'manifest',
    //         href: '/manifest.json',
    //       },
    //       {
    //         tagName: 'meta',
    //         name: 'theme-color',
    //         content: '#2E8B57',
    //       },
    //     ],
    //   },
    // ],
  ],
};

export default config;