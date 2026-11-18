export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {
    colors: { sky: { DEFAULT: "#76B9EF", soft: "#B8DDF8" }, butter: "#F5E6A8", cream: "#FFFDF5", meadow: "#A4C98C",
      choc: "#76513F", lav: "#D8C8F3", bubble: "#F5A6B8", cocoa: "#3F352F" },
    fontFamily: { head: ["Plus Jakarta Sans", "sans-serif"], body: ["Inter", "sans-serif"], brand: ["Fredoka", "sans-serif"] },
    keyframes: { drift: { "0%,100%": { transform: "translateX(0)" }, "50%": { transform: "translateX(28px)" } } },
    animation: { drift: "drift 14s ease-in-out infinite" },
  } },
};
