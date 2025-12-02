/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@aurora/ui', '@aurora/hooks'],
  // Disable ESLint during build for now
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Allow importing from packages
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
    }
    return config
  },
}

module.exports = nextConfig

