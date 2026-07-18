module.exports = {
  async rewrites() {
    return [
      {
        // Strip the /api prefix — backend gateway routes don't have it
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};