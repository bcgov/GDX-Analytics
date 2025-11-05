import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8080, // optional; defaults to 5173 if omitted
  },
  build: {
    sourcemap: false, // disables source maps in production
  },
});
