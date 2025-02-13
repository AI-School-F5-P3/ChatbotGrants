export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080/api";

import axios from "axios";

export async function startSession(userId) {
    try {
        const response = await fetch(`${API_URL}/start_session`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId }),
        });

        if (!response.ok) throw new Error("Failed to start session");

        const data = await response.json();

        // Aseguramos que data tenga un mensaje válido
        return data.message
            ? data
            : { message: "No se recibió mensaje del bot." };
    } catch (error) {
        console.error("Error starting session:", error);
        return { message: "Error al iniciar la sesión." }; // Mensaje de fallback
    }
}

// export async function chat(userId, inputMessage, setMessages) {
//     try {
//         console.log(
//             "🔹 usuario --> ",
//             userId,
//             "\n🔹 mensaje --> ",
//             inputMessage
//         );
//         const response = await axios.post(
//             `${API_URL}/chat`,
//             {
//                 user_id: userId,
//                 message: inputMessage,
//             },
//             {
//                 headers: {
//                     "Content-Type": "application/json",
//                 },
//             }
//         );

//         // Extraer la respuesta del bot
//         const botMessage = response.data.message;

//         // Agregar la respuesta del bot al chat
//         setMessages((prevMessages) => [
//             ...prevMessages,
//             { sender: "bot", text: botMessage }, // Mostrar la siguiente pregunta
//         ]);
//     } catch (error) {
//         console.error("Error enviando el mensaje:", error);
//     }
// }

export async function chat(userId, inputMessage) {
    try {
        console.log("🔹 usuario -->", userId, "\n🔹 mensaje -->", inputMessage);

        const response = await axios.post(
            `${API_URL}/chat`,
            {
                user_id: userId,
                message: inputMessage,
            },
            {
                headers: { "Content-Type": "application/json" },
            }
        );

        return response.data.message; // Retornar el mensaje en lugar de actualizar el estado aquí
    } catch (error) {
        console.error("Error enviando el mensaje:", error);
        return "Hubo un error al procesar tu mensaje."; // Respuesta de fallback
    }
}
