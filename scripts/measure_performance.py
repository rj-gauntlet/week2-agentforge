import os
import sys
import time
import json
from statistics import mean

# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from agent.orchestrator import run_agent

def measure_latency():
    print("Measuring agent latency...\n")
    
    # 1. Single-tool queries
    single_tool_queries = [
        "What are the possible causes of a severe headache?",
        "Is CPT 99213 covered by plan Aetna-123?",
        "Check drug interactions for aspirin and ibuprofen."
    ]
    
    print("--- Single-tool Queries (<5s target) ---")
    single_latencies = []
    for q in single_tool_queries:
        start_time = time.time()
        res = run_agent(q)
        end_time = time.time()
        latency = end_time - start_time
        single_latencies.append(latency)
        
        # Count tools used
        tool_count = 0
        for m in res.get("messages", []):
            if hasattr(m, "tool_calls") and m.tool_calls:
                tool_count += len(m.tool_calls)
                
        print(f"Query: '{q}'")
        print(f"Latency: {latency:.2f}s | Tools used: {tool_count}")
        if latency > 5:
            print(f"  [!] Failed target <5s")
        print("-" * 40)
        
    print(f"Average Single-tool Latency: {mean(single_latencies):.2f}s\n")
    
    # 2. Multi-step queries
    multi_step_queries = [
        "I need a cardiologist in New York. Can you also check their availability next week?",
        "Check the CPT code for a routine checkup and tell me if it's covered under my plan BlueCross-456.",
        "A patient is taking amoxicillin and warfarin. They also have a mild fever. Are there any interactions, and what might cause the fever?"
    ]
    
    print("--- Multi-step Queries (<15s target) ---")
    multi_latencies = []
    for q in multi_step_queries:
        start_time = time.time()
        res = run_agent(q)
        end_time = time.time()
        latency = end_time - start_time
        multi_latencies.append(latency)
        
        # Count tools used
        tool_count = 0
        for m in res.get("messages", []):
            if hasattr(m, "tool_calls") and m.tool_calls:
                tool_count += len(m.tool_calls)
                
        print(f"Query: '{q}'")
        print(f"Latency: {latency:.2f}s | Tools used: {tool_count}")
        if latency > 15:
            print(f"  [!] Failed target <15s")
        print("-" * 40)
        
    print(f"Average Multi-step Latency: {mean(multi_latencies):.2f}s\n")

if __name__ == "__main__":
    measure_latency()
