import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forward all API endpoints to your FastAPI server
      '/analyze': 'http://localhost:8000',
      '/roast': 'http://localhost:8000',
      '/interview-prep': 'http://localhost:8000',
      '/evaluate-answer': 'http://localhost:8000',
      '/match-jd': 'http://localhost:8000'
    }
  }
})