# Alfred Performance Baseline

This document captures the baseline performance of Alfred before the final engineering hardening pass (but after the initial sqlite optimizations).

## Resources
- **Backend RSS (Memory):** ~43.91 MB
- **Backend VMS:** ~31.62 MB

## Database
- **Journal Mode:** `wal`
- *Note: Database was empty during baseline capture so specific query metrics were not captured. Wait, actually I will need to seed the database to get real query metrics.*

## AI Inference (Ollama - qwen3:4b)
- **First Inference (Coldish):** 4.21s
  - Prompt Eval: 340ms
  - Gen Eval: 3.47s
- **Warm Inferences (5 iterations):** 
  - p50: 5.24s
  - Max: 5.36s

## Queue Architecture (Pre-optimization)
- **Queue type:** Memory-backed (`asyncio.Queue`)
- **Persistence:** None. Jobs are lost on crash.
- **Concurrency:** 1 worker

*Note: These baseline numbers will be compared with the final metrics after the final engineering pass.*
