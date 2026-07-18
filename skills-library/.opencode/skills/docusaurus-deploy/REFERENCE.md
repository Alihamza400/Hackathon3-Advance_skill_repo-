# Docusaurus Kubernetes Deployment Skill - Enterprise Reference

## Overview
The `docusaurus-deploy` skill provides enterprise-grade deployment of Docusaurus documentation sites on Kubernetes with production-ready configurations including search, analytics, versioning, multi-language support, and enterprise security.

## Skill Architecture

### File Structure
```
docusaurus-deploy/
├── SKILL.md                 # Agent instructions (~100 tokens)
├── REFERENCE.md             # This document (loaded on-demand)
└── scripts/
    ├── create_docusaurus.sh # Scaffold Docusaurus project
    ├── configure_docusaurus.sh # Enterprise configuration
    ├── build_docusaurus.sh # Static site generation
    ├── deploy_docusaurus.sh # Kubernetes deployment
    ├── configure_search.sh # Algolia DocSearch setup
    └── verify_docusaurus.sh # Deployment verification
```

## Enterprise Features

### 1. Project Scaffolding
The `create_docusaurus.sh` script creates a production-ready Docusaurus v3 project:

- **TypeScript Configuration**: Strict mode, path aliases, strict null checks
- **Theme Customization**: Professional enterprise theme with dark mode
- **Plugin Configuration**: SEO, sitemap, PWA, analytics, ideal-image
- **Content Structure**: Docs, blog, versioned docs, i18n, API reference
- **CI/CD Integration**: GitHub Actions for build and deploy
- **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options

### 2. Enterprise Configuration
The `configure_docusaurus.sh` script applies enterprise settings:

