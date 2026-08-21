/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        theme: {
          bg: 'var(--bg)',
          surface: 'var(--surface)',
          elevated: 'var(--surface-elevated)',
          border: 'var(--border)',
          accent: 'var(--accent)',
          positive: 'var(--positive)',
          neutral: 'var(--neutral)',
          negative: 'var(--negative)',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
