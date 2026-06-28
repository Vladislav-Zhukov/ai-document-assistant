export type ChatRead = {
  id: number;
  user_id: number;
  document_id: number;
  title: string;
  created_at: string;
};

export type MessageRead = {
  id: number;
  chat_id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};