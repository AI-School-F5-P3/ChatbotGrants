import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // Importa el contexto
import { startSession, clearChat } from "../services/services";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import Chat from "../components/Chat";

function Chatbot() {
    const { isAuthenticated, userId } = useAuth(); // Verifica si el usuario está autenticado
    const [messages, setMessages] = useState([]); // Maneja los mensajes del chat

    // Función para iniciar una nueva conversación
    const handleNewConversation = async () => {
        console.log("Nueva conversación iniciada");
    
        // Llamamos a 'clearChat' para guardar el historial y limpiar mensajes
        await clearChat(userId, messages, setMessages);
    
        try {
            const data = await startSession(userId); // Iniciar nueva sesión
            setMessages([{ sender: "bot", text: data.message }]); // Agregar mensaje de bienvenida
        } catch (err) {
            console.error("Error iniciando nueva sesión:", err);
        }
    };

    // 🔒 Si el usuario no está autenticado, redirigimos al login
    if (!isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    return (
        <div className="h-[calc(100vh-2rem)] bg-background flex w-full">
            <main className="main relative min-h-screen-patched flex-1 bg-custom10Gray">
                <Header />
                <Sidebar onNewConversation={handleNewConversation} />
                <Chat
                    userId={userId}
                    messages={messages}
                    setMessages={setMessages}
                />
            </main>
        </div>
    );
}

export default Chatbot;
