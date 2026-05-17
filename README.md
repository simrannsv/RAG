# IPL GraphRAG Benchmark — TigerGraph Hackathon

A 3-pipeline RAG benchmark system built on 1M tokens of IPL cricket data.

## Pipelines
- **LLM-Only** — Groq LLaMA 3.3 70B answering from memory, no retrieval
- **Basic RAG** — FAISS vector search + Groq LLaMA 3.3 70B
- **GraphRAG** — TigerGraph hybrid search (vector + graph traversal) + Groq LLaMA 3.3 70B

## Dataset
1M tokens of IPL cricket data scraped from Wikipedia covering players, 
teams, seasons, auctions, venues, records and team owners.

## Evaluation
20 questions across single-hop and multi-hop categories evaluated on:
- Answer accuracy
- Latency (seconds/query)
- Token usage

## Stack
- TigerGraph Savanna (graph + vector DB)
- Groq LLaMA 3.3 70B (completion)
- Google GenAI embeddings
- Python + httpx + LangChain + FAISS
- Streamlit (dashboard)

## Hackathon
Built for the TigerGraph GraphRAG Inference Hackathon 2026.
#GraphRAGInferenceHackathon
