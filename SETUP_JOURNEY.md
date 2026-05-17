# GraphRAG + TigerGraph Setup: A Journey Through Errors & Fixes

## Overview
Setting up GraphRAG with TigerGraph on Windows + WSL2 + Docker + local Ollama was challenging but educational. This blog documents the major pitfalls we hit and how we solved them.

---

## 🔴 Error 1: TigerGraph Docker Image Stuck on `docker load` (4+ hours)

**The Problem:**
```bash
docker load -i tigergraph-4.2.2-community-docker-image.tar.gz
```
This command stalled indefinitely on a 2.22GB tar.gz file. After 12+ hours, it hadn't completed, and we couldn't tell if it was actually running or frozen.

**Why It Happened:**
- Large file operations over OneDrive-mounted paths are unreliable in WSL2
- `docker load` doesn't give real-time progress feedback
- No timeout or error indication means you can't tell if it's dead or just slow

**The Fix:**
Replaced the tar load with a direct Docker pull:
```bash
docker pull tigergraph/community:4.2.2
```

**Lesson Learned:**
On Windows + WSL2, always prefer `docker pull` over `docker load`. It's faster, gives progress feedback, and handles networking better. Only use `docker load` if you absolutely need a pre-built offline image.

**Time Saved:** ~12 hours → 5 minutes

---

## 🔴 Error 2: `http://localhost` Refused Connection

**The Problem:**
```
curl: (7) Failed to connect to localhost port 80: Connection refused
```

After `setup_graphrag.sh` completed and Docker containers were up, the web UI still wasn't accessible.

**Why It Happened:**
- Nginx container started but immediately exited because the upstream GraphRAG services weren't fully ready yet
- The compose start order didn't account for GraphRAG's boot time

**The Fix:**
Manually restart the nginx container after waiting for GraphRAG to be healthy:
```bash
docker compose -f graphrag/docker-compose.yml up -d
# Wait ~30 seconds for services to boot
docker compose -f graphrag/docker-compose.yml restart nginx
```

**Verification:**
```bash
curl -I http://localhost
# Now returns: HTTP/1.1 200 OK
```

**Lesson Learned:**
Docker compose `depends_on` doesn't guarantee service readiness — it only waits for container startup. For dependent services, always add a small delay and verify health before restarting reverse proxies.

---

## 🔴 Error 3: GraphRAG Login Returns 500 Error

**The Problem:**
```
POST /api/auth/login → 500 Internal Server Error
```

Login screen appeared, but any credentials returned a server error.

**Why It Happened:**
- We tried username `Simss` (our Windows username)
- TigerGraph default credentials are `tigergraph` / `tigergraph`
- Auth mismatch → 500 error

**The Fix:**
Use the correct TigerGraph default credentials:
```
Username: tigergraph
Password: tigergraph
```

**Lesson Learned:**
Always check the official docs for default credentials. Container services rarely use system usernames—they come with hardcoded defaults that you must use first, then optionally change later.

---

## 🔴 Error 4: Groq Multimodal & Gemini Embedding Test Failures

**The Problem:**
GraphRAG UI's "Test" button for LLM models showed:
- ❌ Groq embedding: "Not supported"
- ❌ Groq multimodal: "Vision input not supported"
- ❌ Gemini embedding: Invalid API key / model mismatch errors

**Why It Happened:**
- Groq is a text-only LLM; it doesn't support vision/images
- Google Gemini API requires a valid `GOOGLE_API_KEY` environment variable
- Different Gemini endpoints have different capability levels

**The Fix:**
Split the providers by capability:
- **Embeddings** → Ollama (`nomic-embed-text`) — no API key needed, local, reliable
- **Completion** → Groq (`llama-3.3-70b-versatile`) — fast, text-only
- **Multimodal** → Google Gemini (`gemini-2.5-flash`) — with valid `GOOGLE_API_KEY`

**Config Update:**
```json
{
  "embedding_service": {
    "embedding_model_service": "ollama",
    "base_url": "http://host.docker.internal:11434",
    "model_name": "nomic-embed-text",
    "dimensions": 768
  },
  "completion_service": {
    "llm_service": "groq",
    "llm_model": "llama-3.3-70b-versatile"
  },
  "multimodal_service": {
    "llm_service": "genai",
    "llm_model": "gemini-2.5-flash"
  }
}
```

**Lesson Learned:**
Not all LLM providers support all capabilities. Know your provider limitations:
- Groq = fast completion only
- Gemini = multimodal, but needs API key
- Ollama = local, no API key, reliable for embeddings

---

## 🔴 Error 5: WSL Python Virtual Environment Creation Failed

