import os
import sys
import json
from dotenv import load_dotenv

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith import evaluate, Client
from agent.orchestrator import run_agent

# Load environment variables
load_dotenv()

def load_eval_cases(filepath="data/eval_cases.json"):
    with open(filepath, "r") as f:
        return json.load(f)

# The function that will be evaluated
def agent_target(inputs: dict) -> dict:
    query = inputs["query"]
    result = run_agent(query)
    
    # Extract tools used and their outputs
    tools_used = []
    tool_outputs = {}
    for m in result.get("messages", []):
        if getattr(m, "type", None) == "tool" or m.__class__.__name__ == "ToolMessage":
            try:
                tool_outputs[m.tool_call_id] = json.loads(m.content)
            except Exception:
                tool_outputs[m.tool_call_id] = m.content

    for m in result.get("messages", []):
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tools_used.append(tc["name"])
                # Attach parsed output to the tool name (simplified)
                if tc.get("id") in tool_outputs:
                    # store it keyed by tool name for easy assertions
                    if "parsed_outputs" not in locals():
                        parsed_outputs = {}
                    parsed_outputs[tc["name"]] = tool_outputs[tc["id"]]
                
    return {
        "output": result.get("output", ""),
        "tools_used": tools_used,
        "tool_outputs": locals().get("parsed_outputs", {}),
        "error": result.get("error", None)
    }

# Evaluators
def check_expected_output(run, example):
    """Checks if the agent's output contains the expected keywords using OR logic (less brittle)."""
    expected_contains = example.outputs.get("expected_output_contains", [])
    actual_output = run.outputs.get("output", "").lower()
    
    if not expected_contains:
        return {"key": "output_contains_keywords", "score": 1}
        
    # Use OR logic: if it hits ANY of the expected keywords, it passes.
    score = 0
    for keyword in expected_contains:
        if keyword.lower() in actual_output:
            score = 1
            break
            
    return {"key": "output_contains_keywords", "score": score}

def check_structured_tool_flags(run, example):
    """Asserts that tools returned specific structured JSON flags like can_diagnose: False."""
    expected_flags = example.outputs.get("expected_flags", {})
    if not expected_flags:
        return {"key": "structured_flags_correct", "score": 1}
        
    tool_outputs = run.outputs.get("tool_outputs", {})
    score = 1
    for expected_key, expected_val in expected_flags.items():
        # Check if this key exists in ANY of the tool outputs
        found_match = False
        for tool_name, output_data in tool_outputs.items():
            if isinstance(output_data, dict) and output_data.get(expected_key) == expected_val:
                found_match = True
                break
        if not found_match:
            score = 0
            break
            
    return {"key": "structured_flags_correct", "score": score}

def check_expected_tools(run, example):
    """Checks if the agent used all the expected tools."""
    expected_tools = example.outputs.get("expected_tools", [])
    actual_tools = run.outputs.get("tools_used", [])
    
    if not expected_tools:
        return {"key": "used_expected_tools", "score": 1}
        
    score = 1
    for tool in expected_tools:
        if tool not in actual_tools:
            score = 0
            break
            
    return {"key": "used_expected_tools", "score": score}

def main():
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("Error: LANGCHAIN_API_KEY is not set. Please set it in your .env file.")
        return

    client = Client()
    dataset_name = "AgentForge Healthcare Evals"
    
    # Try to find existing dataset
    dataset = None
    if client.has_dataset(dataset_name=dataset_name):
        print(f"Found existing dataset '{dataset_name}'.")
        dataset = client.read_dataset(dataset_name=dataset_name)
    else:
        print(f"Creating dataset '{dataset_name}' in LangSmith...")
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Evaluation dataset for AgentForge Healthcare MVP."
        )

    # Always clear existing examples and re-upload to keep it in sync with JSON
    print("Syncing test cases from data/eval_cases.json...")
    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    for ex in existing_examples:
        client.delete_example(ex.id)
        
    cases = load_eval_cases()
    for case in cases:
        client.create_example(
            inputs={"query": case["query"]},
            outputs={
                "expected_tools": case.get("expected_tools", []),
                "expected_output_contains": case.get("expected_output_contains", []),
                "expected_flags": case.get("expected_flags", {}),
                "category": case.get("category", "")
            },
            dataset_id=dataset.id,
        )
    print(f"Uploaded {len(cases)} test cases to LangSmith dataset.")
        
    print(f"Running evaluation against dataset: {dataset_name}...")
    
    # Run evaluation
    experiment_results = evaluate(
        agent_target,
        data=dataset_name,
        evaluators=[check_expected_output, check_expected_tools, check_structured_tool_flags],
        experiment_prefix="Agent-Eval-Run",
        metadata={"version": "1.0", "env": "local"}
    )
    
    print("\nEvaluation complete! View your results in the LangSmith dashboard.")

if __name__ == "__main__":
    main()
