import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8080 // uses the default 5173 if not set
  },
  build: {
    sourcemap: false // disables source maps for production
  }
})