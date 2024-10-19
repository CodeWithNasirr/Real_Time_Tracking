/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',  // Include all templates (recursive)
    './static/**/*.js',       // Include any JavaScript files if necessary
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