```javascript
// docusaurus.config.js enterprise features
module.exports = {
  // Core
  title: 'Enterprise Docs',
  tagline: 'Production-ready documentation',
  url: 'https://docs.your-enterprise.com',
  baseUrl: '/',
  
  // Enterprise SEO
  trailingSlash: false,
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  
  // Internationalization
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'fr', 'de', 'ja', 'zh'],
    localeConfigs: {
      en: { label: 'English', direction: 'ltr', htmlLang: 'en-US' },
      es: { label: 'Español', direction: 'ltr', htmlLang: 'es-ES' },
      fr: { label: 'Français', direction: 'ltr', htmlLang: 'fr-FR' },
      de: { label: 'Deutsch', direction: 'ltr', htmlLang: 'de-DE' },
      ja: { label: '日本語', direction: 'ltr', htmlLang: 'ja-JP' },
      zh: { label: '中文', direction: 'ltr', htmlLang: 'zh-CN' },
    },
  },
  
  // Advanced Presets
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/enterprise/docs/edit/main/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          versions: {
            current: { label: 'Latest', banner: 'none' },
            '2.1': { label: 'v2.1', banner: 'none' },
            '2.0': { label: 'v2.0 (LTS)', banner: 'This version is no longer actively maintained.' },
            '1.0': { label: 'v1.0 (Archived)', banner: 'This version is archived and no longer receives updates.', className: 'version-banner--archived' },
          },
        },
        blog: {
          showReadingTime: true,
          postsPerPage: 10,
          blogSidebarTitle: 'All posts',
          blogSidebarCount: 'ALL',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
          ignorePatterns: ['/tags/**'],
          filename: 'sitemap.xml',
        },
        gtag: {
          trackingID: 'G-XXXXXXXXXX',
          anonymizeIP: true,
        },
      },
    ],
  ],
  
  // Plugins
  plugins: [
    [
      '@docusaurus/plugin-ideal-image',
      { quality: 70, max: 1030, min: 640, steps: 2, disableInDev: false },
    ],
    [
      '@docusaurus/plugin-pwa',
      {
        debug: false,
        offlineModeActivationStrategies: ['appInstalled', 'standalone', 'queryString'],
        pwaHead: [
          { tagName: 'link', rel: 'icon', href: '/img/logo.svg' },
          { tagName: 'link', rel: 'manifest', href: '/manifest.json' },
          { tagName: 'meta', name: 'theme-color', content: '#2563eb' },
        ],
      },
    ],
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'api',
        path: 'api',
        routeBasePath: 'api',
        sidebarPath: require.resolve('./sidebars-api.js'),
      },
    ],
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'guides',
        path: 'guides',
        routeBasePath: 'guides',
        sidebarPath: require.resolve('./sidebars-guides.js'),
      },
    ],
  ],
  
  // Theme Config
  themeConfig: {
    // Announcement bar
    announcementBar: {
      id: 'support_us',
      content: '⭐️ If you like our docs, give us a star on <a href="https://github.com/enterprise/docs" target="_blank">GitHub</a>!',
      backgroundColor: '#fafbfc',
      textColor: '#091E42',
      isCloseable: true,
    },
    
    // Navbar
    navbar: {
      title: 'Enterprise Docs',
      logo: { alt: 'Logo', src: 'img/logo.svg', srcDark: 'img/logo_dark.svg' },
      items: [
        { type: 'doc', docId: 'intro', label: 'Docs', position: 'left' },
        { to: '/guides', label: 'Guides', position: 'left' },
        { to: '/api', label: 'API Reference', position: 'left' },
        { to: '/blog', label: 'Blog', position: 'left' },
        { type: 'docsVersionDropdown', position: 'right' },
        { type: 'localeDropdown', position: 'right' },
        {
          href: 'https://github.com/enterprise/docs',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    
    // Footer
    footer: {
      style: 'dark',
      links: [
        { title: 'Docs', items: [{ label: 'Tutorial', to: '/docs/intro' }, { label: 'API Reference', to: '/api' }] },
        { title: 'Community', items: [{ label: 'Stack Overflow', href: 'https://stackoverflow.com/questions/tagged/enterprise' }, { label: 'Discord', href: 'https://discord.gg/enterprise' }] },
        { title: 'More', items: [{ label: 'Blog', to: '/blog' }, { label: 'GitHub', href: 'https://github.com/enterprise/docs' }] },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Enterprise, Inc. Built with Docusaurus.`,
    },
    
    // Search
    algolia: {
      appId: process.env.ALGOLIA_APP_ID,
      apiKey: process.env.ALGOLIA_SEARCH_API_KEY,
      indexName: process.env.ALGOLIA_INDEX_NAME,
      contextualSearch: true,
      searchParameters: { facetFilters: ['version:current'] },
    },
    
    // Code blocks
    prism: {
      theme: require('./src/css/draculaTheme'),
      darkTheme: require('./src/css/draculaTheme'),
      additionalLanguages: ['bash', 'docker', 'yaml', 'json', 'typescript', 'python', 'go', 'rust'],
    },
    
    // Table of contents
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  },
  
  // Custom fields for enterprise
  customFields: {
    enterprise: {
      supportEmail: 'support@enterprise.com',
      salesEmail: 'sales@enterprise.com',
      statusPage: 'https://status.enterprise.com',
      changelog: '/changelog',
    },
  },
};
```

### 2. Static Site Generation
The `build_docusaurus.sh` script handles production builds:

```bash
# Build process
npm ci                    # Clean install with lockfile
npm run build             # Generate static site in ./build
```

**Build Optimizations:**
- Code splitting by route
- Asset hashing for cache busting
- Image optimization (WebP, AVIF)
- CSS/JS minification
- Source maps for debugging

### 3. Kubernetes Deployment
The `deploy_docusaurus.sh` script deploys with enterprise patterns:

```yaml
# Deployment with Nginx
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docs-site
spec:
  replicas: 3
  selector:
    matchLabels:
      app: docs-site
  template:
    metadata:
      labels:
        app: docs-site
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "80"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 101
        fsGroup: 101
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        volumeMounts:
        - name: site-content
          mountPath: /usr/share/nginx/html
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: site-content
        configMap:
          name: docs-site-content
      - name: nginx-config
        configMap:
          name: nginx-config
```

### 4. Search Configuration
The `configure_search.sh` script sets up Algolia DocSearch:

```bash
# Configure Algolia DocSearch
./scripts/configure_search.sh \
  --doc-name=learnflow-docs \
  --algolia-app-id=ABC123 \
  --algolia-api-key=secret \
  --algolia-index-name=learnflow-docs
