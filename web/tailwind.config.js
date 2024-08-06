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
        'light-text-panel': 'var(--color-light-text-panel)',
        'bg-light': 'var(--color-bg-light)',
        'bg-light-tone': 'var(--color-bg-light-tone)',
        'bg-light-panel': 'var(--color-bg-light-panel)',
        'bg-light-code-block': 'var(--color-bg-light-code-block)',
        'bg-light-tone-panel': 'var(--color-bg-light-tone-panel)',
        'bg-light-discussion': 'var(--color-bg-light-discussion)',
        'bg-light-discussion-odd': 'var(--color-bg-light-discussion-odd)',
        'dark-text-panel': 'var(--color-dark-text-panel)',
        'bg-dark': 'var(--color-bg-dark)',
        'bg-dark-tone': 'var(--color-bg-dark-tone)',
        'bg-dark-tone-panel': 'var(--color-bg-dark-tone-panel)',
        'bg-dark-code-block': 'var(--color-bg-dark-code-block)',
        'bg-dark-discussion': 'var(--color-bg-dark-discussion)',
        'bg-dark-discussion-odd': 'var(--color-bg-dark-discussion-odd)'
      },
      fontFamily: {
        sans: ['PTSans', 'Roboto', 'sans-serif']
      },
      container: {
        padding: '2rem',
        center: true
      },
      backgroundImage: {
        'gradient-light': 'linear-gradient(to bottom right, var(--tw-gradient-stops))',
        'gradient-dark': 'linear-gradient(to bottom right, var(--tw-gradient-stops))',
      },
      gradientColorStops: {
        'light-start': '#e0eaff',
        'light-end': '#f0e6ff',
        'dark-start': '#0f2647',
        'dark-end': '#1e1b4b',
      },
    }
  },
  plugins: [
    require('flowbite/plugin'),
    require('tailwind-scrollbar'),
    function({ addBase, theme }) {
      addBase({
        'body': {
          '@apply bg-gradient-light from-light-start to-light-end dark:bg-gradient-dark dark:from-dark-start dark:to-dark-end min-h-screen': {}
        },
      })
    }
  ],
  variants: {
    h1: {
      fontWeight: 'bold'
    }
  }
}
