/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    images: {
      unoptimized: true,
    },
    // Disable server components for Electron compatibility
    experimental: {
      appDir: true,
    },
  }
  
  export default nextConfig
  
  