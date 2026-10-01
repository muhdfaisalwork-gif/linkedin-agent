#!/usr/bin/env python3
"""
Simple launcher for the GitHub SEO Agent FastAPI server.
"""
import uvicorn

if __name__ == "__main__":
    print(r"""
╔══════════════════════════════════════════════╗
║   GitHub SEO Agent — Open Source Studio      ║
║   Dashboard: http://localhost:8500           ║
╚══════════════════════════════════════════════╝
    """)
    uvicorn.run("api.server:app", host="127.0.0.1", port=8500, reload=True)
