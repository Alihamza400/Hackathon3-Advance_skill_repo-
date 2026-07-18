# Next.js Kubernetes Deployment Skill - Enterprise Reference

## Overview
The `nextjs-k8s-deploy` skill provides enterprise-grade deployment of Next.js applications on Kubernetes with production-ready configurations including SSR/SSG support, image optimization, internationalization, and enterprise security.

## Skill Architecture

### File Structure
```
nextjs-k8s-deploy/
├── SKILL.md                 # Agent instructions (~100 tokens)
├── REFERENCE.md             # This document (loaded on-demand)
└── scripts/
    ├── create_config.sh    # Scaffold Next.js project with enterprise config
    ├── build_image.sh      # Multi-stage Docker build with caching
    ├── create_helm.sh      # Production Helm chart generation
    ├── deploy_helm.sh      # Helm deployment with strategies
    ├── setup_ingress.sh    # Ingress with TLS/WAF
    └── verify_helm.sh      # Comprehensive deployment verification
```

## Enterprise Features

### 1. Next.js Application Scaffolding
The `create_config.sh` script generates:

- **Next.js 14+ App Router**: Modern React Server Components
- **TypeScript Configuration**: Strict mode, path aliases, strict null checks
- **Dockerfile**: Multi-stage build (builder → runner) with caching
- **next.config.js**: Enterprise configuration (i18n, images, security headers)
- **Environment Configuration**: Multi-environment config with validation
- **Testing Setup**: Jest + React Testing Library + Playwright

### 2. Multi-Stage Docker Build
The `build_image.sh` script implements:

```dockerfile
# Stage 1: Builder (dependencies + build)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY . .
RUN npm run build

# Stage 2: Runner (minimal production image)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Optimizations**:
- Layer caching for dependencies
- Standalone output for minimal runtime
- Non-root user execution
- Minimal base image (Alpine)
- Proper .dockerignore

### 3. Production Helm Chart
The `create_helm.sh` generates enterprise Helm chart:

```
helm-charts/{app-name}/
├── Chart.yaml
├── values.yaml                 # Enterprise defaults
├── values-production.yaml      # Production overrides
├── values-staging.yaml         # Staging overrides
├── templates/
│   ├── deployment.yaml         # Deployment with HPA
│   ├── service.yaml            # ClusterIP service
│   ├── ingress.yaml            # Ingress with TLS/WAF
│   ├── hpa.yaml                # Horizontal Pod Autoscaler
│   ├── servicemonitor.yaml     # Prometheus monitoring
│   ├── configmap.yaml          # Runtime configuration
│   ├── secret.yaml             # Secrets management
│   ├── servicemonitor.yaml     # Prometheus metrics
│   ├── pdb.yaml                # Pod Disruption Budget
│   ├── networkpolicy.yaml      # Network policies
│   └── _helpers.tpl            # Template helpers
└── .helmignore
```

### 4. Enterprise Deployment Features

#### Blue-Green Deployment
```bash
# Deploy to green namespace
./scripts/deploy_helm.sh my-app --namespace production-green

# Switch traffic
kubectl patch service my-app -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'
```

#### Canary Deployment (with Flagger)
```yaml
# Flagger Canary CRD
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: my-app
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  service:
    port: 3000
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

#### Rollback Strategy
```bash
# Automated rollback on failure
helm rollback my-app --namespace production

# Or with Flagger - automatic rollback on metric threshold breach
```

### 5. Enterprise Ingress Configuration
The `setup_ingress.sh` script configures:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app-name}
  annotations:
    # NGINX Ingress Controller
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1s"
    nginx.ingress.kubernetes.io/limit-connections: "10"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    
    # Security
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Frame-Options "SAMEORIGIN" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header X-XSS-Protection "1; mode=block" always;
      add_header Referrer-Policy "strict-origin-when-cross-origin" always;
      add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';" always;
    
    # TLS
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2 TLSv1.3"
    
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - {app-name}.your-enterprise.com
    secretName: {app-name}-tls
  rules:
  - host: {app-name}.your-enterprise.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {app-name}
            port:
              number: 3000
```

## Next.js Enterprise Configuration

### next.config.js (Enterprise)
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output standalone for Docker
  output: 'standalone',
  
  // Internationalization
  i18n: {
    locales: ['en', 'es', 'fr', 'de', 'ja'],
    defaultLocale: 'en',
    localeDetection: false,
  },
  
  // Image optimization
  images: {
    domains: ['cdn.your-enterprise.com', 'images.unsplash.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 31536000, // 1 year
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
        ],
      },
  ],
  
  // Webpack optimizations
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
          lib: {
            test: /[\\/]node_modules[\\/]/,
            name: 'lib',
            chunks: 'all',
          },
        },
      };
    }
    return config;
  },
  
  // Experimental features
  experimental: {
    serverComponentsExternalPackages: ['@prisma/client'],
    optimizePackageImports: ['lucide-react', 'date-fns'],
  },
  
  // Compiler options
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
    reactRemoveProperties: process.env.NODE_ENV === 'production' ? { properties: ['^data-testid$'] } : false,
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_APP_VERSION: process.env.npm_package_version,
    NEXT_PUBLIC_BUILD_TIME: new Date().toISOString(),
  },
};

module.exports = nextConfig;
```

