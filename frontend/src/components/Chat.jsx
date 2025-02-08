import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  Button,
  Card,
  Typography,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
  Input,
} from "@material-tailwind/react";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [context, setContext] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Iniciar la conversación con el chatbot
    sendMessage("", true);
  }, []);

  const sendMessage = async (message, isInitial = false) => {
    try {
      const response = await axios.post("http://localhost:8000/chat", {
        message: message,
        context: context,
      });

      const newMessage = isInitial
        ? { sender: "bot", text: response.data.response }
        : { sender: "user", text: message };

      setMessages((prevMessages) => [...prevMessages, newMessage]);

      if (!isInitial) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "bot", text: response.data.response },
        ]);
      }

      setContext((prevContext) => prevContext + "\n" + message);
      setIsFinalRecommendation(response.data.is_final_recommendation);

      if (response.data.is_final_recommendation) {
        // Aquí puedes manejar la recomendación final, por ejemplo, mostrando un mensaje especial
        console.log("Recomendación final recibida");
      }
    } catch (error) {
      console.error("Error al enviar mensaje:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          sender: "bot",
          text: "Lo siento, ha ocurrido un error. Por favor, inténtalo de nuevo.",
        },
      ]);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (inputMessage.trim() !== "" && inputMessage.trim() !== "\n") {
      sendMessage(inputMessage);
      setInputMessage("");
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <>
      <div className="chat-area flex items-center align-center justify-center w-full">
        <div className="w-full flex flex-col items-center gap-4 text-center text-sm text-gray-500">
          <div className="w-[calc(100vw-23rem)] flex flex-col space-y-2 overflow-y-auto p-4 h-[calc(100vh-17rem)] bg-white rounded-lg border border-gray-300 shadow-md">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg max-w-[80%] ${
                  msg.sender === "user"
                    ? "bg-blue-200 self-end text-right ml-auto mb-1"
                    : "bg-gray-200 self-start text-left mr-auto mb-1"
                } overflow-wrap break-words`}
              >
                {msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form
            onSubmit={handleSendMessage}
            className="w-[calc(100vw-23rem)] flex items-center rounded-lg border border-gray-300 p-2 bg-white rounded-b-lg shadow-md"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Escribe tu mensaje"
              className="flex-grow px-4 py-2 outline-none rounded-lg w-4/5 font-outfit"
            />
            <Button
              type="submit"
              className="text-white bg-customLightBlue rounded-full p-2 shadow-lg transition-transform duration-150 ease-in-out transform active:scale-95"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                className="text-white h-6 w-6"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
                />
              </svg>
            </Button>
          </form>
        </div>
      </div>
    </>
  );
};

export default Chat;