```

**Search Features:**
- **Algolia DocSearch**: Hosted search with typo tolerance
- **Local Search**: Lunr.js fallback for offline/air-gapped
- **Elasticsearch**: Custom search for enterprise
- **Faceted Search**: Filter by version, language, category
- **Analytics**: Search analytics dashboard

### 3. Deployment Verification
The `verify_docusaurus.sh` script validates:

- Deployment readiness and availability
- Pod health and readiness
- Service endpoints and DNS
- Ingress configuration and TLS
- Content serving (HTML, assets, search)
- Search functionality
- Performance metrics

## Enterprise Configuration

### Versioning Strategy

```javascript
// docusaurus.config.js
versions: {
  current: {
    label: 'Latest',
    banner: 'none',
  },
  '2.1': {
    label: 'v2.1',
    banner: 'none',
  },
  '2.0': {
    label: 'v2.0 (LTS)',
    banner: 'This version is no longer actively maintained.',
  },
  '1.0': {
    label: 'v1.0 (Archived)',
    banner: 'This version is archived and no longer receives updates.',
    className: 'version-banner--archived',
  },
}
```

### Internationalization (i18n)

```
docs/
├── en/
│   ├── intro.md
│   ├── tutorial.md
│   └── api/
│       └── reference.md
├── es/
│   ├── intro.md
│   ├── tutorial.md
│   └── api/
│       └── reference.md
└── fr/
    ├── intro.md
    ├── tutorial.md
    └── api/
        └── reference.md
```

**Configuration:**
```javascript
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'es', 'fr', 'de', 'ja', 'zh'],
  localeConfigs: {
    en: { label: 'English', direction: 'ltr', htmlLang: 'en-US' },
    es: { label: 'Español', direction: 'ltr', htmlLang: 'es-ES' },
    fr: { label: 'Français', direction: 'ltr', htmlLang: 'fr-FR' },
    de: { label: 'Deutsch', direction: 'ltr', htmlLang: 'de-DE' },
    ja: { label: '日本語', direction: 'ltr', htmlLang: 'ja-JP' },
    zh: { label: '中文', direction: 'ltr', htmlLang: 'zh-CN' },
  },
}
```

### Custom Theme & Styling

```css
/* src/css/custom.css */
:root {
  --ifm-color-primary: #2563eb;
  --ifm-color-primary-dark: #1d4ed8;
  --ifm-color-primary-darker: #1e40af;
  --ifm-color-primary-lighter: #3b82f6;
  --ifm-color-primary-lightest: #60a5fa;
  
  --ifm-font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --ifm-font-family-monospace: 'JetBrains Mono', 'Fira Code', monospace;
  --ifm-code-font-size: 95%;
  
  --ifm-background-color: #ffffff;
  --ifm-background-surface-color: #f8fafc;
  --ifm-color-content: #1e293b;
  --ifm-color-content-secondary: #475569;
  
  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.1);
}

/* Dark mode */
[data-theme='dark'] {
  --ifm-color-primary: #3b82f6;
  --ifm-color-primary-dark: #2563eb;
  --ifm-color-primary-darker: #1d4ed8;
  --ifm-color-primary-lighter: #60a5fa;
  --ifm-color-primary-lightest: #93c5fd;
  
  --ifm-background-color: #0f172a;
  --ifm-background-surface-color: #1e293b;
  --ifm-color-content: #f1f5f9;
  --ifm-color-content-secondary: #94a3b8;
}

