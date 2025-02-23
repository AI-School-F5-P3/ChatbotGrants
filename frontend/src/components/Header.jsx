import React, { useState, useEffect } from "react";
import {
    Navbar,
    Collapse,
    Typography,
    Button,
    Menu,
    MenuHandler,
    MenuList,
    MenuItem,
    Avatar,
} from "@material-tailwind/react";
import { UserCircleIcon, PowerIcon } from "@heroicons/react/24/solid";

import userIcon from "/img/user.svg";
import { Logo } from "./Logo.jsx";
import { useAuthActions, useAuth } from "../context/AuthContext"; // ✅ Importa el hook de autenticación

// 📌 Opciones del menú de perfil
const profileMenuItems = [
    { label: "Mi perfil", icon: UserCircleIcon },
    { label: "Salir", icon: PowerIcon },
];

// 📌 Componente del menú de perfil
const ProfileMenu = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const { logout } = useAuthActions(); // ✅ Obtiene logout()
    const { user } = useAuth(); // ✅ Obtiene el usuario autenticado

    const closeMenu = () => setIsMenuOpen(false);

    return (
        <Menu open={isMenuOpen} handler={setIsMenuOpen} placement="bottom-end">
            <MenuHandler>
                <Button
                    variant="text"
                    className="flex items-center gap-1 rounded-full capitalize  py-0.5 pr-0 pl-4 lg:ml-auto"
                >
                    {user?.name}{" "}
                    {/* ✅ Muestra el nombre o email del usuario */}
                    <Avatar
                        variant="circular"
                        size="sm"
                        alt="User"
                        className="border-[5px] border-customLightBlue ml-2"
                        src={userIcon}
                    />
                </Button>
            </MenuHandler>
            <MenuList className="p-1">
                {profileMenuItems.map(({ label, icon }) => (
                    <MenuItem
                        key={label}
                        onClick={label === "Salir" ? logout : closeMenu} // ✅ Llama a logout al hacer clic en "Salir"
                        className={`flex items-center gap-2 rounded ${
                            label === "Salir"
                                ? "hover:bg-red-500/10 focus:bg-red-500/10 active:bg-red-500/10"
                                : ""
                        }`}
                    >
                        {React.createElement(icon, {
                            className: `h-4 w-4 ${
                                label === "Salir" ? "text-red-500" : ""
                            }`,
                            strokeWidth: 2,
                        })}
                        <Typography
                            as="span"
                            variant="small"
                            className="font-normal"
                            color={label === "Salir" ? "red" : "inherit"}
                        >
                            {label}
                        </Typography>
                    </MenuItem>
                ))}
            </MenuList>
        </Menu>
    );
};

// 📌 Componente `Header`
export const Header = () => {
    const [openNav, setOpenNav] = useState(false);
    const { logout } = useAuthActions(); // ✅ Obtiene logout() para el botón "Salir"

    useEffect(() => {
        window.addEventListener("resize", () => {
            if (window.innerWidth >= 960) setOpenNav(false);
        });
    }, []);

    return (
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
                    <div className="flex items-center gap-x-1">
                        <Button
                            fullWidth
                            variant="gradient"
                            size="sm"
                            onClick={logout}
                        >
                            <span>Salir</span>{" "}
                            {/* ✅ Ahora "Salir" cierra sesión */}
                        </Button>
                    </div>
                </Collapse>
            </Navbar>
        </header>
    );
};
