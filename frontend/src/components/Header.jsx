import React, { useState, useEffect } from "react";
import {
  Navbar,
  Collapse,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuHandler,
  MenuList,
  MenuItem,
  Avatar,
  Card,
} from "@material-tailwind/react";
import {
  CubeTransparentIcon,
  UserCircleIcon,
  CodeBracketSquareIcon,
  Square3Stack3DIcon,
  ChevronDownIcon,
  Cog6ToothIcon,
  InboxArrowDownIcon,
  LifebuoyIcon,
  PowerIcon,
  RocketLaunchIcon,
  Bars2Icon,
} from "@heroicons/react/24/solid";

import user from "/img/user.svg";
import { Logo } from "./Logo.jsx";

// 📌 Opciones del menú de perfil
const profileMenuItems = [
  { label: "My Profile", icon: UserCircleIcon },
  // { label: "Edit Profile", icon: Cog6ToothIcon },
  // { label: "Inbox", icon: InboxArrowDownIcon },
  // { label: "Help", icon: LifebuoyIcon },
  { label: "Sign Out", icon: PowerIcon },
];

// 📌 Componente del menú de perfil
const ProfileMenu = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <Menu open={isMenuOpen} handler={setIsMenuOpen} placement="bottom-end">
      <MenuHandler>
        <Button
          variant="text"
          className="flex items-center gap-1 rounded-full capitalize  py-0.5 pr-0 pl-4 lg:ml-auto"
        >
          Mª Rosa Cuenca
          <Avatar
            variant="circular"
            size="sm"
            alt="User"
            className="border-[5px]  border-customLightBlue ml-2"
            src={user}
          />
          {/* <ChevronDownIcon
            strokeWidth={2.5}
            className={` h-3 w-3 transition-transform ${
              isMenuOpen ? "rotate-180" : ""
            }`}
          /> */}
        </Button>
      </MenuHandler>
      <MenuList className="p-1">
        {profileMenuItems.map(({ label, icon }, key) => {
          const isLastItem = key === profileMenuItems.length - 1;
          return (
            <MenuItem
              key={label}
              onClick={closeMenu}
              className={`flex items-center gap-2 rounded ${
                isLastItem
                  ? "hover:bg-red-500/10 focus:bg-red-500/10 active:bg-red-500/10"
                  : ""
              }`}
            >
              {React.createElement(icon, {
                className: `h-4 w-4 ${isLastItem ? "text-red-500" : ""}`,
                strokeWidth: 2,
              })}
              <Typography
                as="span"
                variant="small"
                className="font-normal"
                color={isLastItem ? "red" : "inherit"}
              >
                {label}
              </Typography>
            </MenuItem>
          );
        })}
      </MenuList>
    </Menu>
  );
};

// 📌 Opciones del menú de navegación
const navListItems = [
  { label: "Account", icon: UserCircleIcon },
  { label: "Blocks", icon: CubeTransparentIcon },
  { label: "Docs", icon: CodeBracketSquareIcon },
];

// 📌 Componente de la lista de navegación
const NavList = () => (
  <ul className="mt-2 mb-4 flex flex-col gap-2 lg:mb-0 lg:mt-0 lg:flex-row lg:items-center">
    {navListItems.map(({ label, icon }) => (
      <Typography
        key={label}
        as="a"
        href="#"
        variant="small"
        color="gray"
        className="font-medium text-blue-gray-500"
      >
        <MenuItem className="flex items-center gap-2 lg:rounded-full">
          {React.createElement(icon, { className: "h-[18px] w-[18px]" })}{" "}
          <span className="text-gray-900"> {label}</span>
        </MenuItem>
      </Typography>
    ))}
  </ul>
);

export const Header = () => {
  const [openNav, setOpenNav] = React.useState(false);
  const [isNavOpen, setIsNavOpen] = useState(false);

  const toggleIsNavOpen = () => setIsNavOpen((cur) => !cur);

  useEffect(() => {
    window.addEventListener("resize", () => {
      if (window.innerWidth >= 960) setIsNavOpen(false);
    });
  }, []);

  React.useEffect(() => {
    window.addEventListener(
      "resize",
      () => window.innerWidth >= 960 && setOpenNav(false)
    );
  }, []);

  const navList = (
    <ul className="mt-2 mb-4 flex flex-col gap-2 lg:mb-0 lg:mt-0 lg:flex-row lg:items-center lg:gap-6">
      <Typography
        as="li"
        variant="small"
        color="blue-gray"
        className="p-1 font-normal"
      >
        <a href="#" className="flex items-center">
          Pages
        </a>
      </Typography>
      <Typography
        as="li"
        variant="small"
        color="blue-gray"
        className="p-1 font-normal"
      >
        <a href="#" className="flex items-center">
          Account
        </a>
      </Typography>
      <Typography
        as="li"
        variant="small"
        color="blue-gray"
        className="p-1 font-normal"
      >
        <a href="#" className="flex items-center">
          Blocks
        </a>
      </Typography>
      <Typography
        as="li"
        variant="small"
        color="blue-gray"
        className="p-1 font-normal"
      >
        <a href="#" className="flex items-center">
          Docs
        </a>
      </Typography>
    </ul>
  );

  return (
    <>
    <header className="header w-screen bg-white sticky flex h-20 w-full items-center justify-between border-b">
      <Navbar
        color="transparent"
        className="max-w-full w-full rounded-none py-0 my-0 px-6 h-20"
      >
        <div className="mx-auto flex items-center justify-between h-full">
          <Logo variant="default" />
          <div className="flex items-center gap-4">
            <div className="relative mx-auto flex items-center justify-between  lg:justify-start">
              <ProfileMenu />
            </div>
          </div>
        </div>
        <Collapse open={openNav}>
          {navList}
          <div className="flex items-center gap-x-1">
            <Button fullWidth variant="text" size="sm" className="">
              <span>Log In</span>
            </Button>
            <Button fullWidth variant="gradient" size="sm" className="">
              <span>Sign in</span>
            </Button>
          </div>
        </Collapse>
      </Navbar>
    </header>
    </>
  );
}
