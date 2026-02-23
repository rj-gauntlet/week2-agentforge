# Deploy AgentForge API & Smoke Test

Get a **public URL** so the app satisfies the MVP “deployed and publicly accessible” requirement.

---

## 1. Deploy to Railway (recommended)

1. **Push your code to GitHub** (if not already):
   - Repo should include `main.py`, `agent/`, `requirements.txt`, `Procfile`, and `data/`.

2. **Go to [railway.app](https://railway.app)** and sign in (e.g. with GitHub).

3. **New project → Deploy from GitHub repo**  
   - Select your `week2-agentforge` (or `week2-agentforce`) repo.  
   - Railway will detect Python and use the `Procfile`.

4. **Set environment variables**  
   In the project → your service → **Variables**:
   - `OPENAI_API_KEY` = your OpenAI API key  
   (or `ANTHROPIC_API_KEY` if you use Claude.)

5. **Generate a public URL**  
   - **Settings** → **Networking** → **Generate domain**.  
   - You’ll get a URL like `https://week2-agentforge-production-xxxx.up.railway.app`.

6. **Deploy**  
   - Railway builds and runs `Procfile`: `uvicorn main:app --host 0.0.0.0 --port $PORT`.  
   - Wait until the deployment is live (logs show “Uvicorn running”).

---

## 2. Smoke test (after deploy)

From your machine (no venv needed for this script; it uses the standard library):

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py https://YOUR-RAILWAY-URL.up.railway.app
```

Replace `YOUR-RAILWAY-URL` with the domain Railway gave you (no trailing slash).

**Example:**
```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py https://week2-agentforge-production-abc123.up.railway.app
```

You should see:
```
Smoke testing: https://...
  GET /health  OK
  POST /chat   OK (got reply)
Smoke test PASSED
```

**Test local first:**
```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py http://localhost:8000
```

(Start the API locally first with `.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000`.)

---

## 3. Other platforms

- **Render:** New Web Service → connect repo → Build: `pip install -r requirements.txt`, Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`. Add `OPENAI_API_KEY` in Environment.
- **Modal:** Use a Modal web endpoint that runs `main:app`; set API key in Modal secrets.
- **Vercel:** Use a Python serverless runtime or a single serverless function that runs the app; less straightforward for long-running LLM calls.

The **Procfile** in the repo is for Railway; other platforms use their own config (e.g. Render dashboard, `modal deploy`).

---

## 4. After smoke test passes

- Add the **public URL** to your README and submission.
- Mark **Deployed & public** and **Smoke test** done in [ROADMAP.md](./ROADMAP.md) and [STATUS.md](./STATUS.md).
