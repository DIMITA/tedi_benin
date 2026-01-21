import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production'
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      // Target modern browsers for smaller bundle
      target: 'es2020',
      // Use esbuild for faster builds (terser for smaller size if needed)
      minify: 'esbuild',
      // Code splitting for better caching
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Split vendor chunks for better caching
            if (id.includes('node_modules')) {
              if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
                return 'vendor-vue'
              }
              if (id.includes('leaflet')) {
                return 'vendor-leaflet'
              }
              if (id.includes('chart.js')) {
                return 'vendor-chart'
              }
              if (id.includes('axios')) {
                return 'vendor-axios'
              }
              // All other vendor libs
              return 'vendor'
            }
          },
        },
      },
      // No source maps in production
      sourcemap: false,
      // Chunk size warnings
      chunkSizeWarningLimit: 300,
      // CSS code splitting
      cssCodeSplit: true,
      // Asset inlining threshold (smaller assets inline as base64)
      assetsInlineLimit: 4096,
    },
    // Optimize deps for faster cold start
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'axios'],
    },
    server: {
      port: 3000,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: process.env.VITE_API_URL || 'http://backend:5000',
          changeOrigin: true,
        }
      }
    },
    // Production-specific optimizations
    esbuild: isProduction ? {
      drop: ['console', 'debugger'],
      legalComments: 'none',
    } : {},
  }
})
