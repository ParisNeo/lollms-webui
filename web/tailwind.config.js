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
        'primary': 'var(--color-primary)',
        'primary-light': 'var(--color-primary-light)',
        'secondary': 'var(--color-secondary)',
        'accent': 'var(--color-accent)',
        'bg-dark': 'var(--color-bg-dark)',
        'bg-dark-tone': 'var(--color-bg-dark-tone)',
        'bg-dark-tone-panel': 'var(--color-bg-dark-tone-panel)',
        'bg-dark-code-block': 'var(--color-bg-dark-code-block)',
        'bg-light': 'var(--color-bg-light)',
        'bg-light-tone': 'var(--color-bg-light-tone)',
        'bg-light-code-block': 'var(--color-bg-light-code-block)',
        'bg-light-tone-panel': 'var(--color-bg-light-tone-panel)',
        'bg-dark-discussion': 'var(--color-bg-dark-discussion)',
        'bg-dark-discussion-odd': 'var(--color-bg-dark-discussion-odd)',
        'bg-light-discussion': 'var(--color-bg-light-discussion)',
        'bg-light-discussion-odd': 'var(--color-bg-light-discussion-odd)'
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
