import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ChatRead, MessageRead } from "../types/chat";
import type { DocumentRead } from "../types/document";

export function ChatPage() {
  const [documents, setDocuments] = useState<DocumentRead[]>([]);
  const [chats, setChats] = useState<ChatRead[]>([]);
  const [messages, setMessages] = useState<MessageRead[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
  const [content, setContent] = useState("");

  async function loadDocuments() {
    const response = await api.get<DocumentRead[]>("/documents");
    setDocuments(response.data.filter((doc) => doc.status === "ready"));
  }

  async function loadChats() {
    const response = await api.get<ChatRead[]>("/chats");
    setChats(response.data);
  }

  async function createChat() {
    if (!selectedDocumentId) return;

    const response = await api.post<ChatRead>("/chats", {
      document_id: selectedDocumentId,
      title: "Document chat",
    });

    setSelectedChatId(response.data.id);
    await loadChats();
  }

  async function loadMessages(chatId: number) {
    const response = await api.get<MessageRead[]>(`/chats/${chatId}/messages`);
    setMessages(response.data);
  }

  async function sendMessage() {
    if (!selectedChatId || !content.trim()) return;

    await api.post(`/chats/${selectedChatId}/messages`, {
      content,
    });

    setContent("");
    await loadMessages(selectedChatId);
  }

async function sendStreamingMessage() {
  if (!selectedChatId || !content.trim()) return;

  const token = localStorage.getItem("access_token");
  if (!token) return;

  const userText = content;
  setContent("");

  setMessages((prev) => [
    ...prev,
    {
      id: Date.now(),
      chat_id: selectedChatId,
      role: "user",
      content: userText,
      created_at: new Date().toISOString(),
    },
    {
      id: Date.now() + 1,
      chat_id: selectedChatId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    },
  ]);

  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/chats/${selectedChatId}/stream`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: userText }),
    }
  );

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) return;

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;

      const data = line.replace("data: ", "");

      if (data === "[DONE]") {
        await loadMessages(selectedChatId);
        return;
      }

      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];

        if (last && last.role === "assistant") {
          last.content += data;
        }

        return updated;
      });
    }
  }
}

  useEffect(() => {
    loadDocuments();
    loadChats();
  }, []);

  useEffect(() => {
    if (selectedChatId) {
      loadMessages(selectedChatId);
    }
  }, [selectedChatId]);

  return (
    <div>
      <h1>Chat</h1>

      <h3>Create chat</h3>

      <select
        value={selectedDocumentId ?? ""}
        onChange={(e) => setSelectedDocumentId(Number(e.target.value))}
      >
        <option value="">Select ready document</option>
        {documents.map((doc) => (
          <option key={doc.id} value={doc.id}>
            {doc.filename}
          </option>
        ))}
      </select>

      <button onClick={createChat}>Create chat</button>

      <h3>Your chats</h3>

      <ul>
        {chats.map((chat) => (
          <li key={chat.id}>
            <button onClick={() => setSelectedChatId(chat.id)}>
              Chat #{chat.id} — document #{chat.document_id}
            </button>
          </li>
        ))}
      </ul>

      <h3>Messages</h3>

      <div>
        {messages.map((message) => (
          <div key={message.id}>
            <strong>{message.role}:</strong> {message.content}
          </div>
        ))}
      </div>

      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Ask something about the document..."
      />

      <br />

      <button onClick={sendStreamingMessage}>Send Streaming</button>
    </div>
  );
}