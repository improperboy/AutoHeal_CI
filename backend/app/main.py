from fastapi import FastAPI
from app.api.run_agent import router as run_agent_router
from fastapi.responses import HTMLResponse



app = FastAPI(
    title="AutoHeal CI",
    description="Autonomous CI/CD Healing Agent",
    version="1.0.0"
)

app.include_router(run_agent_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AutoHeal CI</title>
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f172a, #1e293b);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: white;
            }

            .card {
                background: #111827;
                padding: 50px;
                border-radius: 16px;
                width: 420px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            }

            h1 {
                margin-bottom: 10px;
                font-size: 28px;
            }

            p {
                color: #9ca3af;
                margin-bottom: 30px;
            }

            a {
                display: inline-block;
                padding: 12px 24px;
                background: #3b82f6;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: 0.2s ease;
            }

            a:hover {
                background: #2563eb;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AutoHeal CI Agent</h1>
            <p>Autonomous CI Failure Detection & Repair System</p>
            <a href="/docs">Launch Demo</a>
        </div>
    </body>
    </html>
    """


@app.get("/")
def health_check():
    return {"status": "ok"}
