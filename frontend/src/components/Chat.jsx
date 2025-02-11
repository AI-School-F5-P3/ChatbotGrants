import React, { useState, useEffect, useRef } from "react";
import {
    Button,
    ButtonGroup,
    Card,
    CardHeader,
    CardBody,
    Typography,
    Avatar,
} from "@material-tailwind/react";
import Typewriter from "./Typewriter";
import user from "/img/user.svg";
import ayming from "/img/logo_icono.svg";
import { chat, startSession } from "../services/services";

const userId = "user_" + Math.random().toString(36).slice(2, 9);

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    // Llamada inicial al endpoint /msg/ cuando la página carga
    useEffect(() => {
        startSession(userId)
            .then((data) => {
                console.log("Sesión iniciada");
                setMessages([{ sender: "bot", text: data.message }]); // Agrega el mensaje inicial del bot
            })
            .catch((err) => console.error("Error iniciando sesión:", err));
    }, []);

    // Scroll automático al último mensaje
    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollTo({
                top: messagesEndRef.current.scrollHeight,
                behavior: "smooth",
            });
        }
    }, [messages]); // Se ejecuta cada vez que cambia la lista de mensajes

    // Manejo del envío de mensajes
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        // Agregar mensaje del usuario al estado
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "user", text: inputMessage },
        ]);

        setIsTyping(true);

        try {
            await chat(userId, inputMessage, setMessages);
        } catch (error) {
            console.error("Error enviando el mensaje:", error);
        }

        // // Ocultar loader cuando el bot responda
        setIsTyping(false);

        // Limpiar el input después de enviar
        setInputMessage("");
    };

    return (
        <div className="chat-area flex items-center justify-center w-full">
            <div className="w-full h-full flex flex-col items-center justify-end gap-4 text-center text-sm text-customGray pb-8">
                <Card
                    color="transparent"
                    shadow={false}
                    className="flex flex-col-reverse rounded-none w-[calc(100vw-23rem)] overflow-y-auto p-0 h-[calc(100vh-16rem)] "
                >
                    {/* <div className="mb-5">
                        {messages.map((msg, index) => (
                            <Card
                                color="transparent"
                                shadow={false}
                                key={index}
                                className="overflow-hidden flex flex-column"
                            >
                                <span
                                    className={`inline-block flex flex-row max-w-full w-[80%] ${
                                        msg.sender === "user"
                                            ? "chat-msg flex-row-reverse text-right ml-auto my-4"
                                            : "chat-msg text-left mr-auto"
                                    } break-words`}
                                >
                                    <Avatar
                                        variant="circular"
                                        size="md"
                                        alt={
                                            msg.sender === "user"
                                                ? "User"
                                                : "Ayming"
                                        }
                                        className={`${
                                            msg.sender === "user"
                                                ? "border-customLightBlue ml-2"
                                                : "border-white mr-2"
                                        } border-[5px] bg-white`}
                                        src={
                                            msg.sender === "user"
                                                ? user
                                                : ayming
                                        }
                                    />

                                    <CardBody
                                        className={`p-3 rounded-lg max-w-[80%] ${
                                            msg.sender === "user"
                                                ? "bg-customLightBlue text-white text-right ml-auto mt-[.1rem]"
                                                : "bg-white text-left mr-auto mt-[.1rem]"
                                        } break-words`}
                                    >
                                        {msg.sender === "user" ? (
                                            msg.text
                                        ) : (
                                            <>
                                                <Typewriter
                                                    text={msg.text}
                                                    delay={5}
                                                />
                                            </>
                                        )}
                                    </CardBody>
                                </span>
                            </Card>
                        ))}

                        <div ref={messagesEndRef} />
                    </div> */}
                    <div className="mb-5">
                        {messages.map((msg, index) => (
                            <Card
                                color="transparent"
                                shadow={false}
                                key={index}
                                className="overflow-hidden flex flex-column"
                            >
                                <span
                                    className={`inline-block flex flex-row max-w-full w-[80%] ${
                                        msg.sender === "user"
                                            ? "chat-msg flex-row-reverse text-right ml-auto my-4"
                                            : "chat-msg text-left mr-auto"
                                    } break-words`}
                                >
                                    <Avatar
                                        variant="circular"
                                        size="md"
                                        alt={
                                            msg.sender === "user"
                                                ? "User"
                                                : "Ayming"
                                        }
                                        className={`${
                                            msg.sender === "user"
                                                ? "border-customLightBlue ml-2"
                                                : "border-white mr-2"
                                        } border-[5px] bg-white`}
                                        src={
                                            msg.sender === "user"
                                                ? user
                                                : ayming
                                        }
                                    />

                                    <CardBody
                                        className={`p-3 rounded-lg max-w-[80%] ${
                                            msg.sender === "user"
                                                ? "bg-customLightBlue text-white text-right ml-auto mt-[.1rem]"
                                                : "bg-white text-left mr-auto mt-[.1rem]"
                                        } break-words`}
                                    >
                                        {msg.sender === "user" ? (
                                            msg.text
                                        ) : (
                                            <>
                                                {isTyping ? (
                                                    <div className="typing-indicator">
                                                        <span></span>
                                                        <span></span>
                                                        <span></span>
                                                    </div>
                                                ) : (
                                                    <Typewriter
                                                        text={msg.text}
                                                        delay={5}
                                                    />
                                                )}
                                            </>
                                        )}
                                    </CardBody>
                                </span>
                            </Card>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </Card>
                <form onSubmit={handleSendMessage}>
                    <Card className="w-[calc(100vw-23rem)] flex flex-row justify-between p-2 bg-white">
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Escribe tu mensaje"
                            className="placeholder:text-slate-400 px-4 py-2 outline-none rounded-lg w-[calc(100%-2.6rem)] font-outfit"
                        />
                        <Button
                            type="submit"
                            className="text-white bg-customLightBlue rounded-full p-2 pl-[0.65rem] shadow-lg w-[2.6rem] h-[2.6rem] flex align-center justify-center"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth="1.5"
                                stroke="currentColor"
                                className="text-white h-6 w-6"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
                                />
                            </svg>
                        </Button>
                    </Card>
                </form>
            </div>
        </div>
    );
};

export default Chat;
