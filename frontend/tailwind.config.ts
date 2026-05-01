import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#10221b",
        canvas: {
          50: "#faf8f4",
          100: "#f7f5f1",
          200: "#f4efe7",
        },
      },
      fontFamily: {
        sans: ['"Avenir Next"', '"Segoe UI"', "sans-serif"],
      },
      boxShadow: {
        panel: "0 22px 48px rgba(16, 34, 27, 0.08)",
        floating: "0 20px 36px rgba(16, 34, 27, 0.14)",
      },
    },
  },
};

export default config;
