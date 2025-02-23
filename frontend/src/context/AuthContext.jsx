import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import users from "../mocks/users.json"; // ✅ Importa la lista de usuarios desde el JSON

// 📌 Crear el contexto de autenticación
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        return localStorage.getItem("isAuthenticated") === "true";
    });

    // ✅ Estado del usuario autenticado (se guarda el objeto completo)
    const [user, setUser] = useState(() => {
        const storedUser = localStorage.getItem("user");
        return storedUser ? JSON.parse(storedUser) : null;
    });

    // ✅ Guardar en `localStorage` cada vez que `user` o `isAuthenticated` cambian
    useEffect(() => {
        localStorage.setItem("isAuthenticated", isAuthenticated);
        if (user) {
            localStorage.setItem("user", JSON.stringify(user));
        } else {
            localStorage.removeItem("user");
        }
    }, [isAuthenticated, user]);

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, user, setUser }}>
            {children}
        </AuthContext.Provider>
    );
};

// 📌 Hook para manejar login y logout
export const useAuthActions = () => {
    const navigate = useNavigate();
    const { setIsAuthenticated, setUser } = useContext(AuthContext);

    const login = (email, password) => {
        // 🔎 Buscar en `users.json` si el usuario y contraseña coinciden
        const userFound = users.find(u => u.email === email && u.password === password);

        if (userFound) {
            setIsAuthenticated(true);
            setUser(userFound); // 🟢 Guarda el usuario completo en el estado
            localStorage.setItem("user", JSON.stringify(userFound));
            console.log("🔑 Usuario autenticado:", userFound);
            navigate("/chatbot");
            return true;
        } else {
            console.log("❌ Usuario no encontrado o credenciales incorrectas");
            return false;
        }
    };

    const logout = () => {
        setIsAuthenticated(false);
        setUser(null);
        localStorage.removeItem("user");
        localStorage.removeItem("isAuthenticated");
        navigate("/");
    };

    return { login, logout };
};

// 📌 Hook para acceder a la autenticación desde cualquier parte de la app
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth debe estar dentro de AuthProvider");
    }
    return context;
};
