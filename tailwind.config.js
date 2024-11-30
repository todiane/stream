/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './templates/**/*.html',
        './templates/**/*.html',
        './static/**/*.js',
    ],
    theme: {
        extend: {
            fontFamily: {
                'sans': ['Poppins', 'system-ui', 'sans-serif'],
                'poppins': ['Poppins', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [
        require('@tailwindcss/aspect-ratio'),
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
    ],
}