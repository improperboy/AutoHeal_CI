PROJECT TITLE

AutoHeal CI — Autonomous CI/CD Healing Agent

🏗️ HIGH-LEVEL ARCHITECTURE
User (React Dashboard)
        ↓
Backend API (FastAPI / Node)
        ↓
Orchestrator Agent (LangGraph / CrewAI)
        ↓
--------------------------------------------
| Repo Analyzer Agent                      |
| Test Discovery Agent                     |
| Failure Diagnosis Agent                  |
| Fix Generation Agent (LLM)               |
| Code Patch Agent                         |
| Git Agent (Branch + Commit + Push)       |
| CI Monitor Agent                         |
--------------------------------------------
        ↓
Docker Sandbox Runner
        ↓
CI/CD API (GitHub Actions)
        ↓
results.json
        ↓
React Dashboard (Visualization)

🧩 TECH STACK (WINNING COMBINATION)
🖥 FRONTEND (Mandatory React) 

PS3_CICD_Agent_AIML - Google Do…

Stack

React (Vite)

Tailwind CSS

Zustand (state management)

Axios

Recharts (score chart)

React Timeline component

Deployment

Vercel (Recommended)

Folder

/frontend

⚙️ BACKEND (Agent System)
🔹 Recommended Stack
Component	Technology
API Server	FastAPI (Python)
Agent Framework	LangGraph (best for multi-agent loops)
LLM	GPT-4 / Claude / Open-source (DeepSeek-Coder / CodeLlama)
Sandbox	Docker
Git Ops	GitPython
CI Monitor	GitHub REST API
Queue (optional)	Redis + Celery
Storage	PostgreSQL
Logs	JSON structured logs

Why Python?
Because AI + LangGraph + DevOps automation = easiest ecosystem.

🤖 MULTI-AGENT ARCHITECTURE (CRITICAL – 20 marks) 

PS3_CICD_Agent_AIML - Google Do…

You MUST show this clearly in your architecture diagram.

🧠 1️⃣ Orchestrator Agent (Brain)

Controls retry loop (default 5)

Calls agents in order

Stops when CI passes

Framework:

LangGraph (Stateful agent workflow)

📁 2️⃣ Repository Analyzer Agent

Tasks:

Clone repo

Detect language (Python, JS, Java)

Detect test framework:

pytest

unittest

jest

mocha

Parse project tree

Tools:

GitPython

OS walk

🧪 3️⃣ Test Discovery Agent

Find test files dynamically

DO NOT hardcode paths ❌ 

PS3_CICD_Agent_AIML - Google Do…

Example logic:

test_*.py
*_test.py
__tests__/

❌ 4️⃣ Failure Diagnosis Agent

Runs:

pytest --json-report


Extract:

file

line

error type

stack trace

Categorize strictly into required types 

PS3_CICD_Agent_AIML - Google Do…

Bug Types:

LINTING

SYNTAX

LOGIC

TYPE_ERROR

IMPORT

INDENTATION

You MUST map error messages to these exact labels.

🛠 5️⃣ Fix Generation Agent (LLM Powered)

Prompt Template:

You are an autonomous CI healing agent.

Error:
File: {file}
Line: {line}
Error Type: {type}
Stack Trace: {trace}

Return:
- Corrected code snippet
- Minimal patch
- No explanation


IMPORTANT:
Output must match exact test case format 

PS3_CICD_Agent_AIML - Google Do…

🧵 6️⃣ Patch Agent

Apply fix via diff patch

Validate syntax before commit

Libraries:

difflib

ast.parse (for Python)

🔀 7️⃣ Git Agent

Requirements from document 

PS3_CICD_Agent_AIML - Google Do…

:

Branch format:

TEAM_NAME_LEADER_NAME_AI_Fix


Rules:

UPPERCASE

Replace spaces with _

End with _AI_Fix

Push to new branch

Commit prefix: [AI-AGENT]

Example:

[AI-AGENT] Fix SYNTAX error in validator.py line 8


Use:

GitPython

GitHub token

🔄 8️⃣ CI Monitor Agent

Poll GitHub Actions API

Detect status

If failed → loop again

Stop when PASSED

Retry limit default = 5 

PS3_CICD_Agent_AIML - Google Do…

🐳 SANDBOX EXECUTION (MANDATORY)

Use Docker.

Why?

Prevent malicious repo execution

Isolate dependencies

Flow:

docker build temp image
docker run tests
capture logs
destroy container

📊 RESULTS.JSON STRUCTURE (MANDATORY) 

PS3_CICD_Agent_AIML - Google Do…

{
  "repository": "url",
  "team_name": "",
  "leader_name": "",
  "branch_name": "",
  "total_failures": 3,
  "fixes_applied": 3,
  "iterations": 2,
  "ci_status": "PASSED",
  "total_time": "4m 22s",
  "fixes": [
    {
      "file": "src/utils.py",
      "bug_type": "LINTING",
      "line": 15,
      "commit_message": "[AI-AGENT] Fix LINTING error",
      "status": "Fixed"
    }
  ]
}

📊 REACT DASHBOARD STRUCTURE
Pages
1️⃣ Home Page

Repo URL input

Team Name

Leader Name

Run Agent button

2️⃣ Dashboard Page

Sections required (from document) 

PS3_CICD_Agent_AIML - Google Do…

:

✅ Run Summary Card

Repo

Branch

Failures

CI Status Badge

Time

📈 Score Breakdown

Base: 100

Speed bonus

Commit penalty

Final Score

Use Recharts bar graph.

🛠 Fixes Table

Columns:

File

Bug Type

Line

Commit

Status

Color coding:

Green ✓

Red ✗

🕒 CI Timeline

Use:

Vertical timeline

Iteration 1 – FAIL

Iteration 2 – PASS

🧠 MODEL STRATEGY

You have 3 options:

🥇 Best Hackathon Strategy (Most Practical)

Use:

GPT-4 API (if allowed)

OR DeepSeek-Coder 33B (open-source)

Why?
Training your own model = impossible in hackathon timeframe.

🥈 Hybrid Strategy (Very Smart)

Use rule-based detection for:

Missing colon

Unused imports

Indentation

Use LLM only for logic bugs.

This makes:

Faster

More accurate

Less token cost

🔐 SECURITY

Token stored in environment variables

No pushing to main branch ❌ 

PS3_CICD_Agent_AIML - Google Do…

Validate branch naming strictly

📂 COMPLETE PROJECT STRUCTURE
/autoheal-ci
│
├── /frontend
│   ├── src/
│   ├── components/
│   └── pages/
│
├── /backend
│   ├── main.py
│   ├── agents/
│   │     ├── orchestrator.py
│   │     ├── repo_agent.py
│   │     ├── test_agent.py
│   │     ├── diagnose_agent.py
│   │     ├── fix_agent.py
│   │     ├── git_agent.py
│   │     └── ci_agent.py
│   │
│   ├── sandbox/
│   │     └── docker_runner.py
│   │
│   ├── models/
│   │     └── llm_handler.py
│   │
│   ├── utils/
│   │     └── branch_namer.py
│   │
│   └── results.json
│
├── docker-compose.yml
├── README.md
└── architecture-diagram.png