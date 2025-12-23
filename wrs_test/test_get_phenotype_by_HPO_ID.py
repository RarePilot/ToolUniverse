# 1. Create tool environment
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()  # Load all tools

# 2. Query scientific databases
result = tu.run({
    "name": "get_phenotype_by_HPO_ID",
    "arguments": {"id": "HP:0000822"}  # Hypertension
})

print(result)