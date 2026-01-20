# api/index.py - FIXED VERSION
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic model defined BEFORE usage
class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

# Load telemetry data (download sample bundle and place as telemetry.json in api/)
telemetry_data = {}
telemetry_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
if os.path.exists(telemetry_path):
    with open(telemetry_path, "r") as f:
        telemetry_data = json.load(f)
else:
    print("Warning: telemetry.json not found")

@app.post("/api/latency")
async def check_latency(request: LatencyRequest):
    results = {}
    
    for region in request.regions:
        region_data = telemetry_data.get(region, [])
        
        if not region_data:
            results[region] = {
                "avg_latency": 0.0,
                "p95_latency": 0.0,
                "avg_uptime": 100.0,
                "breaches": 0
            }
            continue
        
        latencies = [float(record.get("latency_ms", 0)) for record in region_data]
        latencies = [l for l in latencies if l > 0]
        
        if not latencies:
            results[region] = {
                "avg_latency": 0.0,
                "p95_latency": 0.0,
                "avg_uptime": 100.0,
                "breaches": 0
            }
            continue
        
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        breaches = sum(1 for l in latencies if l > request.threshold_ms)
        avg_uptime = 100.0 * (1 - (breaches / len(latencies)))
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": int(breaches)
        }
    
    return {"regions": results}

