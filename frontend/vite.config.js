import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Permite acceder desde cualquier máquina en la red
    port: 5173,       // Puerto estándar de Vite
    strictPort: true, // Asegura que siempre usa el puerto 5173
    watch: {
      usePolling: true, // Necesario en Docker para recargar archivos
    }
  },
  preview: {
    port: 4173,       // Define un puerto diferente para preview en producción
    strictPort: true,
  }
});
