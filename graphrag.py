import httpx
import time
import json

GRAPHRAG_URL = "http://localhost:8000"
USERNAME = "tigergraph"
PASSWORD = "tigergraph"
GRAPH_NAME = "IPL"

questions = [
    "Who won the first IPL in 2008?",
    "Which team has won the most IPL titles?",
    "Who has scored the most runs in IPL history?",
    "Who has taken the most wickets in IPL history?",
    "Which player has hit the most sixes in IPL?",
    "Which players have played for both Mumbai Indians and Chennai Super Kings?",
    "Which captains have won the IPL more than once?",
    "Which players won both the Orange Cap and were in the winning team the same year?",
    "Which venues have hosted more than 3 IPL finals?",
    "Which overseas players have played under both MS Dhoni and Rohit Sharma?",
    "Which players were part of both the 2008 and 2014 IPL winning teams?",
    "Which coaches have worked with more than one IPL franchise?",
    "Which players have won both IPL and ICC World Cup in the same year?",
    "Which teams have had the same captain for more than 5 seasons?",
    "Which players were retained across the 2021 and 2022 mega auction?",
    "What connection exists between Suresh Raina and MS Dhoni across IPL seasons?",
    "How are Jasprit Bumrah and Rohit Sharma connected across tournaments?",
    "Which players have been bought at the highest price in multiple different auctions?",
    "Which franchise owners have connections to Bollywood?",
    "Which players have represented more than 5 different IPL teams?"
]

results = []

for i, question in enumerate(questions):
    print(f"\nQ{i+1}: {question}")

    start = time.time()

    try:
        response = httpx.get(
            f"{GRAPHRAG_URL}/ui/{GRAPH_NAME}/query",
            auth=(USERNAME, PASSWORD),
            json={
                "query": question,
                "method": "hybrid"
            },
            timeout=120
        )

        latency = round(time.time() - start, 2)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Raw response: {str(data)[:300]}")
            answer = data.get("response", data.get("answer", data.get("result", str(data))))
        else:
            answer = f"Error {response.status_code}: {response.text[:200]}"

    except Exception as e:
        latency = round(time.time() - start, 2)
        answer = f"Exception: {str(e)[:200]}"

    print(f"Answer: {answer[:200]}...")
    print(f"Latency: {latency}s")

    results.append({
        "question": question,
        "pipeline": "GraphRAG",
        "answer": answer,
        "latency": latency,
        "tokens": 0
    })

    time.sleep(3)

with open("results_graphrag.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✓ Done! Results saved to results_graphrag.json")
