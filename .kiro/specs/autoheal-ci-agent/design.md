# Design Document: AutoHeal CI

## Overview

AutoHeal CI is an autonomous CI/CD healing agent that automatically detects, diagnoses, fixes, and verifies code issues in GitHub repositories. The system employs a multi-agent architecture orchestrated by LangGraph, with each agent specializing in a specific aspect of the healing workflow.

The system consists of two main components:

1. **Frontend**: A React-based dashboard (deployed on Vercel) that provides user input interface and comprehensive results visualization
2. **Backend**: A FastAPI-based multi-agent system that orchestrates the autonomous healing process

The workflow follows this sequence:
1. User submits repository details via dashboard
2. Orchestrator Agent coordinates 7 specialized agents in a retry loop
3. Each iteration: analyze → discover tests → diagnose failures → generate fixes → patch code → commit → monitor CI
4. Loop continues until tests pass or retry limit reached
5. Results displayed in dashboard with scoring and timeline

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Dashboard (Vercel)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Input Form   │  │ Run Summary  │  │ Score Panel  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────────────────────────┐    │
│  │ Fixes Table  │  │   CI/CD Timeline                 │    │
│  └──────────────┘  └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Orchestrator Agent (LangGraph)           │  │
│  │                  (Retry Loop Controller)              │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                               │
│         ┌────────────────────┼────────────────────┐         │
│         ▼                    ▼                    ▼         │
│  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐  │
│  │Repo Analyzer│      │Test Discovery│    │  Failure    │  │
│  │   Agent     │──────▶   Agent      │───▶│ Diagnosis   │  │
│  └─────────────┘      └─────────────┘     │   Agent     │  │
│                                            └─────────────┘  │
│                                                   │          │
│                                                   ▼          │
│  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐  │
│  │ CI Monitor  │◀─────│  Git Agent  │◀────│Fix Generation│ │
│  │   Agent     │      │             │     │   Agent     │  │
│  └─────────────┘      └─────────────┘     └─────────────┘  │
│         │                    ▲                    │          │
│         │                    │                    ▼          │
│         │              ┌─────────────┐     ┌─────────────┐  │
│         │              │Code Patch   │     │  LLM API    │  │
│         │              │   Agent     │◀────│(GPT-4/etc)  │  │
│         │              └─────────────┘     └─────────────┘  │
│         │                                                    │
│         └──────────────┐                                     │
│                        ▼                                     │
│              ┌──────────────────┐                           │
│              │ Docker Sandbox   │                           │
│              │  (Test Runner)   │                           │
│              └──────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  GitHub Actions  │
                    │    (CI/CD)       │
                    └──────────────────┘
```

### Multi-Agent Architecture

The system uses **LangGraph** for stateful multi-agent orchestration. LangGraph provides:
- State management across agent transitions
- Conditional routing based on agent outputs
- Built-in retry and error handling
- Graph-based workflow visualization

**Agent Communication Pattern:**
- Agents communicate through a shared state object
- Each agent reads from state, performs its task, and updates state
- Orchestrator controls flow based on state conditions
- No direct agent-to-agent communication (all through state)

### Technology Stack

**Frontend:**
- React 18 with Vite (fast build tool)
- Tailwind CSS (utility-first styling)
- Zustand (lightweight state management)
- Recharts (score visualization)
- Axios (HTTP client)
- React Timeline component (iteration visualization)

**Backend:**
- FastAPI (async Python web framework)
- LangGraph (multi-agent orchestration)
- LangChain (LLM integration)
- GitPython (Git operations)
- Docker SDK for Python (sandbox management)
- Pydantic (data validation)

**LLM:**
- Primary: GPT-4 or Claude (via API)
- Alternative: DeepSeek-Coder (open-source)
- Fallback: Rule-based fixes for simple errors

**Infrastructure:**
- Docker (code sandboxing)
- GitHub REST API (CI/CD monitoring)
- Vercel (frontend deployment)
- Environment variables (secrets management)

## Components and Interfaces

### Frontend Components

#### 1. InputForm Component

**Purpose:** Collect repository details and trigger agent execution

**Props:**
```typescript
interface InputFormProps {
  onSubmit: (data: JobRequest) => Promise<void>;
  isLoading: boolean;
}

interface JobRequest {
  repositoryUrl: string;
  teamName: string;
  leaderName: string;
}
```

**Behavior:**
- Validates GitHub URL format (https://github.com/...)
- Validates non-empty team name and leader name
- Disables submit button while loading
- Shows validation errors inline
- Calls API POST /api/heal on submit

#### 2. RunSummaryCard Component

**Purpose:** Display high-level run information

**Props:**
```typescript
interface RunSummaryProps {
  results: HealingResults;
}

interface HealingResults {
  repository: string;
  teamName: string;
  leaderName: string;
  branchName: string;
  totalFailures: number;
  fixesApplied: number;
  ciStatus: 'PASSED' | 'FAILED';
  totalTime: string;
  iterations: number;
}
```

**Behavior:**
- Displays all summary fields in card layout
- Shows green badge for PASSED, red for FAILED
- Formats time as "Xm Ys"

#### 3. ScoreBreakdownPanel Component

**Purpose:** Calculate and visualize scoring

**Props:**
```typescript
interface ScoreBreakdownProps {
  totalTime: string;
  commitCount: number;
}
```

**Behavior:**
- Calculates base score: 100
- Adds speed bonus: +10 if totalTime < 5 minutes
- Subtracts commit penalty: -2 per commit over 20
- Displays breakdown with Recharts bar chart
- Shows final score prominently

#### 4. FixesTable Component

**Purpose:** Display detailed fix information

**Props:**
```typescript
interface FixesTableProps {
  fixes: Fix[];
}

