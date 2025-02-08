const withMT = require("@material-tailwind/react/utils/withMT");

module.exports = withMT({
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        customLightBlue: '#00aeef',
        customBlue: '#0072b6',
        customGray: '#666666',
        custom75Gray: '#8e8f9b',
        custom50Gray: '#b2b1bb',
        custom10Gray: '#efeff1',
        customGreen: '#00b08b',
        customBrickRed: '#dc533a',
        customAmber: '#db236d',
      },
      fontFamily: {
        'domine': ['Domine', 'serif'], 
        'lato': ['Lato', 'sans-serif'],
        'dyodrum': ['Diodrum-Regular', 'sans-serif'],
      },
    },
  },
  plugins: [],
});
