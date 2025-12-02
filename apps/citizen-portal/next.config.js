const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin('./i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@aurora/ui', '@aurora/hooks'],
  experimental: {
    serverActions: true,
  },
  // Allow importing from packages
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
    }
    return config
  },
}

module.exports = withNextIntl(nextConfig)

