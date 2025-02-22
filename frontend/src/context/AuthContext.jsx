import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        return localStorage.getItem("isAuthenticated") === "true"; // ✅ Recupera autenticación de localStorage
    });
    const [userId, setUserId] = useState(() => {
        return localStorage.getItem("userId") || null; // ✅ Recupera userId de localStorage
    });

    // ✅ Guardar en `localStorage` cada vez que `userId` o `isAuthenticated` cambian
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

// Hook para manejar autenticación con `useNavigate()`
export const useAuthActions = () => {
    const navigate = useNavigate();
    const { setIsAuthenticated, setUserId } = useContext(AuthContext);

    const login = (email, password) => {
        if (email === "admin@ayming.com" && password === "admin") {
            setIsAuthenticated(true);
            const newUserId = `user_${email}`;
            setUserId(newUserId);
            localStorage.setItem("userId", newUserId); // ✅ Guarda `userId` en localStorage
            navigate("/chatbot");
            return true;
        } else {
            return false;
        }
    };

    const logout = () => {
        setIsAuthenticated(false);
        setUserId(null);
        localStorage.removeItem("userId"); // ✅ Borra `userId` al cerrar sesión
        localStorage.removeItem("isAuthenticated"); // ✅ Borra estado de autenticación
        navigate("/");
    };

    return { login, logout };
};

// Hook para obtener el estado de autenticación
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth debe estar dentro de AuthProvider");
    }
    return context;
};
