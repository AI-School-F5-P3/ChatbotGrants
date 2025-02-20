import { createBrowserRouter, Navigate } from "react-router-dom";
import Home from "../pages/Home";
import Chatbot from "../pages/Chatbot";
import Layout from "../layout/Layout"; // ✅ Importamos Layout
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

const ProtectedRoute = ({ element }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? element : <Navigate to="/" replace />;
};

const AuthWrapper = ({ children }) => {
    const navigate = useNavigate();
    const { isAuthenticated, setIsAuthenticated } = useAuth();

    const login = (email, password) => {
        if (email === "admin@ayming.com" && password === "admin") {
            setIsAuthenticated(true);
            navigate("/chatbot"); // ✅ Ahora es seguro llamar `navigate`
            return true;
        } else {
            return false;
        }
    };

    const logout = () => {
        setIsAuthenticated(false);
        navigate("/");
    };

    return children({ login, logout });
};

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout />, // ✅ Ahora todas las rutas están dentro de Layout
        children: [
            {
                index: true,
                element: (
                    <AuthWrapper>
                        {({ login, logout }) => <Home login={login} logout={logout} />}
                    </AuthWrapper>
                ),
            },
            {
                path: "chatbot",
                element: <ProtectedRoute element={<Chatbot />} />, // 🔒 Ruta protegida
            },
        ],
    },
]);
