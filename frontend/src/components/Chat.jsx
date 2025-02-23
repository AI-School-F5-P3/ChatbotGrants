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
import user from "/img/user.svg";
import ayming from "/img/logo_icono.svg";
import { chat, startSession } from "../services/services";
import MarkdownRenderer from "./MarkdownRenderer";

const Chat = ({userId, messages, setMessages, isInputDisabled, setIsInputDisabled, inputMessage, setInputMessage}) => {
    const [isTyping, setIsTyping] = useState(false);
    const [isSessionActive, setIsSessionActive] = useState(true);
    const inputRef = useRef(null);
    const messagesEndRef = useRef(null);

    //     const markdown_content = `
    // Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

    // {% details summary="BDNS: 676689 · Subvenciones para el Fomento de la Contratación en la Comunidad de Madrid" %}

    // # Subvenciones para el Fomento de la Contratación en la Comunidad de Madrid

    // ## Información General

    // | **Concepto**                          | **Detalle** |
    // |----------------------------------------|------------|
    // | **Objetivo**                           | Mejorar la empleabilidad e incorporar al mercado laboral a personas desempleadas, especialmente de colectivos vulnerables. |
    // | **Plazo de presentación**              | Abierta hasta agotar fondos. |
    // | **Fondos disponibles**                 | 120.000.000 € |
    // | **Ámbito de aplicación**               | Comunidad de Madrid |
    // | **Ayuda máxima por beneficiario**      | 14.000 € |
    // | **Convocatoria**                       | [Sede electrónica](https://www.comunidad.madrid/servicios/empleo/ayudas-e-incentivos-empleo) |
    // | **BDNS**                               | 676689 |
    // | **Órgano convocante**                  | Comunidad de Madrid - Consejería de Economía, Hacienda y Empleo |
    // | **Concurrencia**                       | No competitiva (las solicitudes se atienden por orden de presentación). |
    // | **Sujeta a mínimis**                   | Sí |

    // ## Beneficiarios

    // | **Línea de subvención** | **Beneficiarios** |
    // |------------------------|-----------------|
    // | **Líneas 1, 2, 3, 4 y 5** | Autónomos, empresas y entidades privadas sin ánimo de lucro. Agrupaciones privadas de personas físicas o jurídicas, comunidades de bienes u otras unidades económicas sin personalidad jurídica. |
    // | **Línea 6** | Empresas de inserción, entidades sin ánimo de lucro con programas de empleo, centros especiales de empleo. |

    // ## Plazo para la Solicitud

    // - **El plazo de presentación es de 1 mes** desde la fecha de alta en la Seguridad Social de la persona contratada.

    // ## Líneas de Subvención y Cuantía

    // | **Línea** | **Descripción** | **Ayuda** |
    // |----------|----------------|------------|
    // | **Línea 1** | Contratación indefinida de personas desempleadas de especial atención. | Entre 5.500 € y 7.500 € según el colectivo contratado. |
    // | **Línea 2** | Contratación estable de personas jóvenes. | 5.500 € por contratación indefinida. |
    // | **Línea 3** | Contrato formativo para la práctica profesional de personas jóvenes. | 5.500 € por contrato formativo. |
    // | **Línea 4** | Contrato de formación en alternancia para personas jóvenes. | 5.500 € por contrato formativo. |
    // | **Línea 5** | Contratación de personas con discapacidad y colectivos vulnerables. | Entre 6.500 € y 9.500 €, según el colectivo. |
    // | **Línea 6** | Contratación de personas participantes en itinerarios de inserción. | 3.000 € a entidades de inserción. |

    // ## Requisitos de las Contrataciones

    // - El centro de trabajo debe estar en la Comunidad de Madrid.
    // - La contratación debe formalizarse en el modelo oficial de contrato.
    // - La alta en Seguridad Social y el inicio de la relación laboral deben ser previos a la solicitud.

    // ## Obligaciones de los Beneficiarios

    // | **Línea** | **Periodo mínimo de mantenimiento del contrato** |
    // |----------|-----------------------------------------------|
    // | **Líneas 1, 2, 4 y 5** | 12 meses (360 días). |
    // | **Línea 3** | 6 meses (180 días). |
    // | **Línea 6** | 6 meses con seguimiento y acompañamiento del trabajador. |

    // ## Exclusiones

    // - No se subvencionarán contrataciones indefinidas de personas que en los 6 meses anteriores hayan trabajado en la misma empresa con contrato indefinido.

    // ## Requisitos de las Personas Contratadas

    // | **Líneas** | **Requisitos** |
    // |-----------|--------------|
    // | **Líneas 1, 5 y 6** | Personas desempleadas inscritas como demandantes de empleo, salvo excepciones en Línea 5 y Línea 6 para trabajadores con discapacidad y colectivos en exclusión social. |
    // | **Líneas 2, 3 y 4** | Menores de 30 años, inscritos en el Sistema Nacional de Garantía Juvenil y como demandantes de empleo. |
    // | **Línea 3 (específico)** | Deben tener título universitario, grado medio/superior, máster o certificado de formación profesional. |
    // | **Línea 4 (específico)** | Deben carecer de cualificación profesional para formalizar un contrato formativo. |

    // ## Documentos y Enlaces de Interés

    // - **Modificación de Bases Reguladoras (26 de diciembre de 2024):**
    //   [BOCM - 30 de diciembre de 2024](https://www.bocm.es/boletin/CM_Orden_BOCM/2024/12/30/BOCM-20241230-21.PDF)
    // - **Más información:**
    //   - [Comunidad de Madrid - Ayudas e Incentivos](https://www.comunidad.madrid/servicios/empleo/ayudas-e-incentivos-empleo)
    //   - [InfoSubvenciones BDNS 676689](https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/676689)
    // {% /details %}
    // {% details summary="BDNS: 689676 · Bonificaciones en las Cuotas de Seguridad Social para Desarrolladores e Investigadores" %}
    // # Bonificaciones en las Cuotas de Seguridad Social para Desarrolladores e Investigadores

    // ## Información General

    // | **Concepto**                          | **Detalle** |
    // |----------------------------------------|------------|
    // | **Objetivo**                           | Incentivo no tributario para la contratación y mantenimiento del empleo con dedicación exclusiva a actividades de I+D+i. |
    // | **Plazo de presentación**              | Siempre abierta. Presupuesto ilimitado. |
    // | **Fondos disponibles**                 | No especificado. |
    // | **Ámbito de aplicación**               | Estatal. |
    // | **Convocatoria**                       | [Sede electrónica](https://www.seg-social.es) |
    // | **Órgano convocante**                  | Ministerio de Ciencia, Innovación y Universidades. |
    // | **Entrada en vigor**                    | 1 de septiembre de 2023, según el RDL 01/2023. |

    // ## Beneficiarios

    // | **Tipo de beneficiarios** | **Condiciones** |
    // |--------------------------|----------------|
    // | **Autónomos, PYMES y Empresas** | Deben contratar personal dedicado 100% a proyectos de I+D+i. |

    // ## Requisitos Generales

    // | **Requisito** | **Descripción** |
    // |--------------|----------------|
    // | **Dedicación exclusiva** | El trabajador debe dedicarse **100%** a actividades de I+D+i. |
    // | **Tipo de contrato** | Aplicable a contratos indefinidos, en prácticas u obra de servicio de mínimo **3 meses**. |
    // | **Grupos de cotización** | Trabajadores en los grupos **1, 2, 3 y 4** del Régimen General de la Seguridad Social. |
    // | **Compatibilidad** | Compatible con deducciones fiscales por I+D o IT. |
    // | **Personal externo** | Aplica a personal investigador contratado para proyectos de clientes. |

    // ## Cuantía de la Ayuda

    // | **Concepto** | **Bonificación** |
    // |-------------|----------------|
    // | **Bonificación base** | **40%** en las aportaciones empresariales a la Seguridad Social sobre contingencias comunes (23,6% del sueldo). |
    // | **Duración máxima** | Hasta **3 años** por contrato. |
    // | **Contratación de jóvenes investigadores (<30 años)** | Bonificación adicional del **5%**. |
    // | **Contratación de mujeres investigadoras** | Bonificación adicional del **5%**. |
    // | **Bonificaciones acumulables** | Sí, en caso de que se cumplan ambas condiciones. |
    // | **Máximo por persona y año** | Puede superar los **4.000 €**. |

    // ## Gastos Cubiertos

    // | **Concepto** | **Detalle** |
    // |-------------|------------|
    // | **Cuotas de Seguridad Social** | Bonificación en las aportaciones empresariales a la Seguridad Social del personal investigador. |
    // | **Dedicación parcial permitida** | Se admite que hasta un **15% del tiempo** se dedique a formación, docencia o divulgación, manteniendo la exclusividad en I+D+i. |

    // ## Límites Adicionales

    // - **Las bonificaciones, junto con otras ayudas públicas, no pueden superar el 60% del coste salarial anual** del contrato bonificado.

    // ## Consideraciones Adicionales

    // | **Concepto** | **Detalle** |
    // |-------------|------------|
    // | **Número máximo de beneficiarios** | No hay límite de investigadores por empresa. |
    // | **Informe motivado** | Empresas que apliquen la bonificación a **10 o más investigadores** deberán presentar un informe motivado vinculante, emitido por el MINECO y tramitado a través de una entidad certificadora. |

    // ## Enlaces de Interés

    // - **Convocatoria y detalles**:
    //   - [Bonificaciones Seguridad Social para desarrolladores e investigadores](https://fandit.es/subvenciones/detalles-subvencion/bonificaciones-cuotas-de-la-seguridad-social-para-desarrolladores)
    //   - [Normativa RD 475/2014 sobre personal investigador](https://s3.eu-west-1.amazonaws.com/media.fandit.es/files/RD_475-2014_personal_investigador.pdf)
    //   - [Seguridad Social - Información y solicitud](https://www.seg-social.es)

    // {% /details %}
    // `;

    //     const markdown_content = `
    // # 🚀 ¡Bienvenido a Markdoc en Vite!

    // Este contenido está almacenado en una **variable**.

    // ---

    // - ✅ Basado en Markdown
    // - ⚡ Rápido y ligero
    // - 🔒 Seguro y controlado

    // ---

    // ## **¿Listo para probarlo?**

    // {% callout type="info" %}
    // Markdoc permite usar etiquetas personalizadas como esta.
    // {% /callout %}

    // | Nombre   | Edad | Ciudad      |
    // |----------|------|------------|
    // | Ana      | 25   | Madrid     |
    // | Juan     | 30   | Barcelona  |
    // | María    | 28   | Valencia   |

    // {% details summary="Ver más información" %}
    // Aquí hay contenido oculto que se muestra cuando haces clic.
    // {% /details %}

    // `;

    // Llamada inicial al endpoint /msg/ cuando la página carga
    useEffect(() => {
        startSession(userId)
            .then((data) => {
                console.log("Sesión iniciada con userId:", userId);
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
        console.log("Mensajes actualizados\n", messages);
    }, [messages]); // Se ejecuta cada vez que cambia la lista de mensajes

    // Manejo del envío de mensajes
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || !isSessionActive) return;

        // Agregar mensaje del usuario
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "user", text: inputMessage },
        ]);

        setIsTyping(true); // Mostrar el loader de "···" mientras el bot responde
        setInputMessage(""); // Limpiar input después de enviar
        setIsInputDisabled(true); // Deshabilitar el input mientras el bot responde
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "bot", text: "", isTyping: true }, // Mensaje temporal del bot con indicador
        ]);

        try {
            const botResponse = await chat(userId, inputMessage);

            // Reemplazar el mensaje del loader con la respuesta del bot
            setMessages((prevMessages) =>
                prevMessages.map((msg, index) =>
                    index === prevMessages.length - 1 && msg.isTyping
                        ? { sender: "bot", text: botResponse, isTyping: false }
                        : msg
                )
            );
        } catch (error) {
            console.error("Error enviando el mensaje:", error);
        }

        setIsTyping(false);
        setIsInputDisabled(false); // Reactivar input una vez que el bot responde
        // Restaurar el foco en el campo de entrada
        setTimeout(() => {
            if (inputRef.current) {
                inputRef.current.focus();
            }
        }, 100);
    };

    // const handleEndSession = () => {
    //     endSession(userId, messages, setMessages, setIsSessionActive);
    // };

    return (
        <div className="chat-area flex items-center justify-center">
            <div className="w-full h-full flex flex-col items-center justify-end gap-4 text-center text-sm text-customGray pb-8">
                <Card
                    color="transparent"
                    shadow={false}
                    className="flex flex-col-reverse rounded-none w-[95%] overflow-y-auto px-2 h-[calc(100vh-16rem)] "
                >
                    <div className="mb-5">
                        {messages.map((msg, index) => (
                            <Card
                                color="transparent"
                                shadow={false}
                                key={index}
                                className="overflow-hidden flex flex-column"
                            >
                                <div
                                    className={`c-chat-msg min-h-[.5rem] overflow-hidden inline-block flex flex-row max-w-full w-full ${
                                        msg.sender === "user"
                                            ? "flex-row-reverse text-right ml-auto my-4"
                                            : "text-left mr-auto"
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
                                        className={`c-bubble p-3 rounded-lg max-w-[85%] ${
                                            msg.sender === "user"
                                                ? "bg-customLightBlue text-white text-right ml-auto mt-[.1rem]"
                                                : "bg-white text-left mr-auto mt-[.1rem]"
                                        } break-words`}
                                    >
                                        {msg.sender === "user" ? (
                                            msg.text
                                        ) : (
                                            <>
                                                {msg.sender === "bot" ? (
                                                    <>
                                                        {isTyping &&
                                                        index ===
                                                            messages.length -
                                                                1 ? (
                                                            <div className="typing-indicator">
                                                                <span></span>
                                                                <span></span>
                                                                <span></span>
                                                            </div>
                                                        ) : (
                                                            <>
                                                                <MarkdownRenderer
                                                                    markdown={
                                                                        // markdown_content +
                                                                        msg.text
                                                                    }
                                                                />
                                                            </>
                                                        )}
                                                    </>
                                                ) : (
                                                    msg.text
                                                )}
                                            </>
                                        )}
                                    </CardBody>
                                </div>
                            </Card>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </Card>
                <form onSubmit={handleSendMessage} className="w-[95%] px-2">
                    <Card className="w-full flex flex-row justify-between p-2 bg-white">
                        <input
                            type="text"
                            ref={inputRef}
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            disabled={isInputDisabled} // Desactiva el input mientras el bot responde
                            placeholder="Escribe tu mensaje"
                            className="disabled:cursor-not-allowed placeholder:text-slate-400 px-4 py-2 outline-none rounded-lg w-[calc(100%-2.6rem)] font-outfit"
                        />
                        <Button
                            type="submit"
                            disabled={isInputDisabled} // Desactiva el botón mientras el bot responde
                            className="text-white bg-customLightBlue rounded-full p-2 pl-[0.65rem] shadow-lg w-[2.6rem] h-[2.6rem] flex align-center justify-center disabled:cursor-not-allowed"
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
