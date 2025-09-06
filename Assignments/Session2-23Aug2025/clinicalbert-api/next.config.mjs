import path from "path";
/** @type {import('next').NextConfig} */
const nextConfig = {
   webpack: (config) => {
    // ensure @ maps to project root at build time
    config.resolve.alias["@"] = path.resolve(process.cwd());
    return config;
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
}

export default nextConfig
