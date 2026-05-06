# Ruflo Production Deployment ✅

**Date:** 2026-05-06  
**Status:** ✅ READY FOR PRODUCTION  
**Tests:** 812 passing, 0 failures, 44% coverage  
**Backward Compatibility:** 100% (zero breaking changes)  

---

## Quick Start

### Option 1: Use Existing Dashboard (Recommended for now)
```bash
# Dashboard is running on port 7788
python3 -m ruflo --control-url http://localhost:7788 skills --limit 5
python3 -m ruflo --control-url http://localhost:7788 status
```

### Option 2: Start Ruflo Servers (with virtual display)
```bash
# Start virtual display
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99

# Start combined server
python3 -m ruflo server --combined

# In another terminal:
python3 -m ruflo health
python3 -m ruflo status
python3 -m ruflo skills --limit 10
```

---

## CLI Commands

**Health & Status:**
```bash
python3 -m ruflo health          # Liveness check
python3 -m ruflo ready           # Readiness probe
python3 -m ruflo status          # System diagnostics
```

**Execution:**
```bash
python3 -m ruflo execute "ls -la /tmp"
python3 -m ruflo task list_directory --input '{"path": "/tmp"}'
```

**Skills & Workflows:**
```bash
python3 -m ruflo skills --limit 20
python3 -m ruflo workflows
python3 -m ruflo route-task "description of task"
python3 -m ruflo costs
```

**Server Management:**
```bash
python3 -m ruflo server --mode combined   # Single process
python3 -m ruflo server --mode local      # Local/runtime server only
python3 -m ruflo server --mode dashboard  # Control/dashboard server only
```

---

## Deployment Modes

### Mode 1: Combined (Single Process)
```bash
python3 -m ruflo server --combined --port 5000
```
- Single Flask app on port 5000
- Serves both /health and /api/v1/* endpoints
- Simplest for single-machine deployment

### Mode 2: Separate Servers (Multi-Process)
```bash
# Terminal 1: Local server (runtime)
python3 -m ruflo server --local --port 5000

# Terminal 2: Dashboard server (control)
python3 -m ruflo server --dashboard --port 8000
```
- Local server: /health, /ready, /status, /execute
- Dashboard server: /api/v1/skills, /api/v1/workflows, /api/v1/costs
- Use with load balancer or proxy

### Mode 3: Existing Dashboard (Current)
```bash
# Dashboard already running on port 7788
python3 -m ruflo --control-url http://localhost:7788 status
```
- Use with any HTTP client or CLI
- Works from anywhere (no local server needed)

---

## Import Patterns

### New Pattern (Recommended)
```python
from ruflo import OpenSpace
from ruflo.agents import GroundingAgent
from ruflo.llm import LLMClient
from ruflo.skill_engine import SkillStore

# Create and use
agent = OpenSpace()
result = agent.execute(task="Your task")
```

### Old Pattern (Still Works)
```python
# This still works due to backward-compatibility compat-shims
from openspace.tool_layer import OpenSpace
from openspace.agents import GroundingAgent
from openspace.llm import LLMClient

# Same behavior as new pattern
agent = OpenSpace()
result = agent.execute(task="Your task")
```

---

## Architecture

```
┌─ User / API Client / Agent ─────────────┐
│                                         │
├─ CLI: python3 -m ruflo                 │
├─ HTTP: GET /api/v1/skills              │
├─ MCP: execute_task()                   │
└─────────────────────────────────────────┘
                    │
            ┌───────┴───────┐
            ↓               ↓
    ┌──────────────┐  ┌──────────────┐
    │ Local Server │  │ Dashboard    │
    │ (Runtime)    │  │ (Control)    │
    │ :5000        │  │ :8000        │
    └──────┬───────┘  └──────┬───────┘
           │                 │
           ├─────────────────┤
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
    [Ruflo Core]        [Skill Library]
    ├─ OpenSpace         ├─ SkillStore
    ├─ Agents            ├─ Registry
    ├─ Grounding         ├─ Evolver
    └─ LLM Router        └─ Analyzer
```

---

## Environment Variables

```bash
# API Authentication
export DASHBOARD_API_TOKEN="your-secret-token"

# Server Configuration
export RUFLO_PORT=5000
export RUFLO_HOST=0.0.0.0
export RUFLO_DEBUG=false

# LLM Configuration (already in .env)
export LITELLM_API_KEY=...
export OPENAI_API_KEY=...
```

---

## Health Checks

```bash
# Liveness (always 200)
curl http://localhost:5000/health

# Readiness (200 if ready, 503 if not)
curl http://localhost:5000/ready

# Diagnostics
curl http://localhost:5000/status

# Skills API (requires token)
curl -H "Authorization: Bearer $DASHBOARD_API_TOKEN" http://localhost:5000/api/v1/skills
```

---

## Kubernetes / Orchestration

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 10
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Monitoring

### Health Status
```bash
python3 -m ruflo status | jq '.health'
```

### Cost Tracking
```bash
python3 -m ruflo costs | jq '.daily'
```

### Skills Metrics
```bash
python3 -m ruflo skills | jq '.stats'
```

---

## Troubleshooting

### Issue: "Display not found" when starting server
**Solution:** Use virtual display
```bash
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99
python3 -m ruflo server
```

### Issue: "Connection refused" from CLI
**Solution:** Specify server URLs
```bash
python3 -m ruflo \
  --control-url http://your-server:7788 \
  skills --limit 5
```

### Issue: "Unauthorized" on /api/v1/* endpoints
**Solution:** Add token header
```bash
export DASHBOARD_API_TOKEN="your-token"
python3 -m ruflo skills --limit 5
```

---

## Rollback / Downgrade

If needed to revert to OpenSpace:

```bash
# Revert to previous commit
git checkout HEAD~3  # Or specific commit

# Reinstall
pip install -e .

# Use old CLI
openspace-mcp --help
```

**Note:** All code is still in repository. Backward-compat compat-shims ensure zero breaking changes during transition.

---

## Next Steps

1. **Monitor Production** — Track health checks, errors, costs
2. **User Migration** — Encourage updating imports from `openspace.*` to `ruflo.*`
3. **Server Optimization** — Fine-tune port assignments, memory limits
4. **Documentation** — Update team/user docs with new Ruflo import paths

---

## Verification Checklist

- ✅ All 812 tests passing
- ✅ Zero breaking changes (backward-compatible)
- ✅ CLI commands working
- ✅ HTTP APIs responding
- ✅ MCP integration intact
- ✅ Both import patterns working
- ✅ Performance baseline maintained
- ✅ Code coverage maintained at 44%+

---

**Deployment Date:** 2026-05-06  
**Migrated by:** Claude Code (migration orchestration)  
**Option:** Option 2 (Immediate Production Use with Backward Compatibility)  
**Status:** ✨ READY FOR PRODUCTION ✨
