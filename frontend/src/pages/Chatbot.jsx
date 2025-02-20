import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // ✅ Importa el contexto

import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import Chat from "../components/Chat";

function Chatbot() {
    const { isAuthenticated } = useAuth(); // ✅ Verifica si el usuario está autenticado

    // 🔒 Si el usuario no está autenticado, redirigir al login
    if (!isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    return (
        <div className="h-[calc(100vh-2rem)] bg-background flex w-full flex-col sm:flex-row">
            <main className="main relative min-h-screen-patched flex-1 bg-custom10Gray">
                <Header />
                <Sidebar />
                <Chat />
            </main>
        </div>
    );
}

export default Chatbot;
