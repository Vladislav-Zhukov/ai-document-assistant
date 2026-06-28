# 🤖 AI Document Assistant

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-purple)
![MinIO](https://img.shields.io/badge/MinIO-S3-orange)
![Gemini](https://img.shields.io/badge/LLM-Gemini-yellow)

AI Document Assistant is a Retrieval-Augmented Generation (RAG) application that allows users to upload documents, automatically process them, generate embeddings, search through document content, ask questions, and receive AI-powered answers.

The project demonstrates a modern AI Backend architecture using FastAPI, PostgreSQL, Redis, MinIO, Qdrant and Gemini.

---

# Features

## Authentication

- JWT Authentication
- Access & Refresh Tokens
- User registration
- User login

---

## Document Management

- Upload PDF, DOCX and TXT files
- Delete documents
- Document metadata
- Automatic background processing
- Processing status tracking

---

## AI Features

- Automatic text extraction
- Document chunking
- Embedding generation
- Vector search using Qdrant
- Retrieval-Augmented Generation (RAG)
- AI document summarization
- Ask questions across uploaded documents

---

## Infrastructure

- Docker Compose
- PostgreSQL
- Redis
- MinIO (S3 Storage)
- Qdrant Vector Database
- RQ Worker

---

# Architecture

```
                React + TypeScript
                        │
                    HTTP API
                        │
                  FastAPI Backend
                        │
     ┌──────────────┬───────────────┬─────────────┐
     │              │               │             │
 PostgreSQL      Redis          MinIO         Qdrant
     │              │               │             │
 Users        Rate Limit       Documents     Embeddings
 Chats         Cache             Files       Vector Search
 Messages
```

---

# RAG Pipeline

```
User uploads document
        │
        ▼
Save file to MinIO
        │
        ▼
Extract text
        │
        ▼
Split into chunks
        │
        ▼
Generate embeddings
        │
        ▼
Store embeddings in Qdrant
```

Question flow

```
User Question
      │
      ▼
Generate embedding
      │
      ▼
Qdrant similarity search
      │
      ▼
Relevant chunks
      │
      ▼
Gemini
      │
      ▼
Final Answer
```

---

# Technology Stack

## Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2

## Database

- PostgreSQL

## Cache

- Redis

## Object Storage

- MinIO

## Vector Database

- Qdrant

## AI

- Gemini
- Sentence Transformers
- Embeddings
- Retrieval-Augmented Generation (RAG)

## Frontend

- React
- TypeScript
- Axios

## Background Jobs

- Redis Queue (RQ)

## DevOps

- Docker
- Docker Compose

---

# Project Structure

```
app/
│
├── api/
├── core/
├── models/
├── repositories/
├── schemas/
├── services/
├── workers/
│
web/
│
├── src/
│
alembic/
│
docker-compose.yml
```

---

# Main API

## Authentication

```
POST /auth/register
POST /auth/login
```

## Documents

```
POST   /documents/upload
GET    /documents
DELETE /documents/{id}
POST   /documents/{id}/summary
POST   /documents/ask
```

---

# AI Workflow

```
Upload Document
        │
        ▼
Worker extracts text
        │
        ▼
Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Qdrant
        │
        ▼
Ready
```

Question Answering

```
Question
      │
      ▼
Embedding
      │
      ▼
Vector Search
      │
      ▼
Gemini
      │
      ▼
Answer
```

---

# Running

```bash
docker compose up --build
```

Frontend

```
http://localhost:5173
```

Backend

```
http://localhost:8000/docs
```

MinIO

```
http://localhost:9001
```

Qdrant

```
http://localhost:6333/dashboard
```

---

# Future Improvements

- SSE document status updates
- Multi-document chat
- OCR support
- Image understanding
- Multi-language support
- Hybrid Search (BM25 + Vector Search)

---

# What I Learned

This project helped me gain practical experience with:

- Building REST APIs using FastAPI
- JWT Authentication
- SQLAlchemy Async ORM
- Alembic migrations
- Docker Compose
- PostgreSQL
- Redis
- Background workers (RQ)
- MinIO object storage
- Qdrant Vector Database
- Sentence Transformers
- Embedding generation
- Retrieval-Augmented Generation (RAG)
- Gemini API integration
- React + TypeScript frontend
- Polling for frontend synchronization

---

# Screenshots

> Login

(Add screenshot)

> Upload Documents

(Add screenshot)

> AI Summary

(Add screenshot)

> Ask Documents

(Add screenshot)

---

# License

MIT
