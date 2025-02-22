import React, { useEffect, useState } from "react";
import { useAuthActions } from "../context/AuthContext";
import { getUserConversations, getChatHistory } from "../services/services";
import {
    Button,
    Card,
    Typography,
    List,
    ListItem,
    ListItemPrefix,
    Alert,
} from "@material-tailwind/react";
import { DocumentTextIcon } from "@heroicons/react/24/solid";

export function Sidebar({ onNewConversation, userId, setMessages }) {
    const [conversations, setConversations] = useState([]);
    const [openAlert, setOpenAlert] = useState(true);
    const { logout } = useAuthActions();

    // Obtener la lista de conversaciones al cargar el componente
    useEffect(() => {
        if (userId) {
            getUserConversations(userId).then(setConversations);
        }
    }, [userId]);

    // Función para cargar una conversación guardada
    const handleLoadConversation = async (conversationId) => {
        const rawMessages = await getChatHistory(userId, conversationId);

        // Transformamos los mensajes para que coincidan con la estructura esperada en Chat.jsx
        const formattedMessages = rawMessages.map((msg) => ({
            sender: msg.role, // "user" o "bot"
            text: msg.message_content, // Mensaje en el formato esperado
        }));

        setMessages(formattedMessages);
    };

    return (
        <Card className="sidebar h-[calc(100vh-7rem)] p-4 shadow-xl shadow-blue-gray-900/5 rounded-none border-r border-solid border-custom10Gray">
            <div className="flex flex-row flex-wrap items-center justify-center p-2 pt-5">
                <Button
                    variant="outlined"
                    onClick={onNewConversation}
                    className="hover:text-white hover:bg-customBlue mb-4 border border-customBlue text-customBlue"
                >
                    Nueva conversación
                </Button>
            </div>

            <List className="min-w-full text-customGray">
                <Typography
                    color="blue-gray"
                    className="flex items-center text-center text-sm font-semibold text-customGray px-1"
                >
                    Histórico
                </Typography>
                <hr className="my-2 border-blue-gray-50" />
                <div className="overflow-y-auto h-[calc(100vh-19rem)]">
                    {/* Muestra cada conversación con su fecha */}
                    {conversations && conversations.length > 0 ? (
                        conversations.map((conv) => (
                            <ListItem
                                key={conv.conversationId}
                                onClick={() =>
                                    handleLoadConversation(conv.conversationId)
                                }
                                className="cursor-pointer hover:bg-gray-200"
                            >
                                <ListItemPrefix>
                                    <DocumentTextIcon className="h-5 w-5" />
                                </ListItemPrefix>
                                {conv.conversation_date}
                                {/* Se muestra la fecha del último mensaje */}
                            </ListItem>
                        ))
                    ) : (
                        <Typography className="text-center text-gray-500 text-sm mt-2">
                            No hay conversaciones guardadas
                        </Typography>
                    )}
                </div>
            </List>

            <Alert
                open={openAlert}
                className="mt-auto absolute bottom-4 w-[calc(100%-2rem)]"
                onClose={() => setOpenAlert(false)}
            >
                <Typography variant="h6" className="mb-1">
                    Aviso
                </Typography>
                <Typography variant="small" className="font-normal opacity-80">
                    Las conversaciones con más de 30 días de antigüedad se
                    eliminarán automáticamente.
                </Typography>
            </Alert>
        </Card>
    );
}
