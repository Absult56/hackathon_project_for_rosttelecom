/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'rtk-purple': '#7028d8',
        'rtk-indigo': '#29145d',
        'rtk-orange': '#f05a38',
      },
    },
  },
  plugins: [],
}