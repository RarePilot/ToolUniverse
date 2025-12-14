# 1. Create tool environment
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()  # Load all 600+ tools

# 2. Query scientific databases
result = tu.run({
    "name": "OpenTargets_get_associated_targets_by_disease_efoId",
    "arguments": {"efoId": "EFO_0000537"}  # hypertension
})

print(result)