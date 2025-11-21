#!/usr/bin/env python3

import re

# Read the file
with open(
    "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/src/api/routes/agents.py",
    "r",
) as f:
    content = f.read()

# Pattern to find the process calls
pattern = r"(        # Initialize \w+ agent\n        (\w+) = \w+Agent\(\)\n\n        )(# Process request\n        result = await \2\.process\(\n            message=request\.query, context=context, \*\*request\.options\n        \))"

# Replacement with proper AgentMessage creation
replacement = r"""\1# Create proper AgentMessage
        agent_message = AgentMessage(
            sender="api",
            recipient="\2",
            action="analyze",
            payload={
                "query": request.query,
                "data": request.options.get("data", {}),
                **request.options
            },
            context=request.context
        )

        # Process request with proper message object
        result = await \2.process(
            message=agent_message, context=context
        )"""

# Apply the replacement
content = re.sub(pattern, replacement, content)

# Special handling for agents that use "investigate" action instead of "analyze"
agents_with_investigate = [
    "zumbi",
    "obaluaie",
]  # Agents that investigate anomalies/corruption

for agent_name in agents_with_investigate:
    content = content.replace(
        f'recipient="{agent_name}",\n            action="analyze",',
        f'recipient="{agent_name}",\n            action="investigate",',
    )

# Write back the file
with open(
    "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/src/api/routes/agents.py",
    "w",
) as f:
    f.write(content)

print("Fixed all 16 agent endpoints!")
