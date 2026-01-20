import json
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load sample data (in real use, you'd upload or fetch it)
with open("q-vercel-latency.json") as f:
    telemetry_data = json.load(f)

@app.post("/analytics")
async def analytics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold_ms = body["threshold_ms"]
    
    results = {}
    for region in regions:
        region_data = [r for r in telemetry_data if r.get("region") == region]
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for lat in latencies if lat > threshold_ms)
        }
    return results

@app.get("/")
def root():
    return {"message": "POST to /analytics with {'regions':[...], 'threshold_ms': 180}"}


