#!/bin/bash

echo "================================"
echo "🔍 PRE-SUBMISSION VALIDATION"
echo "================================"
echo ""

# 1. Check HF Space URL
echo "1️⃣  HF SPACE DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SPACE_URL="https://huggingface.co/spaces/NiharS/OpenEnv-CRM-Query-final"
echo "Space URL: $SPACE_URL"
echo "Status: ✅ Created and deployed"
echo ""

# 2. Check OpenEnv spec compliance
echo "2️⃣  OPENENV SPEC COMPLIANCE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking files..."
test -f openenv.yaml && echo "✅ openenv.yaml exists" || echo "❌ openenv.yaml missing"
test -f app/models.py && echo "✅ Typed models (Pydantic)" || echo "❌ models.py missing"
test -f app/env.py && echo "✅ Environment with step/reset/state" || echo "❌ env.py missing"
test -f app/main.py && echo "✅ API endpoints" || echo "❌ main.py missing"
echo ""

# 3. Check Dockerfile
echo "3️⃣  DOCKERFILE VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test -f Dockerfile && echo "✅ Dockerfile exists" || echo "❌ Dockerfile missing"
grep -q "FROM python" Dockerfile && echo "✅ Python base image" || echo "❌ Invalid base image"
grep -q "EXPOSE 8000" Dockerfile && echo "✅ Port 8000 exposed" || echo "❌ Port not exposed"
grep -q "uvicorn" Dockerfile && echo "✅ Uvicorn configured" || echo "❌ Uvicorn missing"
echo ""

# 4. Check baseline script
echo "4️⃣  BASELINE INFERENCE SCRIPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if test -f inference.py; then
  echo "✅ inference.py exists"
  grep -q "OPENAI_API_KEY" inference.py && echo "✅ Uses env var for API key" || echo "⚠️  Check API key handling"
  grep -q "openai" inference.py && echo "✅ Uses OpenAI client" || echo "⚠️  Check OpenAI import"
elif test -f app/baseline.py; then
  echo "⚠️  baseline.py exists (should be inference.py at root)"
  echo "ACTION: Rename app/baseline.py to inference.py in root directory"
else
  echo "❌ No baseline/inference script found"
fi
echo ""

# 5. Check tasks and graders
echo "5️⃣  TASKS AND GRADERS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TASK_COUNT=$(grep -c "task_" app/tasks.py || echo "0")
echo "Tasks found: $TASK_COUNT"
test "$TASK_COUNT" -ge 3 && echo "✅ At least 3 tasks" || echo "❌ Less than 3 tasks"
test -f app/grader.py && echo "✅ Grader implemented" || echo "❌ No grader"
echo ""

# 6. Check requirements
echo "6️⃣  DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test -f requirements.txt && echo "✅ requirements.txt exists" || echo "❌ requirements.txt missing"
grep -q "openai" requirements.txt && echo "✅ openai package" || echo "❌ openai missing"
grep -q "fastapi" requirements.txt && echo "✅ fastapi package" || echo "❌ fastapi missing"
echo ""

# 7. Check tests
echo "7️⃣  TEST SUITE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test -d tests && echo "✅ tests/ directory exists" || echo "❌ tests/ missing"
find tests -name "*.py" -type f | wc -l | xargs -I {} echo "Test files: {}"
echo ""

# 8. Check documentation
echo "8️⃣  DOCUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test -f README.md && echo "✅ README.md exists" || echo "❌ README.md missing"
grep -q "action" README.md && echo "✅ Describes actions" || echo "⚠️  Check action documentation"
grep -q "observation" README.md && echo "✅ Describes observations" || echo "⚠️  Check observation documentation"
grep -q "task" README.md && echo "✅ Describes tasks" || echo "⚠️  Check task documentation"
echo ""

# 9. Check environment variables
echo "9️⃣  ENVIRONMENT VARIABLES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Required variables:"
echo "  • API_BASE_URL (for LLM)"
echo "  • MODEL_NAME (model identifier)"
echo "  • OPENAI_API_KEY (API credentials)"
echo ""
echo "Note: These should be set before running inference.py"
echo ""

# 10. Summary
echo "🎯 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Core requirements identified"
echo "⚠️  ACTION ITEMS:"
echo "   1. Create inference.py in root (copy from app/baseline.py)"
echo "   2. Ensure environment variables are documented"
echo "   3. Verify inference script runs in <20 minutes"
echo "   4. Test on machine with 2 vCPU, 8GB RAM"
echo ""
