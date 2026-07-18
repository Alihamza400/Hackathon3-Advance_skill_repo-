/** @type {import('next').NextConfig} */
const UPSTREAM = process.env.UPSTREAM_API_URL || 'http://localhost:8000';

const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  transpilePackages: ['@monaco-editor/react'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${UPSTREAM}/:path*`,
      },
    ];
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    return config;
  },
};

module.exports = nextConfig;