**The Problem:**
```bash
python3 -m venv ~/ipl-env
# Error: The virtual environment was not created successfully because ensurepip is not available
```

Ubuntu 26.04's system Python has `ensurepip` disabled by policy.

**Why It Happened:**
- Ubuntu's Python package disables `ensurepip` for security reasons
- The default `venv` module depends on `ensurepip`
- OneDrive-mounted paths (NTFS in WSL) have permission issues with Python virtual environments

**The Fix:**
Install `virtualenv` as an alternative and create the env in WSL home:
```bash
sudo apt-get update
sudo apt-get install -y virtualenv
virtualenv ~/ipl-env
source ~/ipl-env/bin/activate
```

**Lesson Learned:**
- When `venv` fails on WSL Ubuntu, use `virtualenv` package instead
- Always create virtual environments in native WSL storage (`~/`), never on NTFS mounts like OneDrive
- This solves permission issues and symlink problems

---

## 🔴 Error 6: `fetch_ipl.py` File Not Found

**The Problem:**
```bash
# From inside graphrag/ folder:
python3 fetch_ipl.py
# python3: can't open file '/mnt/c/Users/Simss/OneDrive/Desktop/RAG/graphrag/fetch_ipl.py': [Errno 2] No such file or directory
```

**Why It Happened:**
- `fetch_ipl.py` is at `/mnt/c/Users/Simss/OneDrive/Desktop/RAG/fetch_ipl.py`
- We were in the `graphrag/` subfolder trying to run it
- Script wasn't duplicated inside the subfolder

**The Fix:**
Run from the correct directory:
```bash
cd /mnt/c/Users/Simss/OneDrive/Desktop/RAG
python3 fetch_ipl.py
```

**Lesson Learned:**
Always check your working directory before running scripts. Use absolute paths or `../` to reference files outside your current folder. Consider adding a `__main__` check and path resolution to Python scripts to make them more portable.

---

## 🔴 Error 7: Ollama Model Download Failed (Network Error)

**The Problem:**
```
ollama pull nomic-embed-text
# Error: max retries exceeded: Get "https://dd20bb891979d25aebc...r2.cloudflaragestorage.com/..." - dial tcp: lookup dd20bb891979d25aebc...r2.cloudflaragestorage.com: no such host
```

Download hit 25% and failed with DNS resolution error.

**Why It Happened:**
- Network connectivity issue to Cloudflare blob storage
- Possibly DNS resolution timeout or ISP blocking

**The Fix:**
Retry the pull:
```bash
ollama pull nomic-embed-text
```

If it persists, restart Ollama:
```bash
Stop-Process -Name ollama -Force
ollama serve  # Runs in foreground; let it stabilize, then Ctrl+C and restart
```

**Lesson Learned:**
Large model downloads are vulnerable to network glitches. Build in retry logic for production pipelines. Monitor download progress and set reasonable timeouts. For critical models, consider hosting locally or using a CDN with better availability.

---

## ✅ Final Stack (What Works)

| Component | Service | Config |
|-----------|---------|--------|
| **Database** | TigerGraph 4.2.2 | `tigergraph` / `tigergraph` credentials |
| **UI** | GraphRAG UI | `http://localhost` (nginx → port 3000) |
| **Chat History** | Go backend | `http://chat-history:8002` |
| **Embeddings** | Ollama | `nomic-embed-text` @ `http://host.docker.internal:11434` |
| **Completion** | Groq | `llama-3.3-70b-versatile` (needs `GROQ_API_KEY`) |
| **Multimodal** | Google Gemini | `gemini-2.5-flash` (needs `GOOGLE_API_KEY`) |
| **Graph Extraction** | GraphRAG ECC | `http://graphrag-ecc:8001` |

---

## 🎯 Key Takeaways

1. **Docker on Windows + WSL2 is finicky**: Prefer `docker pull` over `docker load`. Use native WSL storage, not NTFS mounts.

2. **Service orchestration needs health checks**: Don't rely on `depends_on`. Add manual waits and retries.

3. **Know your provider limits**: Not all LLMs are equal. Read capability matrices before designing architecture.

4. **Python virtual environments on WSL**: Use `virtualenv` in WSL home, never on OneDrive/NTFS.

5. **Network resilience matters**: Large downloads fail. Build retries and monitoring into your setup.

6. **Default credentials are your friend**: Always try hardcoded defaults before debugging auth logic.

---

## 🚀 Next Steps

With this setup working, you can now:
- Ingest IPL data via `fetch_ipl.py`
- Build RAG pipelines on top of TigerGraph
- Query with multi-model LLM support
- Use the GraphRAG UI to test and debug

Good luck with your hackathon! 🎉
