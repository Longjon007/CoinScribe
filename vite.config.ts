import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
  },
  build: {
    outDir: 'dist',
    // Only generate sourcemaps in development or when explicitly requested
    sourcemap: mode === 'development',
    // Enable code splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'chart-vendor': ['recharts'],
        },
        // Consistent file naming for better caching
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      },
    },
    // Warn about chunk sizes
    chunkSizeWarningLimit: 600,
    // Enable minification with esbuild (faster than terser)
    minify: 'esbuild',
    target: 'es2015',
    // Enable CSS code splitting for better caching
    cssCodeSplit: true,
    // Optimize dependency handling
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },
  // Enable dependency pre-bundling optimization
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
}))
