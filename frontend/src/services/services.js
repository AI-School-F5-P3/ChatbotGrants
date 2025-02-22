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

export const saveChatHistory = async (userId, messages) => {
    try {
        // Convertir mensajes en un formato adecuado para DynamoDB
        const formattedMessages = messages.map(msg => ({
            userId: userId,  // Clave de partición
            timestamp: new Date().toISOString(),  // Clave de ordenación
            role: msg.sender,  // "user" o "bot"
            message_content: msg.text  // Contenido del mensaje
        }));

        await axios.post(`${API_URL}/save_chat`, { messages: formattedMessages });
        console.log("Histórico guardado en la base de datos");
    } catch (error) {
        console.error("Error guardando historial:", error);
    }
};

// Limpiar la conversación sin desloguear al usuario
export const clearChat = async (userId, messages, setMessages) => {
    try {
        // Guardar historial antes de limpiar
        // await saveChatHistory(userId, messages);

        // Limpiar los mensajes del estado
        setMessages([]);
        console.log("Conversación limpiada");

        // Esperar un pequeño tiempo para asegurar que React actualiza el estado
        await new Promise((resolve) => setTimeout(resolve, 100));
    } catch (error) {
        console.error("Error limpiando conversación:", error);
    }
};

// Cerrar sesión en el backend y limpiar el estado en el frontend
export const logoutAndEndSession = async (
    userId,
    messages,
    setIsAuthenticated,
    setUserId,
    navigate
) => {
    try {
        // Guardar historial antes de cerrar sesión
        // await saveChatHistory(userId, messages);

        // Finalizar sesión en el backend
        await axios.delete(`${API_URL}/end_session/${userId}`);

        // Limpiar estado de autenticación en frontend
        setIsAuthenticated(false);
        setUserId(null);
        localStorage.removeItem("userId"); // ✅ Borra `userId` de localStorage
        localStorage.removeItem("isAuthenticated"); // ✅ Borra autenticación

        console.log("Sesión finalizada y usuario deslogueado");

        // Redirigir al login
        navigate("/");
    } catch (error) {
        console.error("Error cerrando sesión:", error);
    }
};
