/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./src/**/*.{html,js}",
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "home": "url('./static/img/bg-home.jpg')",
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["ui-serif", "Georgia", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
        inter: ["Inter", "sans-serif"],
        opensans: ["Open Sans", "sans-serif"],
        courier: ["Courier Prime", "monospace"]
      },
      dropShadow: {
        custom: "50px 50px 100px white",
        red: "50px 50px 100px #862019",
        blue: "50px 50px 50px #062A5A",
        other: "10px 10px 50px white",
      },
    },
  },
  plugins: [require("flowbite/plugin")],
};
