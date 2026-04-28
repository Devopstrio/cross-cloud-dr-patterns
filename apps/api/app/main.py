import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pythonjsonlogger import jsonlogger

# Logger setup
logger = logging.getLogger("dr-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Cross-Cloud DR Patterns API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/patterns")
def get_patterns():
    return [
        {"id": "active-active", "name": "Active-Active Global", "tier": "Tier 0", "rto": "< 30s", "rpo": "0"},
        {"id": "warm-standby", "name": "Warm Standby", "tier": "Tier 1", "rto": "< 15m", "rpo": "< 5m"},
        {"id": "pilot-light", "name": "Pilot Light", "tier": "Tier 2", "rto": "< 2h", "rpo": "< 15m"}
    ]

@app.post("/failover/simulate")
def simulate_failover(pattern_id: str):
    logger.info(f"Simulating failover for pattern: {pattern_id}")
    return {
        "status": "Simulation Complete",
        "expected_rto": "4.2 minutes",
        "steps_automated": 12,
        "risks_identified": ["Latency spike during DNS propagation"]
    }

@app.get("/readiness/score")
def get_readiness_score():
    return {
        "global_readiness": 92.5,
        "azure_health": "Optimal",
        "aws_health": "Optimal",
        "replication_lag": "1.2s",
        "last_drill": "2026-04-25T10:00:00Z"
    }

@app.get("/dashboard/summary")
def get_dashboard_summary():
    return {
        "protected_workloads": 145,
        "active_dr_tier": "Tier 1",
        "last_failover_test": "Success",
        "data_durability": "99.999999999%"
    }
