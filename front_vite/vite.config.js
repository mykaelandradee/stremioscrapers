import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/manifest.json": "http://localhost:7000",
      "/configure": "http://localhost:7000",
      "/api": "http://localhost:7000",
      "/stream": "http://localhost:7000",
      "/demo": "http://localhost:7000",
    },
  },
  build: {
    outDir: "../static",
    emptyOutDir: true,
  },
});