interface Fix {
  file: string;
  bugType: 'LINTING' | 'SYNTAX' | 'LOGIC' | 'TYPE_ERROR' | 'IMPORT' | 'INDENTATION';
  line: number;
  commitMessage: string;
  status: 'Fixed' | 'Failed';
}
```

**Behavior:**
- Renders table with sortable columns
- Color codes status: green for Fixed, red for Failed
- Truncates long file paths with tooltip
- Responsive: stacks on mobile

#### 5. CITimelineComponent

**Purpose:** Visualize CI/CD iteration history

**Props:**
```typescript
interface CITimelineProps {
  iterations: IterationStatus[];
  retryLimit: number;
}

interface IterationStatus {
  iteration: number;
  status: 'PASSED' | 'FAILED';
  timestamp: string;
  failureCount: number;
}
```

**Behavior:**
- Displays vertical timeline
- Shows pass/fail badge for each iteration
- Displays timestamp and failure count
- Shows "X/Y" iterations used

### Backend Components

#### 1. Orchestrator Agent

**Purpose:** Control the multi-agent workflow and retry loop

**State Schema:**
```python
class OrchestratorState(TypedDict):
    repository_url: str
    team_name: str
    leader_name: str
    branch_name: str
    retry_count: int
    retry_limit: int
    start_time: datetime
    repo_path: str
    language: str
    test_framework: str
    test_files: List[str]
    failures: List[Failure]
    fixes: List[Fix]
    ci_status: str
    iterations: List[IterationStatus]
    error: Optional[str]
```

**LangGraph Workflow:**
```python
workflow = StateGraph(OrchestratorState)

# Add nodes
workflow.add_node("analyze_repo", repo_analyzer_agent)
workflow.add_node("discover_tests", test_discovery_agent)
workflow.add_node("diagnose_failures", failure_diagnosis_agent)
workflow.add_node("generate_fixes", fix_generation_agent)
workflow.add_node("patch_code", code_patch_agent)
workflow.add_node("commit_push", git_agent)
workflow.add_node("monitor_ci", ci_monitor_agent)

# Define edges
workflow.set_entry_point("analyze_repo")
workflow.add_edge("analyze_repo", "discover_tests")
workflow.add_edge("discover_tests", "diagnose_failures")
workflow.add_edge("diagnose_failures", "generate_fixes")
workflow.add_edge("generate_fixes", "patch_code")
workflow.add_edge("patch_code", "commit_push")
workflow.add_edge("commit_push", "monitor_ci")

# Conditional routing from monitor_ci
workflow.add_conditional_edges(
    "monitor_ci",
    should_retry,
    {
        "continue": "diagnose_failures",  # Retry
        "end": END  # Success or limit reached
    }
)
```

**Retry Logic:**
```python
def should_retry(state: OrchestratorState) -> str:
    if state["ci_status"] == "PASSED":
        return "end"
    if state["retry_count"] >= state["retry_limit"]:
        return "end"
    state["retry_count"] += 1
    return "continue"
```

#### 2. Repo Analyzer Agent

**Purpose:** Clone and analyze repository structure

**Interface:**
```python
class RepoAnalyzerAgent:
    def analyze(self, state: OrchestratorState) -> OrchestratorState:
        """
        Clones repository and detects language/framework.
        
        Updates state:
        - repo_path: local clone path
        - language: detected language
        - test_framework: detected framework
        """
```

**Implementation:**
- Uses GitPython to clone repository
- Detects language by file extensions (.py, .js, .java)
- Detects test framework by checking:
  - Python: pytest.ini, setup.py with pytest, unittest imports
  - JavaScript: package.json scripts, jest.config.js, mocha presence
- Parses directory tree using os.walk()

#### 3. Test Discovery Agent

**Purpose:** Dynamically find all test files

**Interface:**
```python
class TestDiscoveryAgent:
    def discover(self, state: OrchestratorState) -> OrchestratorState:
        """
        Finds test files based on language patterns.
        
        Updates state:
        - test_files: list of test file paths
        """
```

**Discovery Patterns:**
```python
PATTERNS = {
    "python": [
        "test_*.py",
        "*_test.py",
        "tests/**/*.py",
        "__tests__/**/*.py"
    ],
    "javascript": [
        "*.test.js",
        "*.spec.js",
        "*.test.ts",
        "*.spec.ts",
        "__tests__/**/*.js",
        "__tests__/**/*.ts"
    ]
}
```

**Implementation:**
- Uses glob patterns to match files
- Recursively searches from repository root
- Excludes node_modules, venv, .git directories
- Returns absolute paths

#### 4. Failure Diagnosis Agent

**Purpose:** Execute tests in sandbox and categorize failures

**Interface:**
```python
class FailureDiagnosisAgent:
    def diagnose(self, state: OrchestratorState) -> OrchestratorState:
        """
        Runs tests in Docker and categorizes failures.
        
        Updates state:
        - failures: list of Failure objects
        """

class Failure(BaseModel):
    file: str
    line: int
    bug_type: BugType
    error_message: str
    stack_trace: str

class BugType(str, Enum):
    LINTING = "LINTING"
    SYNTAX = "SYNTAX"
    LOGIC = "LOGIC"
    TYPE_ERROR = "TYPE_ERROR"
    IMPORT = "IMPORT"
    INDENTATION = "INDENTATION"
