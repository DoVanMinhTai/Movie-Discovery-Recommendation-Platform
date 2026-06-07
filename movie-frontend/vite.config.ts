import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file from parent directory (project root)
  loadEnv(mode, path.resolve(__dirname, '..'), '');
   
  return {
    plugins: [react(), tailwindcss()],
    envDir: path.resolve(__dirname, '..'), // Look for .env files in parent directory
  }
})
