# 🍽️ Restaurant‑Review QA Agent

A LangGraph‑powered AI agent that answers user questions about a restaurant by combining **structured facts** (menu, address, hours, etc.) with **reviews**. Currently, this repo uses the yelp reviews that are publicly available. It automatically decides whether a query can be solved with general information alone or needs to mine the review corpus, then runs a **parallel map‑reduce pipeline** to surface the most relevant opinions.

---

## ✨ Key Features

**Smart routing** : Classifies each user utterance to decide between the *Info* path and the *Review* path.

**Parallel review mining** : Fan‑out reviews in LangGraph map‑reduce cycle (concurrency‑safe).

**Relevance + Recency ranking** : Filters out off‑topic reviews, then scores remaining ones with a weighted blend of relevance and freshness.

**Top‑k evidence** : Streams only the best *k* snippets into the answer synthesis step—keeps token costs predictable.

**Graceful fallback** : Clearly apologises when the knowledge base lacks the requested information.

**Modular graph** : Each logical step is its own node; swap in new models or heuristics without touching the rest.

---

## 🌐 High‑Level Flow

```text
                ┌──────────────┐
  User Query →──►  Classifier   ├───► Info Node ───► Answer
                └──────┬───────┘
                       ▼
                 Review Path
                       ▼
                ┌──────────────┐
                │  Splitter    │   fan‑out (map)
                └──────┬───────┘
         ┌──────────────┴──────────────┐
         │  Review Worker 1 … N        │   parallel LLM calls
         └──────────────┬──────────────┘
                       ▼   fan‑in (reduce)
                ┌──────────────┐
                │ Filter +     │
                │ Ranker       │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ Answer Node  │
                └──────────────┘
```

---

## 🛠️ Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # langgraph, openai, pydantic, python‑dotenv …
```

Set the tokens in the token.json file:

```text
OPENAI_API_KEY="sk‑…"
```

---

## 🚀 Quick Start

```bash
python main.py
```

The script will launch a REPL (Read-Evaluate-Print-Loop); type natural‑language questions such as:

* "Do they have vegan mains?"
* "Is parking tricky on weekends?"
* "How noisy does it get after 8 p.m.?"

---

## ⚙️ Configuration

| Flag / Env          | Description                                | Default |
| -------------       | ------------------------------------------ | ------- |
| `top_k`             | Top‑k reviews to feed into the answer node | `20`    |
| `alpha`             | Weight for relevance vs recency (`0‑1`)    | `0.9`   |
|`freshness_threshold`| Recency half‑life in days                  | `30`    |
| `max_workers`       | Maximum parallel review workers            | `2`     |

---

## 🧩 Extending

* Add more restaurant data. Try to integrate with APIs to get reviews.
* Enable a way to filter out irrelevant, non-restaurant queries
* Use reflection pattern to evaluate if the LLM follows the stated guidelines.

---

## 📝 License

MIT – see `LICENSE` for details.

---

*Built with ❤️ and [LangGraph](https://github.com/langgraph/langgraph).*