```

**Categorization Rules:**
```python
def categorize_error(error_message: str, stack_trace: str) -> BugType:
    """
    Maps error messages to bug types.
    
    Rules:
    - LINTING: unused import, unused variable, line too long
    - SYNTAX: missing colon, invalid syntax, unexpected EOF
    - LOGIC: assertion error, wrong output, test failure
    - TYPE_ERROR: type mismatch, attribute error, cannot convert
    - IMPORT: module not found, import error, no module named
    - INDENTATION: indentation error, unexpected indent
    """
```

**Docker Execution:**
```python
def run_tests_in_sandbox(repo_path: str, test_framework: str) -> TestResults:
    """
    1. Build Docker image with repo code
    2. Install dependencies (pip install -r requirements.txt or npm install)
    3. Run test command:
       - pytest: pytest --json-report --json-report-file=results.json
       - unittest: python -m unittest discover -v
       - jest: npm test -- --json --outputFile=results.json
       - mocha: mocha --reporter json > results.json
    4. Copy results.json from container
    5. Destroy container
    6. Parse results
    """
```

#### 5. Fix Generation Agent

**Purpose:** Generate code fixes using LLM

**Interface:**
```python
class FixGenerationAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def generate_fixes(self, state: OrchestratorState) -> OrchestratorState:
        """
        Generates fixes for all failures.
        
        Updates state:
        - fixes: list of Fix objects
        """

class Fix(BaseModel):
    file: str
    line: int
    bug_type: BugType
    original_code: str
    fixed_code: str
    commit_message: str
    status: str = "Pending"
```

**LLM Prompt Template:**
```python
PROMPT_TEMPLATE = """You are an autonomous CI healing agent.

Error Details:
File: {file}
Line: {line}
Error Type: {bug_type}
Error Message: {error_message}
Stack Trace:
{stack_trace}

Original Code Context:
{code_context}

Instructions:
1. Analyze the error and surrounding code
2. Generate the corrected code snippet
3. Return ONLY the fixed code, no explanations
4. Ensure the fix is minimal and targeted

Fixed Code:"""
```

**Code Context Extraction:**
```python
def get_code_context(file_path: str, line: int, context_lines: int = 5) -> str:
    """
    Extracts code around the error line.
    
    Returns:
    - context_lines before error
    - error line
    - context_lines after error
    """
```

**Hybrid Strategy (Optimization):**
```python
def should_use_llm(bug_type: BugType) -> bool:
    """
    Use rule-based fixes for simple errors, LLM for complex ones.
    
    Rule-based: LINTING, SYNTAX (simple), INDENTATION, IMPORT (simple)
    LLM-based: LOGIC, TYPE_ERROR, complex SYNTAX
    """

def apply_rule_based_fix(failure: Failure) -> Optional[str]:
    """
    Simple fixes without LLM:
    - Remove unused imports
    - Add missing colons
    - Fix indentation
    - Add missing imports from common libraries
    """
```

#### 6. Code Patch Agent

**Purpose:** Apply fixes to source files with validation

**Interface:**
```python
class CodePatchAgent:
    def patch(self, state: OrchestratorState) -> OrchestratorState:
        """
        Applies all fixes and validates syntax.
        
        Updates state:
        - fixes: updates status to "Applied" or "Failed"
        """
```

**Implementation:**
```python
def apply_patch(fix: Fix) -> bool:
    """
    1. Read file content
    2. Replace line or apply diff patch
    3. Validate syntax:
       - Python: ast.parse()
       - JavaScript: run through esprima or similar
    4. If valid: write file, return True
    5. If invalid: revert, return False
    """

def validate_syntax(file_path: str, content: str, language: str) -> bool:
    """
    Language-specific syntax validation.
    """
```

#### 7. Git Agent

**Purpose:** Create branches, commit, and push changes

**Interface:**
```python
class GitAgent:
    def commit_and_push(self, state: OrchestratorState) -> OrchestratorState:
        """
        Creates branch, commits fixes, and pushes.
        
        Updates state:
        - branch_name: created branch name
        """
```

**Branch Naming:**
```python
def create_branch_name(team_name: str, leader_name: str) -> str:
    """
    Format: TEAM_NAME_LEADER_NAME_AI_Fix
    
    Rules:
    1. Convert to uppercase
    2. Replace spaces with underscores
    3. Remove special characters except underscores
    4. Append _AI_Fix
    
    Example:
    Input: "RIFT Organisers", "Saiyam Kumar"
    Output: "RIFT_ORGANISERS_SAIYAM_KUMAR_AI_Fix"
    """
    team = team_name.upper().replace(" ", "_")
    leader = leader_name.upper().replace(" ", "_")
    # Remove special chars except underscore
    team = re.sub(r'[^A-Z0-9_]', '', team)
    leader = re.sub(r'[^A-Z0-9_]', '', leader)
    return f"{team}_{leader}_AI_Fix"
```

**Commit Message Format:**
```python
def create_commit_message(fix: Fix) -> str:
    """
    Format: [AI-AGENT] Fix {BUG_TYPE} error in {file} line {line}
    
    Example:
    "[AI-AGENT] Fix SYNTAX error in validator.py line 8"
    """
    filename = os.path.basename(fix.file)
    return f"[AI-AGENT] Fix {fix.bug_type} error in {filename} line {fix.line}"
```

**Git Operations:**
```python
def execute_git_operations(repo_path: str, branch_name: str, fixes: List[Fix]):
    """
    1. Create new branch from main/master
    2. For each fix:
       - Stage file: git add {file}
       - Commit: git commit -m "{message}"
    3. Push branch: git push origin {branch_name}
    4. Validate: no push to main/master
    """
