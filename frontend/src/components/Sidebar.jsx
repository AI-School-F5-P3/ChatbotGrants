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
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
} from "@material-tailwind/react";
import { DocumentTextIcon } from "@heroicons/react/24/solid";

export function Sidebar({
    onNewConversation,
    userId,
    setMessages,
    isInputDisabled,
    setIsInputDisabled,
    conversations,
    setConversations,
    isSavedConversation,
    setIsSavedConversation,
    setInputMessage,
}) {
    const [openAlert, setOpenAlert] = useState(true);
    const [openDialog, setOpenDialog] = useState(false);
    const { logout } = useAuthActions();

    useEffect(() => {
        if (userId) {
            getUserConversations(userId).then(setConversations);
        }
    }, [userId]);

    const handleLoadConversation = async (conversationId) => {
        const rawMessages = await getChatHistory(userId, conversationId);
        const formattedMessages = rawMessages.map((msg) => ({
            sender: msg.role,
            text: msg.message_content,
        }));
        setMessages(formattedMessages);
        setIsInputDisabled(true);
        setInputMessage("");
        setIsSavedConversation(true);
    };

    const handleNewConversation = () => {
        if (isSavedConversation) {
            onNewConversation(false);
        } else {
            setOpenDialog(true);
        }
    };

    const handleDialogClose = () => {
        setOpenDialog(false);
    };

    const handleConfirmNewConversation = async (save) => {
        setOpenDialog(false); // Cierra el diálogo siempre
        onNewConversation(save); // Se mantiene la llamada a onNewConversation, que manejará el guardado si es necesario
    };

    return (
        <Card className="sidebar h-[calc(100vh-7rem)] p-4 shadow-xl shadow-blue-gray-900/5 rounded-none border-r border-solid border-custom10Gray">
            <div className="flex flex-row flex-wrap items-center justify-center p-2 pt-5">
                <Button
                    variant="outlined"
                    onClick={handleNewConversation}
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
                                    <DocumentTextIcon className="h-4 w-4" />
                                </ListItemPrefix>
                                {conv.conversation_date}
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

            <Dialog open={openDialog} handler={handleDialogClose}>
                <DialogHeader>Guardar conversación</DialogHeader>
                <DialogBody>
                    ¿Deseas guardar la conversación actual antes de iniciar una
                    nueva?
                </DialogBody>
                <DialogFooter>
                    <Button
                        variant="text"
                        color="gray"
                        onClick={() => handleConfirmNewConversation(false)}
                    >
                        No
                    </Button>
                    <Button
                        variant="gradient"
                        color="blue"
                        onClick={() => handleConfirmNewConversation(true)}
                    >
                        Sí, guardar
                    </Button>
                </DialogFooter>
            </Dialog>
        </Card>
    );
}
