import { useState } from "react";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { ChatPage } from "./pages/ChatPage";

function App() {
  const [page, setPage] = useState<"login" | "register" | "documents" | "chat">(
    localStorage.getItem("access_token") ? "documents" : "login"
  );

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setPage("login");
  }

  return (
    <div>
      <nav>
        <button onClick={() => setPage("login")}>Login</button>
        <button onClick={() => setPage("register")}>Register</button>
        <button onClick={() => setPage("documents")}>Documents</button>
        <button onClick={() => setPage("chat")}>Chat</button>
        <button onClick={logout}>Logout</button>
      </nav>

      {page === "login" && <LoginPage onLogin={() => setPage("documents")} />}
      {page === "register" && <RegisterPage />}
      {page === "documents" && <DocumentsPage />}
      {page === "chat" && <ChatPage />}
    </div>
  );
}

export default App;