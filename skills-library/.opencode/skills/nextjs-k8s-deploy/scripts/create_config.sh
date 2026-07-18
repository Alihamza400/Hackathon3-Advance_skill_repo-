#!/bin/bash
# Create Next.js application configuration and boilerplate

APP_NAME="$1"

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app-name>"
    echo "Example: $0 learnflow-frontend"
    exit 1
fi

APP_DIR="./apps/$APP_NAME"

# Create application directory
mkdir -p "$APP_DIR"

echo "Scaffolding Next.js application '$APP_NAME' in $APP_DIR..."

# Initialize a basic Next.js project (without installing node_modules here to save tokens/time)
# This assumes `npx create-next-app` is available in the environment where this script runs.
# For a true enterprise setup, this might be a custom template.

# Create a dummy package.json and basic Next.js structure
cat > "$APP_DIR/package.json" << EOF
{
  "name": "$APP_NAME",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "latest",
    "react": "latest",
    "react-dom": "latest"
  },
  "devDependencies": {
    "eslint": "latest",
    "eslint-config-next": "latest"
  }
}
EOF

mkdir -p "$APP_DIR/pages"
cat > "$APP_DIR/pages/index.js" << EOF
import Head from 'next/head'

export default function Home() {
  return (
    <div className="container">
      <Head>
        <title>{process.env.NEXT_PUBLIC_APP_NAME || 'Next.js App'}</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1 className="title">
          Welcome to <a href="https://nextjs.org">{process.env.NEXT_PUBLIC_APP_NAME || 'Next.js'}!</a>
        </h1>

        <p className="description">
          Get started by editing <code>pages/index.js</code>
        </p>
      </main>

      <footer>
        <a
          href="https://vercel.com?utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          Powered by Opencode + Next.js
        </a>
      </footer>
    </div>
  )
}
EOF

# Create a simple next.config.js for potential future customizations
cat > "$APP_DIR/next.config.js" << EOF
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Add any enterprise-specific configurations here
  env: {
    NEXT_PUBLIC_APP_NAME: "$APP_NAME"
  }
};

module.exports = nextConfig;
EOF

# Create enterprise Dockerfile for Next.js
cat > "$APP_DIR/Dockerfile" << EOF
# Base image: Node.js for Next.js build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./ 
COPY yarn.lock ./ # Use yarn if available
RUN yarn install --frozen-lockfile

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN yarn build

# Production image: Serve the built application
FROM node:18-alpine as runner

WORKDIR /app

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# Expose the port Next.js runs on (default 3000)
EXPOSE 3000

# Start the Next.js production server
CMD ["yarn", "start"]
EOF

# Only this output enters agent context:
echo "✓ Next.js application '$APP_NAME' boilerplate created with Dockerfile and initial config."
