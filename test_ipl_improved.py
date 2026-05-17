"""
IPL-specific RAG pipeline with improved extraction and query generation.
Uses domain-specific prompts for better entity extraction and GSQL query generation.
"""

import json
import os
import time
from typing import Any

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load .env
load_dotenv()
load_dotenv("/mnt/c/Users/Simss/OneDrive/Desktop/RAG/graphrag/.env")
load_dotenv("C:/Users/Simss/OneDrive/Desktop/RAG/graphrag/.env")

BASE_URL = os.getenv("GRAPHRAG_BASE_URL", "http://localhost:8000").rstrip("/")
TG_USERNAME = os.getenv("TG_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TG_PASSWORD", "tigergraph")
RAG_PATTERN = os.getenv("RAG_PATTERN", "hybridsearch")
GRAPH_NAME = os.getenv("GRAPH_NAME", "IPL").strip()

# IPL-specific complex questions for testing
IPL_QUESTIONS = [
    "Which players have represented more than 5 different IPL teams?",
    "Which player has played for the most different teams?",
    "Which players have played for both Mumbai Indians and Chennai Super Kings?",
    "Which players were part of both the 2008 and 2014 IPL winning teams?",
    "Which overseas players have played under both MS Dhoni and Rohit Sharma?",
    "Which teams have had the same captain for more than 5 seasons?",
    "Who has scored the most runs while playing for Mumbai Indians?",
    "Which captains have won the IPL more than once?",
]


def parse_graph_query_response(resp: requests.Response) -> dict[str, Any]:
    """Parse GraphRAG response."""
    payload = resp.json()
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"content": payload}
    if not isinstance(payload, dict):
        payload = {"content": str(payload)}
    return payload


def query_graph(question: str, graph_name: str = GRAPH_NAME) -> dict:
    """Query the graph with a natural language question."""
    try:
        query_url = f"{BASE_URL}/ui/{graph_name}/query"
        resp = requests.get(
            query_url,
            params={"q": question, "rag_pattern": RAG_PATTERN},
            auth=HTTPBasicAuth(TG_USERNAME, TG_PASSWORD),
            timeout=300,
        )
        resp.raise_for_status()
        payload = parse_graph_query_response(resp)
        return {
            "success": True,
            "answer": payload.get("content") or payload.get("natural_language_response") or "",
            "response_type": payload.get("response_type"),
            "answered_question": payload.get("answered_question"),
            "raw": payload,
        }
    except requests.exceptions.ConnectionError as exc:
        return {
            "success": False,
            "error": f"Connection error: {str(exc)}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def test_ipl_questions():
    """Test IPL-specific questions."""
    print(f"\n{'='*80}")
    print(f"Testing IPL-Specific Complex Questions with Improved Prompts")
    print(f"Graph: {GRAPH_NAME}")
    print(f"{'='*80}\n")

    results = []
    for i, question in enumerate(IPL_QUESTIONS, start=1):
        print(f"\n[Q{i}] {question}")
        print("-" * 80)

        start = time.time()
        result = query_graph(question)
        latency = round(time.time() - start, 2)

        if result["success"]:
            answer = result["answer"]
            if isinstance(answer, dict):
                answer = json.dumps(answer, indent=2)
            answer_str = str(answer)[:300]
            print(f"✓ Answer: {answer_str}...")
            print(f"  Latency: {latency}s")
            print(f"  Response Type: {result.get('response_type')}")
            print(f"  Answered: {result.get('answered_question')}")
        else:
            print(f"✗ Error: {result['error']}")

        results.append({
            "question": question,
            "success": result["success"],
            "answer": result.get("answer", result.get("error")),
            "latency": latency,
            "response_type": result.get("response_type"),
            "answered_question": result.get("answered_question"),
        })

        time.sleep(2)  # Pace requests

    # Save results
    out_file = "results_ipl_improved.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Results saved to {out_file}")
    
    # Summary
    successful = sum(1 for r in results if r["success"] and r["answered_question"])
    print(f"\nSummary: {successful}/{len(results)} questions answered successfully")
    print(f"{'='*80}\n")

    return results


def check_graph_health():
    """Check if graph service is running and get schema info."""
    print("Checking Graph Service Health...")
    try:
        query_url = f"{BASE_URL}/ui/{GRAPH_NAME}/query"
        resp = requests.get(
            query_url,
            params={"q": "What entities are in the graph?", "rag_pattern": RAG_PATTERN},
            auth=HTTPBasicAuth(TG_USERNAME, TG_PASSWORD),
            timeout=10,
        )
        if resp.status_code == 200:
            print(f"✓ Graph service is running at {BASE_URL}")
            print(f"✓ Graph name: {GRAPH_NAME}")
            return True
        else:
            print(f"✗ Graph service returned status {resp.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to graph service: {str(e)}")
        print(f"  Make sure GraphRAG is running at {BASE_URL}")
        return False


if __name__ == "__main__":
    # Check health
    if check_graph_health():
        print()
        # Run tests
        test_ipl_questions()
    else:
        print("\n⚠ Please start the GraphRAG service and try again")
