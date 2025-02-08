import { Typography } from "@material-tailwind/react";
import logo from '/img/logo_blanco_transparente.svg';
import { Logo } from "./Logo";
const Footer = () => {
  return (
    <footer className="footer w-full h-8">
      <div className="flex flex-row flex-wrap items-center justify-center gap-y-6 gap-x-12 text-white text-center md:justify-between">
        {/* <img
            alt="Logo Ayming"
            className="w-[100px] object-cover object-center"
            src={logo}
        />
        <ul className="flex flex-wrap text-white items-center gap-y-2 gap-x-8">
          <li>
            <Typography
              as="a"
              href="#"
              color="blue-gray"
              className="font-normal transition-colors text-white hover:text-blue-500 focus:text-blue-500"
            >
              About Us
            </Typography>
          </li>
          <li>
            <Typography
              as="a"
              href="#"
              color="blue-gray"
              className="font-normal transition-colors text-white hover:text-blue-500 focus:text-blue-500"
            >
              License
            </Typography>
          </li>
          <li>
            <Typography
              as="a"
              href="#"
              color="blue-gray"
              className="font-normal transition-colors text-white hover:text-blue-500 focus:text-blue-500"
            >
              Contribute
            </Typography>
          </li>
          <li>
            <Typography
              as="a"
              href="#"
              color="blue-gray"
              className="font-normal transition-colors text-white hover:text-blue-500 focus:text-blue-500"
            >
              Contact Us
            </Typography>
          </li>
        </ul> */}
      </div>
      {/* <Typography color="white" className="text-center font-normal">
          <Logo />
      </Typography> */}
    </footer>
  );
}

export default Footer;