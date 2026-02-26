import path from 'path'
import { fileURLToPath } from 'url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react({ jsxRuntime: 'classic' })],
  root: path.resolve(__dirname),
  optimizeDeps: {
    disabled: true,
  },
  // Resolve React to ESM CDN so it works without pre-bundling (avoids optimizer crash on Node 24)
  resolve: {
    alias: {
      'react': 'https://esm.sh/react@18.3.1',
      'react-dom': 'https://esm.sh/react-dom@18.3.1',
      'react-dom/client': 'https://esm.sh/react-dom@18.3.1/client',
    },
  },
})
