/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './templates/**/*.html',
        './profiles/templates/**/*.html',
        './courses/templates/**/*.html',
        './static/**/*.js',
    ],

    theme: {
        extend: {
            safelist: [
                {
                    pattern: /(bg|text|border)-(red|blue|green)-(50|100|200|300|400|500|600|700|800|900)/,
                },
            ],
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