import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./router/Router";
import { ThemeProvider } from "@material-tailwind/react";
import { AuthProvider } from "./context/AuthContext"; // ✅ Importa AuthProvider

import "./index.css";
import "./assets/styles/main.scss"; 

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>
);