/* Custom components */
.hero__title { font-size: 3.5rem; font-weight: 800; }
.navbar__title { font-weight: 700; font-size: 1.25rem; }
.menu__link { font-weight: 500; border-radius: 0.375rem; }
.menu__link--active { background-color: var(--ifm-color-primary-lighter); color: var(--ifm-color-primary); font-weight: 600; }
.card { border: 1px solid #e2e8f0; border-radius: 0.75rem; }
.card:hover { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
```

### Nginx Configuration

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.your-enterprise.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https:; font-src 'self' data: https://fonts.gstatic.com; connect-src 'self' https://api.your-enterprise.com wss://ws.your-enterprise.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /_next/static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /_next/image {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle SPA routing - fallback to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## Deployment Patterns

### Blue-Green Deployment
```bash
# Deploy new version to green namespace
./scripts/deploy_docusaurus.sh learnflow-docs --namespace documentation-green

# Switch traffic
kubectl patch service docs-site -n documentation \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback if needed
kubectl patch service docs-site -n documentation \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Canary Deployment (with Flagger)
```yaml
# Flagger Canary CRD
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: docs-site
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: docs-site
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    metrics:
    - name: request-success-rate
      threshold: 99
      interval: 1m
    - name: request-duration-p99
      threshold: 500
      interval: 1m
```

### Rolling Update Strategy
```yaml
# Deployment with rolling update
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0
```

## Search Configuration

### Algolia DocSearch (Recommended)
```bash
# Configure Algolia DocSearch
./scripts/configure_search.sh \
  --doc-name=learnflow-docs \
  --algolia-app-id=ABC123 \
  --algolia-api-key=secret \
  --algolia-index-name=learnflow-docs
```

**Configuration in docusaurus.config.js:**
```javascript
algolia: {
  appId: process.env.ALGOLIA_APP_ID,
  apiKey: process.env.ALGOLIA_SEARCH_API_KEY,
  indexName: process.env.ALGOLIA_INDEX_NAME,
  contextualSearch: true,
  searchParameters: {
    facetFilters: ['version:current'],
  },
},
```

### Local Search (Fallback)
```javascript
// For air-gapped environments
plugins: [
  [
    '@docusaurus/plugin-content-docs',
    {
      // ... other config
    },
  ],
  [
    require.resolve('@cmfcmf/docusaurus-search-local'),
    {
      indexBlog: true,
      indexPages: true,
      language: 'en',
      // ... other options
    },
  ],
]
```

### Elasticsearch Integration
```javascript
// Custom search component with Elasticsearch
// Requires custom search component and Elasticsearch backend
```

## Security Hardening

### Content Security Policy
```javascript
// next.config.js equivalent for Docusaurus
async headers() {
  return [
    {
      source: '/:path*',
      headers: [
        {
          key: 'Content-Security-Policy',
          value: [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.your-enterprise.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src 'self' data: https:",
            "font-src 'self' data: https://fonts.gstatic.com",
            "connect-src 'self' https://api.your-enterprise.com wss://ws.your-enterprise.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
          ].join('; '),
        },
      ],
    },
  ];
}
```

### Security Headers (Nginx)
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.your-enterprise.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https:; font-src 'self' data: https://fonts.gstatic.com; connect-src 'self' https://api.your-enterprise.com wss://ws.your-enterprise.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
```

### Security Scanning
```bash
# Container scanning
trivy image your-registry.io/docs-site:latest

# Dependency scanning
npm audit --audit-level=high
snyk test

# SAST
sonar-scanner \
  -Dsonar.projectKey=docs-site \
  -Dsonar.sources=. \
  -Dsonar.exclusions=**/node_modules/**,**/.next/**
```

## Monitoring & Observability

### Prometheus Metrics
```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: docs-site
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: docs-site
  endpoints:
  - port: http
    path: /api/metrics
    interval: 30s
```

### Key Metrics to Monitor
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Build info
docusaurus_build_info{version="1.0.0"}
```

### Distributed Tracing
```javascript
// OpenTelemetry instrumentation
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';

const provider = new NodeTracerProvider();
provider.register();

registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
  ],
});
```

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| Build fails | Out of memory | Increase build memory: `NODE_OPTIONS="--max-old-space-size=4096"` |
| Image too large | Unused dependencies | Use `.dockerignore`, analyze with `dive` |
| Slow cold starts | Large bundle | Enable `output: 'standalone'`, code splitting |
| SSR failures | Missing env vars | Verify all `NEXT_PUBLIC_*` vars in all environments |
| Hydration errors | Client/server mismatch | Use `useEffect` for client-only code |
| Image optimization fails | Missing sharp | Install `sharp` in Dockerfile |
| Memory OOM | Memory limit too low | Increase container memory limit |

### Debug Commands
```bash
# Check pod logs
kubectl logs -l app=docs-site -c docs-site --tail=100

# Exec into pod
kubectl exec -it deployment/docs-site -- sh

# Check Docusaurus build output
kubectl exec -it deployment/docs-site -- ls -la /usr/share/nginx/html/

# Test locally
docker run -p 8080:80 your-registry.io/docs-site:latest

# Analyze bundle
npm run build && npx @docusaurus/bundle-analyzer
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial enterprise release |
| 1.1.0 | 2024-01-20 | Added i18n and image optimization |
| 1.2.0 | 2024-01-25 | Added security hardening |
| 2.0.0 | 2024-07-09 | Enterprise rewrite for Hackathon III |

## Related Documentation

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Docusaurus Deployment](https://docusaurus.io/docs/deployment)
- [Algolia DocSearch](https://docsearch.algolia.com/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager](https://cert-manager.io/docs/)
- [Flagger Progressive Delivery](https://flagger.app/)