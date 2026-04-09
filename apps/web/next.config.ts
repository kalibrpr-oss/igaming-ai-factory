import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  /** Сборка в статику для заливки на shared-хостинг (папка out/) */
  output: "export",
  /** /guide/index.html — чтобы Apache открывал вложенные URL без 404 */
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
