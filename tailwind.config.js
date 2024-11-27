/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html",
    "./templates/**/*.{html,js}",
    "./courses/templates/**/*.html",
    "./profiles/templates/**/*.html",
    "./staticfiles/css/**/*.css",
    "./staticfiles/js/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

