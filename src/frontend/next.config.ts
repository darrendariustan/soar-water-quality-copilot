import type { NextConfig } from "next";

// Proxy /api/* to the backend server-side. This keeps the browser on HTTPS
// (Vercel) while forwarding to an HTTP backend, avoiding mixed-content blocks.
// Local dev (docker-compose) defaults to the local backend; set BACKEND_URL
// on Vercel to point at the deployed backend.
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
