const withMT = require("@material-tailwind/react/utils/withMT");

module.exports = withMT({
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        custom50LightBlue: '#84d0f5',
        custom75LightBlue: '#44c8f5',
        customLightBlue: '#00aeef',
        custom50Blue: '#84b2dc',
        custom75Blue: '#278fc9',
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
