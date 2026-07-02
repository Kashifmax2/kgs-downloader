/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        dark: {
          100: '#1e293b',
          200: '#1a2234',
          300: '#151c2c',
          400: '#111827',
          500: '#0f172a',
          600: '#0c1222',
          700: '#080d19',
          800: '#050911',
          900: '#020408',
        },
        accent: {
          DEFAULT: '#6366f1',
          light: '#818cf8',
          dark: '#4f46e5',
        },
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #1e293b 100%)',
        'gradient-card': 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
        'gradient-button': 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
        'gradient-button-hover': 'linear-gradient(135deg, #38bdf8 0%, #818cf8 100%)',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(14, 165, 233, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(14, 165, 233, 0.6)' },
        },
      },
    },
  },
  plugins: [],
};
