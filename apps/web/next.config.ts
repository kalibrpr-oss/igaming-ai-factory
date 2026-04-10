import type { NextConfig } from "next";

/**
 * Статический экспорт (out/) только на `next build`.
 * Если включить output: "export" и для `next dev`, при заходе с LAN/Docker IP (172.x)
 * часто отдаётся «голый» HTML без CSS — чанки и стили расходятся с хостом в адресе.
 */
const isStaticExportBuild = process.argv.includes("build");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  /** В CI нет интерактивного eslint init; типы и сборку проверяет next build. */
  eslint: {
    ignoreDuringBuilds: true,
  },
  ...(isStaticExportBuild
    ? {
        output: "export" as const,
        /** /guide/index.html — чтобы Apache открывал вложенные URL без 404 */
        trailingSlash: true,
      }
    : {}),
  images: {
    unoptimized: isStaticExportBuild,
  },
};

export default nextConfig;