```

#### 8. CI Monitor Agent

**Purpose:** Poll GitHub Actions and track status

**Interface:**
```python
class CIMonitorAgent:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
    
    def monitor(self, state: OrchestratorState) -> OrchestratorState:
        """
        Polls CI/CD status until completion.
        
        Updates state:
        - ci_status: "PASSED" or "FAILED"
        - iterations: appends IterationStatus
        """

class IterationStatus(BaseModel):
    iteration: int
    status: str
    timestamp: datetime
    failure_count: int
```

**Polling Logic:**
```python
def poll_ci_status(repo_url: str, branch_name: str, timeout: int = 600) -> str:
    """
    1. Extract owner/repo from URL
    2. Get workflow runs for branch
    3. Poll every 10 seconds
    4. Return status when complete or timeout
    
    Statuses:
    - "queued" / "in_progress" -> continue polling
    - "completed" with conclusion "success" -> "PASSED"
    - "completed" with conclusion "failure" -> "FAILED"
    """
```

### API Endpoints

#### POST /api/heal

**Purpose:** Start healing job

**Request:**
```json
{
  "repositoryUrl": "https://github.com/owner/repo",
  "teamName": "RIFT Organisers",
  "leaderName": "Saiyam Kumar"
}
```

**Response:**
```json
{
  "jobId": "uuid-string",
  "status": "queued"
}
```

**Implementation:**
```python
@app.post("/api/heal")
async def start_healing(request: HealRequest) -> HealResponse:
    """
    1. Validate inputs
    2. Create job ID
    3. Start orchestrator in background task
    4. Return job ID immediately
    """
```

#### GET /api/status/{job_id}

**Purpose:** Get job status and results

**Response (In Progress):**
```json
{
  "jobId": "uuid-string",
  "status": "running",
  "currentStep": "diagnose_failures",
  "progress": 40
}
```

**Response (Complete):**
```json
{
  "jobId": "uuid-string",
  "status": "completed",
  "results": {
    "repository": "https://github.com/owner/repo",
    "teamName": "RIFT Organisers",
    "leaderName": "Saiyam Kumar",
    "branchName": "RIFT_ORGANISERS_SAIYAM_KUMAR_AI_Fix",
    "totalFailures": 3,
    "fixesApplied": 3,
    "iterations": 2,
    "ciStatus": "PASSED",
    "totalTime": "4m 22s",
    "fixes": [...]
  }
}
```

## Data Models

### Frontend Data Models

```typescript
// Job Request
interface JobRequest {
  repositoryUrl: string;
  teamName: string;
  leaderName: string;
}

// Job Response
interface JobResponse {
  jobId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
}

// Status Response
interface StatusResponse {
  jobId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  currentStep?: string;
  progress?: number;
  results?: HealingResults;
  error?: string;
}

// Healing Results
interface HealingResults {
  repository: string;
  teamName: string;
  leaderName: string;
  branchName: string;
  totalFailures: number;
  fixesApplied: number;
  iterations: number;
  ciStatus: 'PASSED' | 'FAILED';
  totalTime: string;
  fixes: Fix[];
  iterationHistory: IterationStatus[];
}

// Fix
interface Fix {
  file: string;
  bugType: 'LINTING' | 'SYNTAX' | 'LOGIC' | 'TYPE_ERROR' | 'IMPORT' | 'INDENTATION';
  line: number;
  commitMessage: string;
  status: 'Fixed' | 'Failed';
}

// Iteration Status
interface IterationStatus {
  iteration: number;
  status: 'PASSED' | 'FAILED';
  timestamp: string;
  failureCount: number;
}

// Score Breakdown
interface ScoreBreakdown {
  baseScore: number;
  speedBonus: number;
  commitPenalty: number;
  finalScore: number;
}
```

### Backend Data Models

```python
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from enum import Enum
from datetime import datetime

# Enums
class BugType(str, Enum):
    LINTING = "LINTING"
    SYNTAX = "SYNTAX"
    LOGIC = "LOGIC"
    TYPE_ERROR = "TYPE_ERROR"
    IMPORT = "IMPORT"
    INDENTATION = "INDENTATION"

class CIStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"

class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"

