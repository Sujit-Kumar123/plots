import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL ?? 'http://localhost:8000'

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["motion"],
  // Silence the "webpack config but no turbopack config" error in Next.js 16
  turbopack: {},
  // In local dev (no Docker), proxy /api/* to the FastAPI backend so that
  // the relative-URL default in api.ts works without NEXT_PUBLIC_API_URL.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ]
  },
};

export default nextConfig;
