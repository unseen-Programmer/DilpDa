import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import App from "./App";
import { store } from "./store/store";
import "./styles/index.css";

createRoot(document.getElementById("app")!).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            className: "dilpda-toast",
            duration: 3200,
          }}
        />
      </BrowserRouter>
    </Provider>
  </StrictMode>,
);
