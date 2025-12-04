/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@aurora/ui', '@aurora/hooks'],
  experimental: {
    serverActions: true,
  },
  // Allow importing from packages and root node_modules
  webpack: (config, { isServer }) => {
    const path = require('path')
    
    // Resolve modules from local node_modules first, then root
    const rootNodeModules = path.resolve(__dirname, '../../node_modules')
    const localNodeModules = path.resolve(__dirname, 'node_modules')
    
    config.resolve.modules = [
      'node_modules',
      localNodeModules,
      rootNodeModules,
      ...(config.resolve.modules || []),
    ]
    
    return config
  },
}

module.exports = nextConfig

