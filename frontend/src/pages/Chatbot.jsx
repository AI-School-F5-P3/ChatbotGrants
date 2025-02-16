import React from "react";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import Chat from "../components/Chat";
// import "../app.css";

function Chatbot() {
    return (
        <>
            <div className="h-[calc(100vh-2rem)] bg-background flex w-full flex-col sm:flex-row">
                <main className="main relative min-h-screen-patched flex-1 bg-custom10Gray">
                    <Header />
                    <Sidebar />
                    <Chat />
                </main>
            </div>
        </>
    );
}

export default Chatbot;
