import { createBrowserRouter } from "react-router-dom";
import Layout from "../layout/Layout";
import Home from "../pages/Home";
import Chatbot from "../pages/Chatbot";

export const router = createBrowserRouter([{
  path: '/',
  element: <Layout />,
  children: [
      {
          index: true,
          element: <Home />
      },
      {
          path:'chatbot',
          element: <Chatbot />
      }
]
}])
