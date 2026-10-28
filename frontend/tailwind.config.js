/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f5fa',
          100: '#e1ecf5',
          200: '#c2d9ec',
          300: '#94bfe0',
          400: '#5fa0d0',
          500: '#3883bf',
          600: '#2768a3',
          700: '#205384',
          800: '#1d466e',
          900: '#0f2742', // Deep navy primary
          950: '#0a1a2e',
        },
        slate: {
          850: '#172033',
        }
      }
    },
  },
  plugins: [],
}