class TestFramework(str, Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"

# Request/Response Models
class HealRequest(BaseModel):
    repository_url: HttpUrl
    team_name: str
    leader_name: str

class HealResponse(BaseModel):
    job_id: str
    status: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    current_step: Optional[str] = None
    progress: Optional[int] = None
    results: Optional['HealingResults'] = None
    error: Optional[str] = None

# Core Data Models
class Failure(BaseModel):
    file: str
    line: int
    bug_type: BugType
    error_message: str
    stack_trace: str

class Fix(BaseModel):
    file: str
    line: int
    bug_type: BugType
    original_code: str
    fixed_code: str
    commit_message: str
    status: str = "Pending"

class IterationStatus(BaseModel):
    iteration: int
    status: str
    timestamp: datetime
    failure_count: int

class HealingResults(BaseModel):
    repository: str
    team_name: str
    leader_name: str
    branch_name: str
    total_failures: int
    fixes_applied: int
    iterations: int
    ci_status: CIStatus
    total_time: str
    fixes: List[Fix]
    iteration_history: List[IterationStatus]

# Orchestrator State
class OrchestratorState(TypedDict):
    # Input
    repository_url: str
    team_name: str
    leader_name: str
    
    # Configuration
    retry_limit: int
    retry_count: int
    start_time: datetime
    
    # Repository Info
    repo_path: str
    language: Language
    test_framework: TestFramework
    
    # Workflow Data
    test_files: List[str]
    failures: List[Failure]
    fixes: List[Fix]
    
    # Results
    branch_name: str
    ci_status: CIStatus
    iterations: List[IterationStatus]
    
    # Error Handling
    error: Optional[str]
```

### Results JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "repository",
    "team_name",
    "leader_name",
    "branch_name",
    "total_failures",
    "fixes_applied",
    "iterations",
    "ci_status",
    "total_time",
    "fixes"
  ],
  "properties": {
    "repository": {
      "type": "string",
      "format": "uri"
    },
    "team_name": {
      "type": "string"
    },
    "leader_name": {
      "type": "string"
    },
    "branch_name": {
      "type": "string",
      "pattern": "^[A-Z0-9_]+_AI_Fix$"
    },
    "total_failures": {
      "type": "integer",
      "minimum": 0
    },
    "fixes_applied": {
      "type": "integer",
      "minimum": 0
    },
    "iterations": {
      "type": "integer",
      "minimum": 1
    },
    "ci_status": {
      "type": "string",
      "enum": ["PASSED", "FAILED"]
    },
    "total_time": {
      "type": "string",
      "pattern": "^\\d+m \\d+s$"
    },
    "fixes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file", "bug_type", "line", "commit_message", "status"],
        "properties": {
          "file": {
            "type": "string"
          },
          "bug_type": {
            "type": "string",
            "enum": ["LINTING", "SYNTAX", "LOGIC", "TYPE_ERROR", "IMPORT", "INDENTATION"]
          },
          "line": {
            "type": "integer",
            "minimum": 1
          },
          "commit_message": {
            "type": "string",
            "pattern": "^\\[AI-AGENT\\]"
          },
          "status": {
            "type": "string",
            "enum": ["Fixed", "Failed"]
          }
        }
      }
    }
  }
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: GitHub URL Validation

*For any* string input to the repository URL field, the validation function should return true only if the string matches the pattern "https://github.com/[owner]/[repo]" and false otherwise.

**Validates: Requirements 1.2**

### Property 2: Branch Name Format Compliance

*For any* team name and leader name inputs, the generated branch name should be all uppercase, contain only letters, numbers, and underscores, and end with "_AI_Fix".

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 3: Commit Message Prefix

*For any* fix that is committed, the commit message should start with "[AI-AGENT]" and include the bug type and filename.

**Validates: Requirements 8.6, 8.7**

### Property 4: Test File Discovery Completeness

*For any* repository with test files following standard naming patterns (test_*.py, *.test.js, etc.), the Test_Discovery_Agent should find all test files without using hardcoded paths.

**Validates: Requirements 3.1, 3.2, 3.3, 3.5**

### Property 5: Bug Type Categorization Uniqueness

*For any* test failure, the Failure_Diagnosis_Agent should categorize it into exactly one of the six bug types: LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, or INDENTATION.

**Validates: Requirements 5.3**

### Property 6: Failure Extraction Completeness

*For any* test failure output, the Failure_Diagnosis_Agent should extract all required fields: file path, line number, error message, and stack trace.

**Validates: Requirements 5.1, 5.2, 5.4**

### Property 7: Docker Container Cleanup

*For any* test execution in Docker, after capturing results, the container should be destroyed and not appear in the list of running or stopped containers.

**Validates: Requirements 4.5**

### Property 8: Syntax Validation Rollback

*For any* invalid code patch that fails syntax validation, the Code_Patch_Agent should revert the file to its previous state and mark the fix status as "Failed".

**Validates: Requirements 7.3**

### Property 9: Retry Loop Termination on Success

*For any* healing process where CI status becomes "PASSED", the Orchestrator_Agent should stop the retry loop immediately and not execute additional iterations.

**Validates: Requirements 10.3**

### Property 10: Retry Loop Termination on Limit

*For any* healing process where the retry counter reaches the retry limit (default 5), the Orchestrator_Agent should stop the retry loop and generate final results regardless of CI status.

**Validates: Requirements 10.5**

### Property 11: Results JSON Validity

*For any* completed healing process, the generated results.json file should be valid JSON that can be parsed without errors and deserialized into the HealingResults data model.

**Validates: Requirements 11.7**

### Property 12: Results JSON Completeness

*For any* completed healing process, the results.json should contain all required fields: repository, team_name, leader_name, branch_name, total_failures, fixes_applied, iterations, ci_status, total_time, and fixes array.

**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6**

### Property 13: Time Format Consistency

*For any* total execution time, the format should match the pattern "Xm Ys" where X is minutes and Y is seconds.

**Validates: Requirements 11.5**

### Property 14: Speed Bonus Calculation

*For any* healing process with total time less than 5 minutes, the score calculation should add exactly 10 points as a speed bonus; otherwise, the speed bonus should be 0.

**Validates: Requirements 12.4**

### Property 15: Commit Penalty Calculation

*For any* healing process with N commits, if N > 20, the penalty should be exactly (N - 20) * 2 points; otherwise, the penalty should be 0.

**Validates: Requirements 12.5**

### Property 16: Main Branch Protection

*For any* git operations performed by the Git_Agent, no commits or pushes should be made to the main or master branch.

**Validates: Requirements 8.9**

### Property 17: Fix Status Color Coding

*For any* fix displayed in the dashboard table, if the status is "Fixed", the color should be green; if the status is "Failed", the color should be red.

**Validates: Requirements 12.8**

### Property 18: CI Status Badge Color

*For any* CI status displayed in the dashboard, if the status is "PASSED", the badge should be green; if the status is "FAILED", the badge should be red.

**Validates: Requirements 12.2**

### Property 19: Loading State Prevention

*For any* dashboard state where isLoading is true, the form submit button should be disabled and form resubmission should be prevented.

**Validates: Requirements 1.4**

### Property 20: Input Validation Error Display

*For any* invalid or missing input in the dashboard form, validation error messages should be displayed to the user.

**Validates: Requirements 1.5**

### Property 21: Repository Clone Error Handling

*For any* invalid repository URL or inaccessible repository, the Repo_Analyzer_Agent should return an error object containing a descriptive failure reason rather than throwing an unhandled exception.

**Validates: Requirements 2.5**

### Property 22: Test Framework Command Selection

*For any* detected test framework (pytest, unittest, jest, mocha), the Docker_Sandbox should execute the correct test command specific to that framework.

**Validates: Requirements 20.1, 20.2, 20.3, 20.4**

### Property 23: Agent Execution Sequence

*For any* iteration of the healing process, agents should be called in the exact sequence: Repo_Analyzer_Agent → Test_Discovery_Agent → Failure_Diagnosis_Agent → Fix_Generation_Agent → Code_Patch_Agent → Git_Agent → CI_Monitor_Agent.

**Validates: Requirements 10.2**

### Property 24: Responsive Layout Adaptation

*For any* viewport width between 320px and 1920px, the dashboard should display all content without horizontal overflow and maintain readability.

**Validates: Requirements 13.3, 13.5**

### Property 25: State Update Propagation

*For any* state change (loading, results, error), all dashboard components should have access to the updated state without requiring prop drilling.

**Validates: Requirements 14.2, 14.3, 14.4**

### Property 26: API Job ID Response

*For any* valid POST request to /api/heal, the response should immediately return a unique job ID without waiting for the healing process to complete.

**Validates: Requirements 15.2**

### Property 27: Status Polling Continuation

*For any* job that is not yet complete, the dashboard should continue polling the /api/status/{job_id} endpoint at regular intervals until completion or timeout.

**Validates: Requirements 15.5**

### Property 28: Error Message User-Friendliness

*For any* error condition (clone failure, API failure, timeout, network error), the dashboard should display a user-friendly error message and, where applicable, provide a retry option.

**Validates: Requirements 17.1, 17.2, 17.3, 17.4**

### Property 29: Error Logging Completeness

*For any* error that occurs in the system, the error log should include a timestamp, error message, and contextual information for debugging.

**Validates: Requirements 17.5**

### Property 30: Token Exclusion from Logs

*For any* log entry or error message generated by the system, GitHub tokens or other sensitive credentials should not appear in the logged content.

**Validates: Requirements 18.2**

### Property 31: Input Sanitization

*For any* user input (repository URL, team name, leader name), the system should validate and sanitize the input to prevent injection attacks before processing.

**Validates: Requirements 18.5**

### Property 32: Fix Prompt Construction

*For any* diagnosed failure, the Fix_Generation_Agent should construct a prompt that includes the file path, line number, bug type, error message, stack trace, and code context.

**Validates: Requirements 6.1**

### Property 33: Minimal Patch Generation

*For any* fix generated by the Fix_Generation_Agent, the output should contain only the corrected code snippet without explanatory text or comments.

**Validates: Requirements 6.4**

### Property 34: Patch Application Correctness

*For any* fix applied by the Code_Patch_Agent, the target file should be modified at the specified line number with the corrected code.

**Validates: Requirements 7.1**

### Property 35: Patch Log Maintenance

*For any* patch operation (successful or failed), the Code_Patch_Agent should record the operation in a patch log with file, line, and status information.

**Validates: Requirements 7.5**

### Property 36: CI Polling Timestamp Recording

*For any* CI status check performed by the CI_Monitor_Agent, a timestamp should be recorded for that check.

**Validates: Requirements 9.5**

### Property 37: Orchestrator Time Tracking

*For any* healing process from start to completion, the Orchestrator_Agent should track and record the total execution time.

**Validates: Requirements 10.7**

### Property 38: Dashboard Results Display Completeness

*For any* completed healing process, the dashboard should display all required sections: Run Summary Card, Score Breakdown Panel, Fixes Applied Table, and CI/CD Status Timeline.

**Validates: Requirements 12.1, 12.3, 12.7, 12.9**

### Property 39: Timeline Iteration Display

*For any* healing process with N iterations, the CI/CD Status Timeline should display exactly N iteration entries, each with status, timestamp, and failure count.

**Validates: Requirements 12.9, 12.10**

### Property 40: Test Output Parsing Framework-Specific

*For any* test framework's output format, the Failure_Diagnosis_Agent should correctly parse the output to extract failure information specific to that framework's reporting format.

**Validates: Requirements 20.5**

## Error Handling

### Frontend Error Handling

**Network Errors:**
- Wrap all API calls in try-catch blocks
- Display toast notifications for transient errors
- Provide "Retry" button for failed requests
- Show offline indicator when network is unavailable

**Validation Errors:**
- Validate inputs on blur and submit
- Display inline error messages below form fields
- Prevent form submission until all validations pass
- Clear error messages when user corrects input

**API Errors:**
- Parse error responses from backend
- Display user-friendly messages (not raw error codes)
- Log detailed errors to console for debugging
- Provide fallback UI for critical failures

**State Errors:**
- Use error boundaries to catch React component errors
- Display fallback UI when components crash
- Log errors to monitoring service (e.g., Sentry)
- Provide "Reload" option to recover

### Backend Error Handling

**Repository Errors:**
- Catch GitPython exceptions (authentication, not found, network)
- Return structured error responses with error codes
- Clean up partial clones on failure
- Log repository URL and error details

**Docker Errors:**
- Catch Docker SDK exceptions (build failures, container crashes)
- Ensure containers are cleaned up even on errors
- Return test execution errors to orchestrator
- Log container IDs and error messages

**LLM Errors:**
- Handle API rate limits with exponential backoff
- Catch timeout errors and retry with shorter context
- Fall back to rule-based fixes if LLM unavailable
- Log prompt and response for debugging

**Git Operation Errors:**
- Catch push failures (authentication, conflicts)
- Validate branch names before creation
- Handle merge conflicts gracefully
- Log git commands and output

**CI Monitoring Errors:**
- Handle GitHub API rate limits
- Timeout polling after configurable duration
- Return partial results if CI never completes
- Log API responses for debugging

**Orchestrator Errors:**
- Catch exceptions from any agent
- Continue to next iteration if possible
- Generate results even on partial failure
- Include error details in results.json

### Error Response Format

All API errors should follow this format:

```json
{
  "error": {
    "code": "REPO_CLONE_FAILED",
    "message": "Failed to clone repository: Authentication required",
    "details": {
      "repository": "https://github.com/owner/repo",
      "reason": "Invalid credentials"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Codes

- `REPO_CLONE_FAILED`: Repository cloning failed
- `REPO_NOT_FOUND`: Repository does not exist
- `REPO_ACCESS_DENIED`: No permission to access repository
- `TEST_DISCOVERY_FAILED`: No test files found
- `TEST_EXECUTION_FAILED`: Tests could not be executed
- `DOCKER_BUILD_FAILED`: Docker image build failed
- `DOCKER_RUN_FAILED`: Docker container execution failed
- `LLM_API_ERROR`: LLM API request failed
- `LLM_TIMEOUT`: LLM response timeout
- `PATCH_APPLY_FAILED`: Code patch could not be applied
- `SYNTAX_VALIDATION_FAILED`: Patched code has syntax errors
- `GIT_PUSH_FAILED`: Failed to push to remote repository
- `CI_TIMEOUT`: CI pipeline did not complete in time
- `RETRY_LIMIT_REACHED`: Maximum retry iterations reached
- `INVALID_INPUT`: User input validation failed

## Testing Strategy

### Dual Testing Approach

The AutoHeal CI system requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests:**
- Test specific examples and edge cases
- Verify integration points between components
- Test error conditions and boundary cases
- Focus on concrete scenarios with known inputs/outputs

**Property-Based Tests:**
- Verify universal properties across all inputs
- Use randomized input generation for comprehensive coverage
- Test invariants that should always hold
- Minimum 100 iterations per property test

Both testing approaches are complementary and necessary. Unit tests catch specific bugs and verify concrete behavior, while property tests ensure general correctness across the input space.

### Property-Based Testing Configuration

**Library Selection:**
- Python backend: Use `hypothesis` library
- TypeScript/JavaScript frontend: Use `fast-check` library

**Test Configuration:**
```python
# Python example with hypothesis
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(
    team_name=st.text(min_size=1, max_size=50),
    leader_name=st.text(min_size=1, max_size=50)
)
def test_branch_name_format(team_name, leader_name):
    """
    Feature: autoheal-ci-agent, Property 2: Branch Name Format Compliance
    """
    branch_name = create_branch_name(team_name, leader_name)
    assert branch_name.isupper()
    assert branch_name.endswith("_AI_Fix")
    assert all(c.isupper() or c.isdigit() or c == '_' for c in branch_name)
```

```typescript
// TypeScript example with fast-check
import fc from 'fast-check';

describe('Feature: autoheal-ci-agent, Property 1: GitHub URL Validation', () => {
  it('should validate GitHub URLs correctly', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        const isValid = validateGitHubUrl(input);
        const matchesPattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+$/.test(input);
        return isValid === matchesPattern;
      }),
      { numRuns: 100 }
    );
  });
});
```

**Tagging Requirements:**
- Each property test must include a comment referencing the design property
- Format: `Feature: autoheal-ci-agent, Property {number}: {property_title}`
- This enables traceability from requirements → design → tests

### Frontend Testing

**Unit Tests (Jest + React Testing Library):**

1. **Component Rendering Tests:**
   - InputForm renders with all required fields
   - RunSummaryCard displays all summary information
   - ScoreBreakdownPanel calculates scores correctly
   - FixesTable renders fix data in table format
   - CITimelineComponent displays iteration history

2. **User Interaction Tests:**
   - Form submission triggers API call
   - Validation errors display on invalid input
   - Loading state disables form during execution
   - Retry button appears on errors

3. **State Management Tests:**
   - Loading state updates correctly
   - Results state updates on API response
   - Error state updates on failures
   - State persists across component re-renders

**Property-Based Tests (fast-check):**

1. **URL Validation Property (Property 1)**
2. **Loading State Prevention Property (Property 19)**
3. **Input Validation Error Display Property (Property 20)**
4. **Fix Status Color Coding Property (Property 17)**
5. **CI Status Badge Color Property (Property 18)**
6. **Speed Bonus Calculation Property (Property 14)**
7. **Commit Penalty Calculation Property (Property 15)**
8. **Responsive Layout Adaptation Property (Property 24)**

### Backend Testing

**Unit Tests (pytest):**

1. **Repo Analyzer Tests:**
   - Clone successful repositories
   - Handle clone failures gracefully
   - Detect Python language correctly
   - Detect JavaScript language correctly
   - Identify pytest framework
   - Identify jest framework

2. **Test Discovery Tests:**
   - Find Python test files with test_*.py pattern
   - Find JavaScript test files with *.test.js pattern
   - Exclude node_modules and venv directories
   - Return empty list when no tests found

3. **Failure Diagnosis Tests:**
   - Parse pytest JSON output
   - Parse jest JSON output
   - Categorize linting errors correctly
   - Categorize syntax errors correctly
   - Categorize import errors correctly
   - Extract file, line, and message from failures

4. **Fix Generation Tests:**
   - Construct prompts with all required fields
   - Parse LLM responses correctly
   - Apply rule-based fixes for simple errors
   - Handle LLM API errors gracefully

5. **Code Patch Tests:**
   - Apply patches to correct line numbers
   - Validate Python syntax with ast.parse
   - Revert invalid patches
   - Maintain patch log

6. **Git Agent Tests:**
   - Create branch names in correct format
   - Convert names to uppercase
   - Replace spaces with underscores
   - Prefix commits with [AI-AGENT]
   - Prevent pushes to main branch

7. **CI Monitor Tests:**
   - Poll GitHub Actions API
   - Detect PASSED status correctly
   - Detect FAILED status correctly
   - Timeout after configured duration

8. **Orchestrator Tests:**
   - Initialize retry counter to zero
   - Call agents in correct sequence
   - Stop on CI PASSED
   - Stop at retry limit
   - Track execution time

**Property-Based Tests (hypothesis):**

1. **Branch Name Format Compliance Property (Property 2)**
2. **Commit Message Prefix Property (Property 3)**
3. **Test File Discovery Completeness Property (Property 4)**
4. **Bug Type Categorization Uniqueness Property (Property 5)**
5. **Failure Extraction Completeness Property (Property 6)**
6. **Docker Container Cleanup Property (Property 7)**
7. **Syntax Validation Rollback Property (Property 8)**
8. **Retry Loop Termination on Success Property (Property 9)**
9. **Retry Loop Termination on Limit Property (Property 10)**
10. **Results JSON Validity Property (Property 11)**
11. **Results JSON Completeness Property (Property 12)**
12. **Time Format Consistency Property (Property 13)**
13. **Main Branch Protection Property (Property 16)**
14. **Repository Clone Error Handling Property (Property 21)**
15. **Test Framework Command Selection Property (Property 22)**
16. **Agent Execution Sequence Property (Property 23)**
17. **Token Exclusion from Logs Property (Property 30)**
18. **Input Sanitization Property (Property 31)**
19. **Minimal Patch Generation Property (Property 33)**
20. **Patch Application Correctness Property (Property 34)**

### Integration Tests

**End-to-End Workflow Tests:**

1. **Successful Healing Flow:**
   - Submit repository with known failures
   - Verify all agents execute in sequence
   - Verify fixes are generated and applied
   - Verify branch is created and pushed
   - Verify CI passes after fixes
   - Verify results.json is generated

2. **Retry Loop Flow:**
   - Submit repository with multiple failure types
   - Verify first iteration fixes some issues
   - Verify second iteration fixes remaining issues
   - Verify CI passes after multiple iterations
   - Verify iteration history is recorded

3. **Failure Scenarios:**
   - Invalid repository URL returns error
   - Repository with no tests returns error
   - LLM API failure falls back to rule-based fixes
   - Retry limit reached generates final results
   - Docker failures are handled gracefully

**API Integration Tests:**

1. **POST /api/heal:**
   - Valid request returns job ID
   - Invalid URL returns validation error
   - Missing fields return validation error

2. **GET /api/status/{job_id}:**
   - Valid job ID returns status
   - Invalid job ID returns 404
   - Completed job returns full results

### Test Data

**Sample Repositories:**
- Python repository with pytest and linting errors
- Python repository with syntax errors
- JavaScript repository with jest and type errors
- JavaScript repository with import errors
- Repository with mixed error types
- Repository with no errors (baseline)

**Mock Data:**
- Sample test output from pytest, unittest, jest, mocha
- Sample error messages for each bug type
- Sample LLM responses with fixes
- Sample GitHub API responses

### Continuous Integration

**CI Pipeline:**
1. Run linters (eslint, pylint)
2. Run unit tests with coverage
3. Run property-based tests (100 iterations each)
4. Run integration tests
5. Build Docker images
6. Deploy frontend to Vercel (on main branch)

**Coverage Requirements:**
- Minimum 80% code coverage for unit tests
- All 40 correctness properties must have property-based tests
- All critical paths must have integration tests

### Manual Testing Checklist

**Dashboard UI:**
- [ ] Form accepts valid inputs
- [ ] Form rejects invalid inputs with clear messages
- [ ] Loading indicator appears during execution
- [ ] Results display correctly after completion
- [ ] Score calculation is accurate
- [ ] Timeline shows all iterations
- [ ] Responsive layout works on mobile
- [ ] Error messages are user-friendly

**Backend Workflow:**
- [ ] Repository clones successfully
- [ ] Test files are discovered dynamically
- [ ] Tests execute in Docker sandbox
- [ ] Failures are categorized correctly
- [ ] Fixes are generated by LLM
- [ ] Patches apply without syntax errors
- [ ] Branch name follows format
- [ ] Commits have correct prefix
- [ ] CI pipeline is monitored
- [ ] Retry loop works correctly
- [ ] Results.json is generated

**Error Handling:**
- [ ] Invalid repository URL shows error
- [ ] Network failures show retry option
- [ ] LLM failures fall back gracefully
- [ ] Docker failures are handled
- [ ] Timeout shows partial results
- [ ] All errors are logged
