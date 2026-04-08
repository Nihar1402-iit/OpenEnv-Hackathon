# ⚡ COMMAND REFERENCE - COPY & PASTE

## Verify Everything Works (Copy & Paste)

```bash
#!/bin/bash
cd "/Users/niharshah/Desktop/Meta Hackathon" && \
echo "🔍 Checking Docker image..." && \
docker images | grep openenv-crm && \
echo "✅ Image found!" && \
echo "" && \
echo "🚀 Testing container..." && \
CID=$(docker run -d -p 7860:7860 -e HF_TOKEN=test openenv-crm:latest 2>/dev/null) && \
sleep 3 && \
echo "" && \
echo "📍 Health Check:" && \
curl -s http://localhost:7860/health && \
echo "" && \
echo "" && \
echo "📊 Grader Endpoint (Cold Start):" && \
curl -s -X POST http://localhost:7860/grader \
  -H "Content-Type: application/json" \
  -d '{}' | jq . && \
echo "" && \
docker stop $CID >/dev/null 2>&1 && \
echo "✅ All tests passed - Ready to submit!"
```

## Quick Submit Process

**Step 1: Visit Portal**
```
Meta PyTorch Hackathon → https://openenv.org/hackathon
```

**Step 2: Resubmit**
- Click "Resubmit" or "New Submission"
- Select "Docker Image" type
- Image: `openenv-crm:latest`
- Description: "Fixed Phase 2: Grader endpoint + logging"

**Step 3: Monitor**
- Check back in 10-15 minutes
- Expected: Phase 2 Validation PASSED ✅

## Key Information

**Docker Image**
```bash
# Image name
openenv-crm:latest

# Size
661MB (661 MB), 159MB (compressed)

# ID
931db5257de5
```

**Container Endpoints**
```bash
# Health check
GET http://localhost:7860/health

# Grader (cold start)
POST http://localhost:7860/grader
Body: {}

# Main app
GET http://localhost:7860/
```

## Test Script (Run This)

```bash
#!/bin/bash

echo "Starting container..."
docker run -d -p 7860:7860 -e HF_TOKEN=test openenv-crm:latest > /tmp/container.txt
CID=$(cat /tmp/container.txt)

echo "Waiting for startup..."
sleep 5

echo ""
echo "=== GRADER ENDPOINT TEST ==="
curl -s -X POST http://localhost:7860/grader \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool

echo ""
echo "Stopping container..."
docker stop $CID

echo "✅ Complete!"
```

## Troubleshooting

**If container won't start:**
```bash
# Check logs
docker run --rm -e HF_TOKEN=test openenv-crm:latest
```

**If port 7860 is in use:**
```bash
# Kill process on port 7860
lsof -i :7860 | grep -v PID | awk '{print $2}' | xargs kill -9
```

**If Docker image not found:**
```bash
# Rebuild image
cd "/Users/niharshah/Desktop/Meta Hackathon"
docker build -t openenv-crm:latest .
```

## Expected Output

**Grader Response (Should see 0.01 scores):**
```json
{
  "scores": {
    "task_easy_001": 0.01,
    "task_medium_001": 0.01,
    "task_hard_001": 0.01,
    "task_extreme_001": 0.01
  }
}
```

## Git Commands

**Check latest commit:**
```bash
cd "/Users/niharshah/Desktop/Meta Hackathon"
git log -1 --oneline
```

**Expected output:**
```
0bd0c6b ✨ FINAL - All complete and ready to submit
```

**Push latest changes:**
```bash
git add -A
git commit -m "Ready to resubmit"
git push origin main
```

## Quick Status Check

```bash
cd "/Users/niharshah/Desktop/Meta Hackathon"

# Show image
echo "=== DOCKER IMAGE ==="
docker images openenv-crm:latest

# Show graders available
echo -e "\n=== GRADERS AVAILABLE ==="
python3 -c "from app.graders import GRADERS; print(f'✅ {len(GRADERS)} graders: {list(GRADERS.keys())}')"

# Show recent git commits
echo -e "\n=== RECENT COMMITS ==="
git log --oneline -5
```

## One-Liner Commands

**Run all tests:**
```bash
cd "/Users/niharshah/Desktop/Meta Hackathon" && python3 FINAL_VERIFICATION.py && python3 FINAL_JUDGE_SIMULATOR.py
```

**Check graders:**
```bash
python3 -c "from app.graders import GRADERS; print('✅ GRADERS:', {k: GRADERS[k]({}) for k in GRADERS})"
```

**Verify image:**
```bash
docker inspect openenv-crm:latest | grep -E "Id|Size"
```

## Remember

- ✅ Image name: `openenv-crm:latest` (exact)
- ✅ Port: 7860 (HF Spaces standard)
- ✅ 4 graders must be found
- ✅ All scores in (0.001, 0.999)
- ✅ Cold start must work
- ✅ No exceptions allowed

---

**You're ready! Submit now and check back in 10 minutes for Phase 2 results.** 🚀
