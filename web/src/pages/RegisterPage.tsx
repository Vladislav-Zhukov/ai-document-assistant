import { useState } from "react";
import { api } from "../api/client";

export function RegisterPage() {
  const [email, setEmail] = useState("newuser@example.com");
  const [password, setPassword] = useState("12345678");
  const [message, setMessage] = useState("");

  async function handleRegister() {
    try {
      await api.post("/auth/register", {
        email,
        password,
      });

      setMessage("Registered successfully. Now you can login.");
    } catch {
      setMessage("Registration failed");
    }
  }

  return (
    <div>
      <h1>Register</h1>

      <input value={email} onChange={(e) => setEmail(e.target.value)} />

      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
      />

      <button onClick={handleRegister}>Register</button>

      <p>{message}</p>
    </div>
  );
}