# 1. Create tool environment
from tooluniverse import ToolUniverse

tu = ToolUniverse()
tu.load_tools()  # Load all tools

# 2. Query scientific databases
result = tu.run({
    "name": "get_joint_associated_diseases_by_HPO_ID_list",
    "arguments": {
        "HPO_ID_list": ["HP:0000822", "HP:0001250"],  # Hypertension, Seizures
        "limit": 5,
        "offset": 0
    }
})

print(result)