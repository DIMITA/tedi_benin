/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'tedi-primary': '#10b981',   // Green - Growth, Agriculture
        'tedi-secondary': '#2563eb',  // Blue - Economy, Data
        'tedi-accent': '#f59e0b',     // Amber - Highlights
      }
    },
  },
  plugins: [],
}
