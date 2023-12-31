/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    'node_modules/flowbite-vue/**/*.{js,jsx,ts,tsx}'
  ],

  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#0e8ef0',
        'primary-light': '#3dabff',
        secondary: '#0fd974',
        accent: '#f0700e',
        'bg-dark': '#132e59',
        'bg-dark-tone': '#25477d',
        'bg-dark-tone-panel': '#4367a3',
        'bg-dark-code-block': '#2254a7',
        'bg-light': '#e2edff',
        'bg-light-tone': '#b9d2f7',
        'bg-light-code-block': '#cad7ed',
        'bg-light-tone-panel': '#8fb5ef',
        'bg-dark-discussion': '#435E8A',
        'bg-dark-discussion-odd': '#284471',
        'bg-light-discussion': '#c5d8f8',
        'bg-light-discussion-odd': '#d6e7ff'
      },
      fontFamily: {
        sans: ['PTSans', 'Roboto', 'sans-serif']
      },
      container: {
        padding: '2rem',
        center: true
      }
    }
  },
  plugins: [require('flowbite/plugin'), require('tailwind-scrollbar')],
  variants: {
    h1: {
      fontWeight: 'bold'
    }
  }
}
