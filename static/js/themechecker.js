// Default starts with dark mode.
document.documentElement.classList.add('dark');
// Changes theme based on user's device preference when page is loaded.
if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
} else {
    document.documentElement.classList.remove('dark')
}