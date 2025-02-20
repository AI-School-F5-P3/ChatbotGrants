import React, { createContext, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook para manejar autenticación con `useNavigate()`
export const useAuthActions = () => {
    const navigate = useNavigate();
    const { setIsAuthenticated } = useContext(AuthContext);

    const login = (email, password) => {
        if (email === "admin@ayming.com" && password === "admin") {
            setIsAuthenticated(true);
            navigate("/chatbot");
            return true;
        } else {
            return false;
        }
    };

    const logout = () => {
        setIsAuthenticated(false);
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
