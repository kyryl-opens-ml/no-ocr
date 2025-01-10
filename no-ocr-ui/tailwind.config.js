/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#FFD700', // Yellow
        secondary: '#000000', // Black
        background: '#FFFFFF', // White
      },
      fontFamily: {
        heading: ['"Roboto Mono"', 'monospace'],
        body: ['"Open Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