### Environment Configuration
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.your-enterprise.com
NEXT_PUBLIC_WS_URL=wss://ws.your-enterprise.com
NEXT_PUBLIC_ANALYTICS_ID=GA_MEASUREMENT_ID
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx

# Build-time
NEXT_TELEMETRY_DISABLED=1
NEXT_PRIVATE_STANDALONE=true
```

## Helm Values (Enterprise)

### values.yaml (Base)
```yaml
replicaCount: 3

image:
  repository: your-registry.io/nextjs-app
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets:
  - name: registry-credentials

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/nextjs-app-role
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "3000"
  prometheus.io/path: "/api/metrics"

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000

service:
  type: ClusterIP
  port: 3000
  targetPort: 3000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
  hosts:
    - host: app.your-enterprise.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: nextjs-app-tls
      hosts:
        - app.your-enterprise.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max

nodeSelector:
  node-type: application

tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "application"
    effect: "NoSchedule"

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - nextjs-app
        topologyKey: kubernetes.io/hostname

podDisruptionBudget:
  enabled: true
  minAvailable: 50%

networkPolicy:
  enabled: true
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: ingress-nginx
      ports:
      - protocol: TCP
        port: 3000
```

### values-production.yaml
```yaml
replicaCount: 5

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  minReplicas: 5
  maxReplicas: 50

ingress:
  hosts:
    - host: app.your-enterprise.com
      paths:
        - path: /
          pathType: Prefix

# Enable additional security
podSecurityContext:
  seccompProfile:
    type: RuntimeDefault

# Enable Prometheus ServiceMonitor
serviceMonitor:
  enabled: true
  interval: 30s
  scrapeTimeout: 10s

# Enable PodDisruptionBudget
podDisruptionBudget:
  minAvailable: 50%
```

## Verification & Testing

### Deployment Verification
The `verify_helm.sh` script performs:

1. **Helm Release Status**: Checks release status is `deployed`
2. **Deployment Readiness**: Waits for deployment `Available` condition
2. **Pod Health**: Verifies all pods `Ready` and `Running`
3. **Service Endpoints**: Verifies service has matching endpoints
4. **Ingress Configuration**: Validates ingress hosts, TLS, annotations
5. **Health Checks**: Verifies `/health` endpoint returns 200
6. **Metrics Endpoint**: Validates `/api/metrics` for Prometheus
7. **Static Assets**: Verifies static asset serving
7. **SSR/SSG**: Validates server-side rendering works

### Testing Commands
```bash
# Full verification
./scripts/verify_helm.sh my-app --namespace production --verbose

# Quick health check
curl -s https://app.your-enterprise.com/health

# Load test
k6 run --vus 100 --duration 60s load-test.js

# Smoke test
curl -s https://app.your-enterprise.com | grep -q "Welcome" && echo "OK"
```

## Performance Optimization

### Build Optimization
```javascript
// next.config.js - Build optimizations
module.exports = {
  // ... other config
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  experimental: {
    optimizePackageImports: ['lucide-react', 'date-fns', 'lodash'],
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },
};
```

### Runtime Performance
```yaml
# Helm values for performance
resources:
  limits:
    cpu: "1000m"
    memory: "1Gi"
  requests:
    cpu: "250m"
    memory: "256Mi"

autoscaling:
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
    scaleDown:
      stabilizationWindowSeconds: 300
```

### Caching Strategy
```nginx
# Nginx ingress annotations for caching
nginx.ingress.kubernetes.io/configuration-snippet: |
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
```

## Monitoring & Observability

### Prometheus Metrics
```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nextjs-app
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: nextjs-app
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
nextjs_build_info{version="1.0.0"}
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

## Security Hardening

### Content Security Policy
```javascript
// next.config.js
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

### Security Scanning
```bash
# Container scanning
trivy image your-registry.io/nextjs-app:latest

# Dependency scanning
npm audit --audit-level=high
snyk test

# SAST
sonar-scanner \
  -Dsonar.projectKey=nextjs-app \
  -Dsonar.sources=. \
  -Dsonar.exclusions=**/node_modules/**,**/.next/**
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
kubectl logs -l app=nextjs-app -c nextjs-app --tail=100

# Exec into pod
kubectl exec -it deployment/nextjs-app -- sh

# Check Next.js build output
kubectl exec -it deployment/nextjs-app -- ls -la .next/

# Test locally
docker run -p 3000:3000 your-registry.io/nextjs-app:latest

# Analyze bundle
npm run build && npx @next/bundle-analyzer
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial enterprise release |
| 1.1.0 | 2024-01-20 | Added i18n and image optimization |
| 1.2.0 | 2024-01-25 | Added security hardening |
| 2.0.0 | 2024-07-09 | Enterprise rewrite for Hackathon III |

## Related Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [Helm Documentation](https://helm.sh/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager](https://cert-manager.io/docs/)
- [Flagger Progressive Delivery](https://flagger.app/)