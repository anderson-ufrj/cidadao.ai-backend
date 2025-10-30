#!/bin/bash
# Script to check coverage of all agents individually

echo "======================================================================"
echo "🔍 CHECKING REAL COVERAGE OF ALL AGENTS"
echo "======================================================================"
echo ""

export JWT_SECRET_KEY=test
export SECRET_KEY=test

AGENTS=(
    "abaporu"
    "anita"
    "ayrton_senna"
    "bonifacio"
    "ceuci"
    "dandara"
    "drummond"
    "lampiao"
    "machado"
    "maria_quiteria"
    "nana"
    "obaluaie"
    "oscar_niemeyer"
    "oxossi"
    "tiradentes"
    "zumbi"
)

echo "Agent,Coverage,Statements,Missing,Tests" > /tmp/agents_coverage.csv

for agent in "${AGENTS[@]}"; do
    echo "----------------------------------------"
    echo "📊 Testing: $agent"
    echo "----------------------------------------"

    # Run tests for this agent
    output=$(venv/bin/pytest tests/unit/agents/test_${agent}*.py \
        --cov=src.agents.${agent} \
        --cov-report=term \
        -q 2>&1)

    # Extract coverage percentage
    coverage=$(echo "$output" | grep "src/agents/${agent}.py" | awk '{print $NF}' | sed 's/%//')
    statements=$(echo "$output" | grep "src/agents/${agent}.py" | awk '{print $2}')
    missing=$(echo "$output" | grep "src/agents/${agent}.py" | awk '{print $3}')
    tests=$(echo "$output" | grep "passed" | awk '{print $1}')

    if [ -z "$coverage" ]; then
        coverage="N/A"
        statements="N/A"
        missing="N/A"
        tests="0"
    fi

    echo "$agent,$coverage,$statements,$missing,$tests" >> /tmp/agents_coverage.csv

    echo "✅ Coverage: $coverage%"
    echo ""
done

echo "======================================================================"
echo "📊 SUMMARY REPORT"
echo "======================================================================"
echo ""

cat /tmp/agents_coverage.csv | column -t -s,

echo ""
echo "======================================================================"
echo "Report saved to: /tmp/agents_coverage.csv"
echo "======================================================================"
