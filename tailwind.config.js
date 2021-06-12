const defaultTheme = require("tailwindcss/defaultTheme");
module.exports = {
    future: {},
    purge: [],
    theme: {
        extend: {
            fontFamily: {
                sans: ["Inter var", ...defaultTheme.fontFamily.sans],
            },
        },
    },
    variants: {},
    plugins: [
        require("@tailwindcss/ui"),
        require('@tailwindcss/forms'),
    ],
};
