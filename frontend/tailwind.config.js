/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#09090b', // Deep black
        surface: 'rgba(24, 24, 27, 0.7)', // Zinc 900 with opacity for glass
        primary: '#6366f1', // Indigo 500
        primaryHover: '#4f46e5', // Indigo 600
        textMain: '#fafafa',
        textMuted: '#a1a1aa',
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
      }
    },
  },
  plugins: [],
}
