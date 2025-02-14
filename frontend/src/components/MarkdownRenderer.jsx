import React from "react";
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
  return (
      <details className="my-5 p-2 border border-gray-300 rounded-md">
          <summary className="cursor-pointer font-semibold">{summary}</summary>
          <div className="mt-2">{children}</div>
      </details>
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
