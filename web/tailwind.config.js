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
        sans: [
          'Inter',                // Modern, professional font with excellent readability
          'Outfit',              // Clean and contemporary
          'PTSans',              // Keeping your existing font
          'Roboto',              // Keeping your existing font
          'ui-sans-serif',       // System UI font
          'system-ui',           // System default
          '-apple-system',       // Apple systems
          'BlinkMacSystemFont',  // Chrome on macOS
          'Segoe UI',           // Windows
          'Arial',              // Universal fallback
          'sans-serif'          // Final fallback
        ],
        // You might also want to add specific font configurations for different purposes
        heading: [
          'Montserrat',         // Professional heading font
          'Inter',
          'sans-serif'
        ],
        mono: [
          'JetBrains Mono',     // High-quality monospace font
          'Consolas',
          'monospace'
        ]
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
      keyframes: {
        'bubble-in-up': { // Name of the keyframes
          '0%': {
            opacity: '0',
            transform: 'translateY(10px) translateX(-50%) scale(0.95)', // Match your CSS definition
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0) translateX(-50%) scale(1)', // Match your CSS definition
          },
        },
        'bubble-in-down': { // Keep this if you might use it later
          '0%': {
            opacity: '0',
            transform: 'translate(-50%, 10px) scale(0.95)',
          },
          '100%': {
            opacity: '1',
            transform: 'translate(-50%, 0) scale(1)',
          },
        }
        // Add other custom keyframes here
      },
      animation: {
        // -- Add this section --
        'bubble-in-up': 'bubble-in-up 0.3s ease-out forwards', // Map utility name to keyframes name, duration, timing, fill-mode etc.
                                                              // 'forwards' keeps the end state
        'bubble-in-down': 'bubble-in-down 0.3s ease-out forwards', // Optional: if you need this too
        // Add other custom animations here
      },
    }
  },
  plugins: [
    require('flowbite/plugin'),
    require('tailwind-scrollbar'),
    require('@tailwindcss/typography'),
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
