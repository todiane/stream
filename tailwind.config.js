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
            transitionTimingFunction: {
                'custom-ease': 'cubic-bezier(0.4, 0, 0.2, 1)',
            },
            transitionDuration: {
                '500': '500ms',
            },
            safelist: [
                {
                    pattern: /(bg|text|border)-(red|blue|green|gray)-(50|100|200|300|400|500|600|700|800|900)/,
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
    variants: {
        extend: {
            scale: ['hover'],
        },
    },
}