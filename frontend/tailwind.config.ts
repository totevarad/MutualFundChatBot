import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#101415",
        surface: "#101415",
        primary: "#4edea3",
        secondary: "#bec6e0",
        tertiary: "#b9c7e0",
        "surface-container-low": "#191c1e",
        "surface-container-high": "#272a2c",
        "surface-container-highest": "#323537",
        outline: "#86948a",
        "outline-variant": "#3c4a42",
      },
      fontFamily: {
        sans: ["var(--font-hanken-grotesk)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      keyframes: {
        "typing-dot": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
        marquee: {
          "0%": { transform: "translateX(0%)" },
          "100%": { transform: "translateX(-100%)" },
        },
      },
      animation: {
        "typing-dot": "typing-dot 1s infinite ease-in-out",
        marquee: "marquee 20s linear infinite",
      },
    },
  },
  plugins: [],
};
export default config;
