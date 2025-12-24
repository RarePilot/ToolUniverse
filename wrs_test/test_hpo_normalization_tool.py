from tooluniverse import ToolUniverse
import json
import os
import multiprocessing

# mac上必须开启
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

tu = ToolUniverse()

queries = [
    "Bartonellosis",
    "Swollen lymph nodes",
    "Fever"
]

result = tu.run({
    "name": "hpo_normalization_tool",
    "arguments": {
        "queries": queries,
        "top_k": 3,
    }
})

print(result)
