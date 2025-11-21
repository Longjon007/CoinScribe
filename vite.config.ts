import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Enable code splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'chart-vendor': ['recharts'],
        },
      },
    },
    // Warn about chunk sizes
    chunkSizeWarningLimit: 600,
    // Enable minification with esbuild (faster than terser)
    minify: 'esbuild',
    target: 'es2015',
  },
})
