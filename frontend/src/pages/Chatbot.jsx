import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // Importa el contexto
import { startSession, clearChat,getUserConversations, } from "../services/services";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import Chat from "../components/Chat";

function Chatbot() {
    const { isAuthenticated, userId } = useAuth(); // Verifica si el usuario está autenticado
    const [messages, setMessages] = useState([]); // Maneja los mensajes del chat
    const [isInputDisabled, setIsInputDisabled] = useState(false); //  Maneja el estado de input deshabilitado
    const [isSavedConversation, setIsSavedConversation] = useState(false); //  Maneja el estado de conversación guardada
    const [conversations, setConversations] = useState([]); //  Maneja las conversaciones del usuario
    const [inputMessage, setInputMessage] = useState("");
        

    const initNewConversation = async () => {
        try {
            setIsSavedConversation(false); //  Reinicia el estado de conversación guardada
            setIsInputDisabled(false); //  Habilita el input para enviar mensajes
            const data = await startSession(userId);
            setMessages([{ sender: "bot", text: data.message }]);
        } catch (err) {
            console.error("Error iniciando nueva sesión:", err);
        }
    };



    // Función para iniciar una nueva conversación
    const handleNewConversation = async (save, isSavedConversation) => {
        // Recibe un booleano para guardar o no la conversación
        console.log("Nueva conversación iniciada");

        if (save | isSavedConversation) {
            //  Si el usuario eligió guardar la conversación o si ya está guardada
            await clearChat(userId, messages, setMessages); //  Solo se guarda si el usuario eligió "Sí"
            const updatedConversations = await getUserConversations(userId);
            setConversations(updatedConversations);
            console.log("✅ Conversación guardada y limpiada");
        } else {
            setMessages([]); //  Si no guarda, simplemente limpia los mensajes sin llamar a clearChat
            console.log("🗑 Conversación limpiada sin guardar");
        }

        setInputMessage(""); // Limpiar input después de enviar
        initNewConversation(); //  Inicia una nueva conversación
    };

    // 🔒 Si el usuario no está autenticado, redirigimos al login
    if (!isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    return (
        <div className="h-[calc(100vh-2rem)] bg-background flex w-full">
            <main className="main relative min-h-screen-patched flex-1 bg-custom10Gray">
                <Header />
                <Sidebar
                    onNewConversation={handleNewConversation}
                    userId={userId}
                    setMessages={setMessages}
                    isInputDisabled={isInputDisabled}
                    setIsInputDisabled={setIsInputDisabled}
                    isSavedConversation={isSavedConversation}
                    setIsSavedConversation={setIsSavedConversation}
                    conversations={conversations}
                    setConversations={setConversations}
                    setInputMessage={setInputMessage}
                />
                <Chat
                    userId={userId}
                    messages={messages}
                    setMessages={setMessages}
                    isInputDisabled={isInputDisabled}
                    setIsInputDisabled={setIsInputDisabled}
                    inputMessage={inputMessage}
                    setInputMessage={setInputMessage}
                />
            </main>
        </div>
    );
}

export default Chatbot;
