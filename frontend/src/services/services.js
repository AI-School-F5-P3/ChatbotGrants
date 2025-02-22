export const API_URL =
    import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

import axios from "axios";

export async function startSession(userId) {
    try {
        const response = await axios.post(`${API_URL}/start_session`, {
            user_id: userId,
        });

        return response.data.message
            ? response.data
            : { message: "No se recibió mensaje del bot." };
    } catch (error) {
        console.error("Error starting session:", error);
        return { message: "Error al iniciar la sesión." };
    }
}

export async function chat(userId, inputMessage) {
    try {
        if (process.env.NODE_ENV !== "production") {
            console.log(
                "🔹 usuario -->",
                userId,
                "\n🔹 mensaje -->",
                inputMessage
            );
        }

        const response = await axios.post(`${API_URL}/chat`, {
            user_id: userId,
            message: inputMessage,
        });

        return response.data.message;
    } catch (error) {
        console.error("Error enviando el mensaje:", error);
        return "Hubo un error al procesar tu mensaje.";
    }
}

export const saveChat = async (userId, messages) => {
    try {
        if (messages.length === 0) return; // No enviar si no hay mensajes

        // Formatear mensajes para coincidir con el endpoint `/save_chat`
        const formattedMessages = messages.map(msg => ({
            userId: userId,  // Clave de partición en DynamoDB
            timestamp: new Date().toISOString(),  // Marca de tiempo ISO
            role: msg.sender,  // "user" o "bot"
            message_content: msg.text  // Contenido del mensaje
        }));

        await axios.post(`${API_URL}/save_chat`, { messages: formattedMessages });
        console.log("✅ Conversación guardada en la base de datos");
    } catch (error) {
        console.error("❌ Error guardando conversación:", error);
    }
};

export const getChatHistory = async (userId, conversationId) => {
    try {
        const response = await axios.get(`${API_URL}/get_chat_messages`, {
            params: { user_id: userId, conversation_id: conversationId },
        });
        return response.data.messages;
    } catch (error) {
        console.error("❌ Error obteniendo el historial de chat:", error);
        return [];
    }
};

export const getUserConversations = async (userId) => {
    try {
        console.log(`🔹 Obteniendo conversaciones del usuario: ${API_URL}/get_user_conversations/${userId}`);
        const response = await axios.get(`${API_URL}/get_user_conversations/${userId}`);

        // ✅ Cambiamos a "messages" porque es la clave correcta en la API
        const conversations = response.data.messages || [];
        
        console.log("✅ Conversaciones obtenidas:", conversations);
        return conversations;
    } catch (error) {
        console.error("❌ Error obteniendo la lista de conversaciones:", error);
        return [];  // ✅ Devuelve un array vacío en caso de error
    }
};



// Limpiar la conversación sin desloguear al usuario
export const clearChat = async (userId, messages, setMessages) => {
    try {
        await saveChat(userId, messages); // Guarda la conversación antes de limpiarla
        setMessages([]); // Limpia los mensajes del estado
        console.log("🗑 Conversación limpiada");

        await new Promise((resolve) => setTimeout(resolve, 100)); // Pequeña espera para actualizar React
    } catch (error) {
        console.error("❌ Error limpiando conversación:", error);
    }
};

// Cerrar sesión en el backend y limpiar el estado en el frontend
export const logoutAndEndSession = async (userId, messages, setIsAuthenticated, setUserId, navigate) => {
    try {
        await saveChat(userId, messages); // Guarda el historial antes de cerrar sesión

        await axios.delete(`${API_URL}/end_session/${userId}`); // Finaliza sesión en backend

        setIsAuthenticated(false);
        setUserId(null);
        localStorage.removeItem("userId");
        localStorage.removeItem("isAuthenticated");

        console.log("👋 Sesión finalizada y usuario deslogueado");
        navigate("/"); // Redirige al login
    } catch (error) {
        console.error("❌ Error cerrando sesión:", error);
    }
};
