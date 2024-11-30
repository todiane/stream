/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        '../templates/**/*.html',
        '../**/templates/**/*.html',
        './static/css/**/*.css',
    ],
    theme: {
        extend: {
            fontFamily: {
                'sans': ['Poppins', 'system-ui', 'sans-serif'],
                'poppins': ['Poppins', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
