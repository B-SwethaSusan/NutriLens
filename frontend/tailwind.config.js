/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#16302b',
        paper: '#f7faf6',
        sage: { 50: '#f3f8f3', 100: '#e3f0e5', 200: '#c8e1cb', 500: '#4f9d69', 600: '#398257', 700: '#286746' },
        citrus: '#f5b544',
      },
      boxShadow: { soft: '0 12px 45px rgba(25, 74, 52, .08)' },
      fontFamily: { sans: ['DM Sans', 'ui-sans-serif', 'system-ui'] },
    },
  },
  plugins: [],
}
