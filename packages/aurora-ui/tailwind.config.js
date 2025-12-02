/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        aurora: {
          dark: '#0a0a0f',
          darker: '#050508',
          purple: '#8b5cf6',
          'purple-dark': '#6d28d9',
          'purple-light': '#a78bfa',
          sky: '#0ea5e9',
          'sky-dark': '#0284c7',
          neon: '#00f5ff',
        },
      },
      animation: {
        'pulse-neon': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(139, 92, 246, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(139, 92, 246, 0.8), 0 0 30px rgba(139, 92, 246, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}

