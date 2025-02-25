import { createBrowserRouter, Navigate } from "react-router-dom";
import Home from "../pages/Home";
import Chatbot from "../pages/Chatbot";
import Layout from "../layout/Layout"; // ✅ Importamos Layout
import { useAuth, useAuthActions } from "../context/AuthContext"; // ✅ Importamos el hook correcto
import { useEffect } from "react";

const ProtectedRoute = ({ element }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? element : <Navigate to="/" replace />;
};

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout />, // ✅ Ahora todas las rutas están dentro de Layout
        children: [
            {
                index: true,
                element: <Home />, // ✅ Home ahora obtiene `login` directamente del contexto
            },
            {
                path: "chatbot",
                element: <ProtectedRoute element={<Chatbot />} />, // 🔒 Ruta protegida
            },
        ],
    },
]);
