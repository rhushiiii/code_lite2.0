/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Space Grotesk", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(168,85,247,0.35), 0 20px 40px rgba(88,28,135,0.25)",
      },
      colors: {
        surface: {
          900: "#0B1020",
          800: "#12192e",
          700: "#1b2440",
        },
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in-up": "fadeInUp 0.45s ease-out forwards",
      },
    },
  },
  plugins: [],
};
