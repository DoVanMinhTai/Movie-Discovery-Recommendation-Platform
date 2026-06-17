import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig(({ mode }) => {
  loadEnv(mode, path.resolve(__dirname, '..'), '');
  const envDir = path.resolve(__dirname, '..');
  const env = loadEnv(mode, envDir);

  return {
    plugins: [react(), tailwindcss()],
    envDir: envDir,
    define: {
     'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL),
    },
    server: {
      host: '[0.0.0.0]',
      port: 5173,
    },
  }
})
