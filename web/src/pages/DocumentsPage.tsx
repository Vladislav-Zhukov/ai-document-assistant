import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { DocumentRead } from "../types/document";

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRead[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [summary, setSummary] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  async function loadDocuments() {
    console.log("Loading documents...");

    const response = await api.get<DocumentRead[]>("/documents");
    console.log(response.data);

    setDocuments(response.data);
  }

  async function uploadDocument() {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await api.post("/documents/upload", formData);

    setFile(null);
    setMessage("Document uploaded");
    await loadDocuments();
  }

  async function deleteDocument(id: number) {
    await api.delete(`/documents/${id}`);
    setMessage("Document deleted");
    await loadDocuments();
  }

  async function summarizeDocument(id: number) {
    setSummary("Loading summary...");

    try {
      const response = await api.post(`/documents/${id}/summary`);
      setSummary(response.data.summary);
    } catch {
      setSummary("Failed to generate summary");
    }
  }

  async function askAllDocuments() {
    if (!question.trim()) return;

    setAnswer("Thinking...");

    try {
      const response = await api.post("/documents/ask", {
        question,
      });

      setAnswer(response.data.answer);
    } catch {
      setAnswer("Failed to ask documents");
    }
  }

  useEffect(() => {
    loadDocuments().catch(() => setMessage("Failed to load documents"));
  }, []);

  useEffect(() => {
    const hasProcessing = documents.some(
      (doc) => String(doc.status).toLowerCase() === "processing"
    );

    console.log("hasProcessing:", hasProcessing);

    if (!hasProcessing) return;

    const intervalId = window.setInterval(() => {
      loadDocuments().catch(() => setMessage("Failed to refresh documents"));
    }, 3000);

    return () => window.clearInterval(intervalId);
  }, [documents]);

  return (
    <div>
      <h1>Documents</h1>

      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />

      <button onClick={uploadDocument}>Upload</button>

      <p>{message}</p>

      <ul>
        {documents.map((doc) => {
          const status = String(doc.status).toLowerCase();
          const isReady = status === "ready";
          const isProcessing = status === "processing";

          return (
            <li key={doc.id}>
              <strong>{doc.filename}</strong> —{" "}
              {isProcessing ? (
                <span>⏳ Processing...</span>
              ) : isReady ? (
                <span>✅ Ready</span>
              ) : (
                <span>{doc.status}</span>
              )}

              <br />
              Type: {doc.document_type ?? "unknown"}
              <br />
              Confidence: {doc.document_type_confidence ?? "-"}
              <br />
              Words: {doc.words_count ?? "-"} | Chunks:{" "}
              {doc.chunks_count ?? "-"}
              <br />

              <button onClick={() => deleteDocument(doc.id)}>Delete</button>

              <button
                onClick={() => summarizeDocument(doc.id)}
                disabled={!isReady}
              >
                Summary
              </button>
            </li>
          );
        })}
      </ul>

      <h3>Summary</h3>
      <p>{summary}</p>

      <hr />

      <h3>Ask all documents</h3>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask something across all documents..."
        rows={5}
        cols={80}
      />

      <br />

      <button onClick={askAllDocuments}>Ask</button>

      <h3>Answer</h3>
      <p>{answer}</p>
    </div>
  );
}