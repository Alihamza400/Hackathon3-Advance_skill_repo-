#!/bin/bash
# Create Docusaurus site configuration and boilerplate

DOC_NAME="$1"

if [ -z "$DOC_NAME" ]; then
    echo "Usage: $0 <doc-name>"
    echo "Example: $0 learnflow-docs"
    exit 1
}

DOC_DIR="./docs/$DOC_NAME"

# Create documentation directory
mkdir -p "$DOC_DIR"

echo "Scaffolding Docusaurus site '$DOC_NAME' in $DOC_DIR..."

# Initialize a basic Docusaurus project
# This assumes `npx create-docusaurus` is available in the environment.
# For an enterprise setup, this might be a custom template.

# Create a dummy package.json and basic Docusaurus structure
cat > "$DOC_DIR/package.json" << EOF
{
  "name": "$DOC_NAME",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "docusaurus": "docusaurus",
    "start": "docusaurus start",
    "build": "docusaurus build",
    "swizzle": "docusaurus swizzle",
    "deploy": "docusaurus deploy",
    "clear": "docusaurus clear",
    "serve": "docusaurus serve",
    "write-translations": "docusaurus write-translations",
    "write-heading-ids": "docusaurus write-heading-ids"
  },
  "dependencies": {
    "@docusaurus/core": "^2.0.0",
    "@docusaurus/preset-classic": "^2.0.0",
    "clsx": "^1.1.1",
    "prism-react-renderer": "^1.2.1",
    "react": "^17.0.2",
    "react-dom": "^17.0.2"
  },
  "browserslist": {
    "production": [
      ">0.5%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

mkdir -p "$DOC_DIR/src/pages"
cat > "$DOC_DIR/src/pages/index.js" << EOF
import React from 'react';
import Layout from '@theme/Layout';

function Home() {
  return (
    <Layout
      title="Welcome to ${DOC_NAME}"
      description="Description will go into a meta tag in <head />">
      <main>
        <h1>Hello Docusaurus</h1>
        <p>This is your new documentation site.</p>
      </main>
    </Layout>
  );
}

export default Home;
EOF

mkdir -p "$DOC_DIR/docs"
cat > "$DOC_DIR/docusaurus.config.js" << EOF
// @ts-check
// Note: type annotations allow type checking and IDEs to provide autocompletion

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: '${DOC_NAME}',
  tagline: 'Documentation for your Enterprise Application',
  url: 'https://${DOC_NAME}.your-enterprise.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  // GitHub pages deployment config.
  organizationName: 'your-enterprise-org', // Usually your GitHub org/user name.
  projectName: '${DOC_NAME}', // Usually your repo name.

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo. For example: https://github.com/facebook/docusaurus
          editUrl:
            'https://github.com/your-enterprise-org/${DOC_NAME}/tree/main/packages/docs/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo. For example: https://github.com/facebook/docusaurus
          editUrl:
            'https://github.com/your-enterprise-org/${DOC_NAME}/tree/main/packages/blog/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: '${DOC_NAME}',
        logo: {
          alt: 'My Site Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'doc',
            docId: 'intro',
            position: 'left',
            label: 'Tutorial',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/your-enterprise-org/${DOC_NAME}',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Tutorial',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              },
              {
                label: 'Discord',
                href: 'https://discordapp.com/invite/docusaurus',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/docusaurus',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {label: 'Blog', to: '/blog'},
              {label: 'GitHub', href: 'https://github.com/your-enterprise-org/${DOC_NAME}'},
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Your Enterprise, Inc. Built with Docusaurus and Opencode.`,
      },
      prism: {
        theme: require('./src/css/draculaTheme'),
        darkTheme: require('./src/css/draculaTheme'),
      },
    }),
};

module.exports = config;
EOF

# Create a basic sidebar config
cat > "$DOC_DIR/sidebars.js" << EOF
/**
 * Creating a sidebar enables you to:1. create an ordered group of docs
 * 2. render a sidebar in the docs sidebars
 * 3. have a left sidebar
 */

module.exports = {
  tutorialSidebar: [
    {type: 'autogenerated', dirName: '.'},
  ],
};
EOF

# Create a basic custom CSS file
mkdir -p "$DOC_DIR/src/css"
cat > "$DOC_DIR/src/css/custom.css" << EOF
/**
 * Any CSS here will be applied to all pages on the site.
 */

/* You can override the default Infima variables here. */
.hero__title {
  font-size: 3rem;
}

.navbar__title {
  font-weight: bold;
}
EOF

# Create a dummy blog post and doc
mkdir -p "$DOC_DIR/blog"
cat > "$DOC_DIR/blog/2023-01-01-welcome.md" << EOF
---
slug: welcome
title: Welcome to Enterprise Docs
authors: [opencode]
tags: [welcome, enterprise, docs]
---

This is your first enterprise blog post. More to come!
EOF

mkdir -p "$DOC_DIR/docs"
cat > "$DOC_DIR/docs/intro.md" << EOF
---
id: intro
title: Introduction to LearnFlow
sidebar_label: Introduction
---

Welcome to the LearnFlow enterprise documentation. This section provides an overview of the platform.
EOF

# Only this output enters agent context:
echo "✓ Docusaurus site '$DOC_NAME' boilerplate created with enterprise configurations."
