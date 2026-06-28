export type DocumentRead = {
  id: number;
  filename: string;
  content_type: string;
  storage_path: string;
  status: string;
  created_at: string;

  pages_count?: number | null;
  words_count?: number | null;
  chunks_count?: number | null;
  language?: string | null;

  document_type?: string | null;
  document_type_confidence?: number | null;
};