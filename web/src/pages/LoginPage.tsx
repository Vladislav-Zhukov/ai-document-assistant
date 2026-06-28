import { useState } from "react";
import { api } from "../api/client";
import type { TokenResponse } from "../types/auth";

type LoginPageProps = {
  onLogin: () => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState("user@example.com");
  const [password, setPassword] = useState("12345678");
  const [message, setMessage] = useState("");

  async function handleLogin() {
    try {
      const response = await api.post<TokenResponse>("/auth/login", {
        email,
        password,
      });

      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      setMessage("Logged in successfully");
      onLogin();
    } catch {
      setMessage("Login failed");
    }
  }

  return (
    <div>
      <h1>Login</h1>

      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
      />

      <button onClick={handleLogin}>Login</button>

      <p>{message}</p>
    </div>
  );
}