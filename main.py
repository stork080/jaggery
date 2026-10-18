from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict

app = FastAPI(title="Analytics Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

API_KEY = "ak_m8n2p4ixaej3mcwv90bpfpn8"
STUDENT_EMAIL = "25f2004578@ds.study.iitm.ac.in"


@app.post("/analytics")
async def analytics(request: Request):
    # 1. Auth FIRST — before any body parsing
    key = request.headers.get("x-api-key")
    if not key or key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    # 2. Parse body
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON"})

    events = body.get("events", []) if isinstance(body, dict) else []
    if not isinstance(events, list):
        events = []

    # 3. Aggregate
    total_events = len(events)
    unique_users = set()
    revenue = 0.0
    user_totals: Dict[str, float] = {}

    for e in events:
        if not isinstance(e, dict):
            continue
        user = e.get("user")
        amount = e.get("amount", 0)
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0.0

        if user is not None:
            unique_users.add(user)

        if amount > 0:
            revenue += amount
            if user is not None:
                user_totals[user] = user_totals.get(user, 0.0) + amount

    revenue = round(revenue, 2)
    top_user = max(user_totals, key=user_totals.get) if user_totals else ""

    return {
        "email": STUDENT_EMAIL,
        "total_events": total_events,
        "unique_users": len(unique_users),
        "revenue": revenue,
        "top_user": top_user,
    }


@app.get("/")
async def root():
    return {"status": "ok"}
