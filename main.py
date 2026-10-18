from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Analytics Service")

# ---------------------------------------------------------------
# CORS — required for the browser grader
# ---------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

# ---------------------------------------------------------------
# Assigned values
# ---------------------------------------------------------------
API_KEY = "ak_m8n2p4ixaej3mcwv90bpfpn8"
STUDENT_EMAIL = "25f2004578@ds.study.iitm.ac.in"


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


# ---------------------------------------------------------------
# POST /analytics
# ---------------------------------------------------------------
@app.post("/analytics")
async def analytics(payload: AnalyticsRequest, request: Request):
    # Auth check
    key = request.headers.get("x-api-key")
    if not key or key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    events = payload.events

    total_events = len(events)
    unique_users = len({e.user for e in events})

    revenue = 0.0
    user_totals: Dict[str, float] = {}

    for e in events:
        if e.amount > 0:
            revenue += e.amount
            user_totals[e.user] = user_totals.get(e.user, 0.0) + e.amount

    revenue = round(revenue, 2)

    top_user = ""
    if user_totals:
        top_user = max(user_totals, key=user_totals.get)

    return {
        "email": STUDENT_EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }


@app.get("/")
async def root():
    return {"status": "ok"}
