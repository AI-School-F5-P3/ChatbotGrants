import React, { useRef, useEffect } from "react";
import Markdoc from "@markdoc/markdoc";
import {
    Card,
    CardBody,
    CardHeader,
    Table as MTTable,
} from "@material-tailwind/react";

// Definición del tag personalizado Callout
const callout = {
    render: "Callout",
    attributes: {
        type: {
            type: String,
            default: "note",
            matches: ["note", "info", "warning", "error"],
        },
    },
};

// Componente Callout
const Callout = ({ type = "note", children }) => {
    const styles = {
        note: "bg-gray-100 border-gray-500",
        info: "bg-blue-50 border-blue-500",
        warning: "bg-yellow-50 border-yellow-500",
        error: "bg-red-50 border-red-500",
    };

    return (
        <div className={`p-4 my-4 border-l-4 rounded-r ${styles[type]}`}>
            {children}
        </div>
    );
};

// Definición del tag personalizado Details
const details = {
    render: "Details",
    attributes: {
        summary: { type: String },
    },
};

// Componente Details
const Details = ({ summary, children }) => {
    const detailsRef = useRef(null);

    useEffect(() => {
        const details = detailsRef.current;

        const handleToggle = () => {
            setTimeout(() => {
                if (details.open) {
                    // Si se abre, desplazamos el elemento a la parte superior
                    details.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                    });
                } else {
                    // Si se cierra, desplazamos la vista a la parte inferior
                    requestAnimationFrame(() => {
                        const rect = details.getBoundingClientRect();
                        const bottomOffset = rect.bottom + window.scrollY;
                        const viewportHeight = window.innerHeight;
                        const maxScroll =
                            document.documentElement.scrollHeight -
                            viewportHeight;

                        if (bottomOffset > maxScroll) {
                            // Si el elemento está cerca del final de la página, llevamos el scroll al máximo
                            window.scrollTo({
                                top: maxScroll,
                                behavior: "smooth",
                            });
                        } else {
                            // Si hay espacio suficiente, desplazamos el scroll hasta la parte inferior del elemento
                            window.scrollBy({
                                top: rect.height,
                                behavior: "smooth",
                            });
                        }
                    });
                }
            }, 100);
        };

        details.addEventListener("toggle", handleToggle);
        return () => details.removeEventListener("toggle", handleToggle);
    }, []);

    return (
        <>
            <details
                ref={detailsRef}
                className="my-5 p-2 border border-gray-300 rounded-md"
            >
                <summary className="cursor-pointer font-semibold">
                    {summary}
                </summary>
                <div className="mt-6">{children}</div>
            </details>
        </>
    );
};

const MarkdownRenderer = ({ markdown }) => {
    // Configuración de Markdoc
    const config = {
        tags: {
            callout,
            details,
        },
    };

    // Parsear el contenido markdown
    const ast = Markdoc.parse(markdown);
    const content = Markdoc.transform(ast, config);

    // Crear el objeto de componentes disponibles
    const components = {
        Callout,
        Details,
    };

    return <>{Markdoc.renderers.react(content, React, { components })}</>;
};

export default MarkdownRenderer;
