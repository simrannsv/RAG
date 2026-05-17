import os
import time
import json
import httpx

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def groq_chat(messages):
    response = httpx.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Authorization': 'Bearer ' + GROQ_API_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'model': 'llama-3.3-70b-versatile',
            'messages': messages
        },
        timeout=60
    )
    data = response.json()
    return data['choices'][0]['message']['content'], data['usage']['total_tokens']

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

    answer, tokens_used = groq_chat([
        {"role": "system", "content": "You are an IPL cricket expert. Answer questions accurately and concisely."},
        {"role": "user", "content": question}
    ])

    latency = round(time.time() - start, 2)

    print(f"Answer: {answer[:200]}...")
    print(f"Latency: {latency}s | Tokens: {tokens_used}")

    results.append({
        "question": question,
        "pipeline": "LLM-Only",
        "answer": answer,
        "latency": latency,
        "tokens": tokens_used
    })

with open("results_llm_only.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✓ Done! Results saved to results_llm_only.json")
