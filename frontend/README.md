# React, Vite, Material tailwind y Markdoc

--- 

## 🔄 Flujo de Trabajo

1️⃣ **Inicio de sesión** → Validación de usuarios con `users.json`.  
2️⃣ **Carga del chatbot** → Se inicializa la sesión.  
3️⃣ **Inicio de conversación** → Se obtiene el primer mensaje del bot (`startSession`).  
4️⃣ **Envío de mensajes** → Comunicación con el backend (`chat()`).  
5️⃣ **Renderizado Markdown** → Se formatean las respuestas con `MarkdownRenderer.jsx`.  
6️⃣ **Gestión del historial** → Guardado y recuperación de chats (`Sidebar.jsx`).  
7️⃣ **Salida del usuario** → Cierre de sesión y almacenamiento en `LocalStorage`.  

---

## 📌 Características Destacadas

✅ **Autenticación segura** con Context API.  
✅ **Rutas protegidas** con React Router.  
✅ **Markdown enriquecido** para mejor presentación de respuestas.  
✅ **Experiencia rápida y fluida** gracias a Vite.  
🚀 **Aplicación escalable, modular y optimizada.**  

---

## 🏗️ Estructura General
La aplicación sigue una **arquitectura modular y escalable**, utilizando diferentes componentes y tecnologías:

-  **Frontend con React.js**: Desarrollo de la interfaz de usuario.
-  **Vite**: Herramienta de construcción y servidor de desarrollo rápido.
-  **React Router**: Manejo de rutas y protección de páginas mediante autenticación.
-  **React Context API**: Gestión del estado de autenticación.
-  **Axios**: Comunicación con la API del backend.
-  **Markdoc**: Procesamiento y renderizado de contenido Markdown en el chatbot.
-  **Material Tailwind**: Mejora de la interfaz con estilos modernos y componentes UI.
-  **LocalStorage**: Almacenamiento de sesión del usuario.

---

## 🌟 Tecnologías Clave y Beneficios

| **Tecnología**        | **Uso en el Proyecto**                                | **Beneficio** |
|----------------------|----------------------------------------------------|--------------|
| **Vite**          | Bundler y servidor de desarrollo                   | 🚀 Rápida recarga en caliente y compilación. |
| **React.js**      | Construcción de la UI con componentes reutilizables | 🔹 Desarrollo modular y eficiente. |
| **React Router**  | Navegación y rutas protegidas                      | 🔒 Seguridad y control de acceso. |
| **Context API**   | Gestión del estado de autenticación                 | 🔄 Estado global sin necesidad de Redux. |
| **Axios**         | Peticiones HTTP al backend                          | ⚡ Comunicación eficiente con la API. |
| **Markdoc**       | Procesamiento de Markdown                          | 📝 Respuestas enriquecidas en el chat. |
| **Material Tailwind** | Componentes estilizados                           | 🎨 Diseño moderno y adaptable. |
| **LocalStorage**  | Almacenamiento de sesión                           | 🛠️ Persistencia de usuario sin recargar la página. |

---

## 🛠️ Detalles del proyecto

### **A) Autenticación de Usuarios**

📌 **Archivos clave**: `AuthContext.jsx`, `users.json`, `Home.jsx`

#### **Página de Inicio (`Home.jsx`)**
- Los usuarios ingresan su email y contraseña.
- Se valida contra `users.json` en `AuthContext.jsx`.
- Si los datos son correctos, se **almacena la sesión en LocalStorage**.
- Se redirige a la página del **chatbot**.

#### **Usuarios registrados en `users.json`**
```json
[
    {
        "email": "admin@ayming.com",
        "password": "admin",
        "userId": "user_admin",
        "name": "María Rosa Cuenca"
    }
]
```


### **B) Rutas y Protección de Páginas**

📌 **Archivo clave**: `Router.jsx`

Se utiliza **React Router** para manejar las rutas de la aplicación:

- **`/`** → Página de Login
- **`/chatbot`** → Página protegida con autenticación

🔒 **Si el usuario no está autenticado, es redirigido automáticamente al login.**

```jsx
const ProtectedRoute = ({ element }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? element : <Navigate to="/" replace />;
};
```

### **C) Estructura de la Aplicación y Navegación**
📌 **Archivo clave**: `Layout.jsx`

Se usa un **layout general** que contiene un **Footer** y un **Outlet** para renderizar las páginas dinámicamente.

```jsx
const Layout = () => {
  return (
    <>         
      <Outlet/> 
      <Footer/>
    </>
  )
}
```

---

### **D) Chatbot y Manejo de Conversaciones**
📌 **Archivos clave**: `Chatbot.jsx`, `Chat.jsx`, `Sidebar.jsx`

#### **Inicio de Conversación (`startSession()`)**
- Al iniciar sesión, se llama al backend para **crear una nueva sesión**.
- Se recibe el primer mensaje del bot.

#### **Envío de Mensajes (`Chat.jsx`)**
- Los mensajes se envían al servidor a través de `chat(userId, inputMessage)`.
- Se actualiza la conversación en tiempo real.

#### **Historial de Conversaciones (`Sidebar.jsx`)**
- Se listan las conversaciones anteriores del usuario (`getUserConversations()`).
- Se pueden recuperar mensajes previos (`getChatHistory()`).

#### **Guardar y Limpiar Chat**
- El usuario puede limpiar la conversación con `clearChat()`, guardando antes si lo desea.

---

### **E) Renderizado de Markdown con Markdoc**
📌 **Archivo clave**: `MarkdownRenderer.jsx`

El chatbot puede mostrar **respuestas formateadas en Markdown**, incluyendo:

✅ **Texto enriquecido**: negritas, títulos, listas.  
✅ **Tablas**: Formateo de datos estructurados.  
✅ **Callouts**: Mensajes destacados (`info`, `warning`, `error`).  
✅ **Detalles interactivos**: Secciones plegables con más información.

#### **Ejemplo de Markdoc en el chat**
```markdown
{% details summary="Ver más información" %}
Aquí hay contenido oculto que se muestra cuando haces clic.
{% /details %}
```

➡️ Mejora la experiencia de usuario al mostrar respuestas estructuradas y fáciles de leer.

---

## 🔄 Resumen del Funcionamiento

📌 **Inicio de sesión** → 📌 **Carga del chatbot** → 📌 **Inicio de conversación**  
📌 **Envío de mensajes** → 📌 **Procesamiento en backend** → 📌 **Renderizado con Markdown**  
📌 **Gestión del historial** → 📌 **Salida de usuario y almacenamiento de sesión**  

✔ **Autenticación segura con Context API y React Router.**  
✔ **Interfaz rápida y modular gracias a React y Vite.**  
✔ **Mensajes enriquecidos con Markdoc para una mejor experiencia de usuario.**  
✔ **Sistema de historial y almacenamiento de conversaciones en el backend.**  

---
