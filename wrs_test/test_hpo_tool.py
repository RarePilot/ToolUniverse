# 1. Create tool environment
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()  # Load all tools

# 2. Query scientific databases
# Calling get_HPO_ID_by_phenotype with all parameters
result = tu.run({
    "name": "get_HPO_ID_by_phenotype",
    "arguments": {
        "query": "hypertension",
        "limit": 5,
        "offset": 0
    }
})

print(result)