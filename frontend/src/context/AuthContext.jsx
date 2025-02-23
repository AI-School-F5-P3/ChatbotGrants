import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import users from "../mocks/users.json"; // ✅ Importa la lista de usuarios desde el JSON

// 📌 Crear el contexto de autenticación
const AuthContext = createContext();

// 📌 Proveedor de autenticación que gestiona el estado global de `isAuthenticated` y `userId`
export const AuthProvider = ({ children }) => {
    // ✅ Estado de autenticación: se inicializa desde `localStorage`
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        return localStorage.getItem("isAuthenticated") === "true";
    });

    // ✅ Estado del usuario autenticado (ID del usuario)
    const [userId, setUserId] = useState(() => {
        return localStorage.getItem("userId") || null;
    });

    // ✅ Guardar `isAuthenticated` y `userId` en `localStorage` cada vez que cambien
    useEffect(() => {
        localStorage.setItem("isAuthenticated", isAuthenticated);
        if (userId) {
            localStorage.setItem("userId", userId);
        }
    }, [isAuthenticated, userId]);

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, userId, setUserId }}>
            {children}
        </AuthContext.Provider>
    );
};

// 📌 Hook personalizado para manejar las acciones de autenticación (login y logout)
export const useAuthActions = () => {
    const navigate = useNavigate();
    const { setIsAuthenticated, setUserId } = useContext(AuthContext);

    // ✅ Función de inicio de sesión (verifica email y contraseña en `users.json`)
    const login = (email, password) => {
        // 🔎 Buscar en `users.json` si el usuario y contraseña coinciden
        const user = users.find(u => u.email === email && u.password === password);

        if (user) {
            // 🟢 Si es válido, actualiza el estado y guarda en `localStorage`
            setIsAuthenticated(true);
            setUserId(user.userId);
            console.log("🔑 Usuario autenticado:", user)
            localStorage.setItem("userId", user.userId);
            navigate("/chatbot"); // 🔀 Redirige al usuario a la página del chatbot
            return true;
        } else {
            // 🔴 Si las credenciales son incorrectas, retorna `false`
            return false;
        }
    };

    // ✅ Función de cierre de sesión (borra el estado y redirige al inicio)
    const logout = () => {
        setIsAuthenticated(false);
        setUserId(null);
        localStorage.removeItem("userId"); // 🗑️ Borra el ID del usuario
        localStorage.removeItem("isAuthenticated"); // 🗑️ Borra el estado de autenticación
        navigate("/"); // 🔀 Redirige al usuario a la página de inicio
    };

    return { login, logout };
};

// 📌 Hook para obtener el estado de autenticación en cualquier parte de la app
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth debe estar dentro de AuthProvider");
    }
    return context;
};
