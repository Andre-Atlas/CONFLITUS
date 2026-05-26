import express from "express";
import path from "path";

const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Proxy all /api/* requests to FastAPI backend
  app.all("/api/*", async (req, res) => {
    try {
      const targetUrl = `${BACKEND_URL}${req.originalUrl}`;
      const fetchOptions: RequestInit = {
        method: req.method,
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
      };

      if (req.method !== "GET" && req.method !== "HEAD" && req.body) {
        fetchOptions.body = JSON.stringify(req.body);
      }

      const response = await fetch(targetUrl, fetchOptions);
      const contentType = response.headers.get("content-type");

      if (contentType?.includes("application/json")) {
        const data = await response.json();
        res.status(response.status).json(data);
      } else {
        const text = await response.text();
        res.status(response.status).send(text);
      }
    } catch (err) {
      console.error("[Proxy] Erro ao conectar ao backend Python:", err);
      res.status(502).json({
        error: "Backend Python não está disponível.",
        hint: "Inicie com: cd backend && python -m uvicorn app.main:app --reload --port 8000",
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const { createServer: createViteServer } = await import("vite");
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    // Static files in production
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[Frontend] Server running on http://localhost:${PORT}`);
    console.log(`[Frontend] Proxying /api/* → ${BACKEND_URL}`);
  });
}

startServer();
