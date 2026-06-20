/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Dark theme surfaces
        canvas:  '#0D0F12',   // page background — deep near-black
        surface: '#151920',   // card/panel background
        raised:  '#1C2333',   // elevated elements, inputs
        border:  '#2A3348',   // borders and dividers

        // Text
        primary:   '#E8EAF0', // main text — cool off-white
        secondary: '#8B95A8', // subtext — readable mid-grey
        muted:     '#4A5568', // placeholder, labels

        // Signal colors — same intent, adjusted for dark bg
        verified:  '#34D399', // authentic — vivid teal-green
        flag:      '#F87171', // suspicious — warm red
        uncertain: '#FBBF24', // inconclusive — amber

        // Accent
        accent: '#6366F1',    // indigo — used sparingly for CTAs
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body:    ['"Inter"', 'sans-serif'],
        mono:    ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
