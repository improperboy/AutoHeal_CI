# Requirements Document

## Introduction

AutoHeal CI is an autonomous CI/CD healing agent system that automatically detects, fixes, and verifies code issues in GitHub repositories. The system consists of a React dashboard frontend and a multi-agent backend that orchestrates repository analysis, test discovery, failure diagnosis, fix generation, code patching, git operations, and CI/CD monitoring until all tests pass.

## Glossary

- **AutoHeal_System**: The complete autonomous CI/CD healing agent system including frontend and backend
- **Dashboard**: The React-based web interface for user interaction and results visualization
- **Orchestrator_Agent**: The central agent that controls the multi-agent workflow and retry loop
- **Repo_Analyzer_Agent**: Agent responsible for cloning and analyzing repository structure
- **Test_Discovery_Agent**: Agent that dynamically discovers test files in the repository
- **Failure_Diagnosis_Agent**: Agent that runs tests and categorizes failures
- **Fix_Generation_Agent**: LLM-powered agent that generates code fixes
- **Code_Patch_Agent**: Agent that applies fixes to code files
- **Git_Agent**: Agent that handles branch creation, commits, and pushes
- **CI_Monitor_Agent**: Agent that polls CI/CD pipeline status
- **Docker_Sandbox**: Isolated Docker container environment for safe code execution
- **Bug_Type**: One of six categories: LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, INDENTATION
- **Branch_Name**: Git branch name following format: TEAM_NAME_LEADER_NAME_AI_Fix
- **Results_JSON**: Output file containing complete run summary and fix details
- **Retry_Limit**: Maximum number of fix-test-monitor iterations (default: 5)
- **Test_Framework**: Testing library used by repository (pytest, unittest, jest, mocha)

## Requirements

### Requirement 1: Dashboard Input Interface

**User Story:** As a user, I want to input repository details through a web form, so that I can initiate the autonomous healing process.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Dashboard SHALL display an input form with fields for repository URL, team name, and leader name
2. WHEN a user enters a GitHub repository URL, THE Dashboard SHALL validate the URL format
3. WHEN a user clicks the "Run Agent" button with valid inputs, THE Dashboard SHALL trigger the backend API and display a loading indicator
4. WHEN the agent is running, THE Dashboard SHALL prevent form resubmission
5. WHEN inputs are invalid or missing, THE Dashboard SHALL display validation error messages

### Requirement 2: Repository Analysis

**User Story:** As the system, I want to analyze repository structure and detect programming languages, so that I can configure appropriate testing strategies.

#### Acceptance Criteria

1. WHEN a repository URL is provided, THE Repo_Analyzer_Agent SHALL clone the repository to a temporary location
2. WHEN the repository is cloned, THE Repo_Analyzer_Agent SHALL detect the primary programming language (Python, JavaScript, Java)
3. WHEN the language is detected, THE Repo_Analyzer_Agent SHALL identify the test framework (pytest, unittest, jest, mocha)
4. WHEN analyzing the repository, THE Repo_Analyzer_Agent SHALL parse the complete project directory tree
5. IF the repository cannot be cloned, THEN THE Repo_Analyzer_Agent SHALL return an error with the failure reason

### Requirement 3: Dynamic Test Discovery

**User Story:** As the system, I want to automatically discover all test files, so that I can run comprehensive tests without hardcoded paths.

#### Acceptance Criteria

1. WHEN the repository structure is available, THE Test_Discovery_Agent SHALL search for test files using language-specific patterns
2. FOR Python repositories, THE Test_Discovery_Agent SHALL identify files matching patterns: test_*.py, *_test.py, and files in __tests__/ directories
3. FOR JavaScript repositories, THE Test_Discovery_Agent SHALL identify files matching patterns: *.test.js, *.spec.js, and files in __tests__/ directories
4. THE Test_Discovery_Agent SHALL NOT use hardcoded file paths
5. WHEN test files are discovered, THE Test_Discovery_Agent SHALL return a list of all test file paths

### Requirement 4: Sandboxed Test Execution

**User Story:** As the system, I want to execute tests in isolated Docker containers, so that I can prevent malicious code from affecting the host system.

#### Acceptance Criteria

1. WHEN tests need to be executed, THE Docker_Sandbox SHALL create a temporary Docker container with the repository code
2. WHEN the container is created, THE Docker_Sandbox SHALL install all project dependencies
3. WHEN dependencies are installed, THE Docker_Sandbox SHALL execute the test command appropriate for the detected Test_Framework
4. WHEN tests complete, THE Docker_Sandbox SHALL capture all output logs and test results
5. WHEN results are captured, THE Docker_Sandbox SHALL destroy the container
6. THE Docker_Sandbox SHALL prevent network access to external resources during test execution

### Requirement 5: Failure Diagnosis and Categorization

**User Story:** As the system, I want to diagnose test failures and categorize them by bug type, so that I can generate appropriate fixes.

#### Acceptance Criteria

1. WHEN test execution completes with failures, THE Failure_Diagnosis_Agent SHALL parse the test output to extract failure details
2. FOR each failure, THE Failure_Diagnosis_Agent SHALL extract the file path, line number, error message, and stack trace
3. WHEN analyzing error messages, THE Failure_Diagnosis_Agent SHALL categorize each failure into exactly one Bug_Type: LINTING, SYNTAX, LOGIC, TYPE_ERROR, IMPORT, or INDENTATION
4. WHEN categorization is complete, THE Failure_Diagnosis_Agent SHALL return a structured list of failures with file, line, type, and trace
5. THE Failure_Diagnosis_Agent SHALL match the exact test case format specified in evaluation criteria

### Requirement 6: AI-Powered Fix Generation

**User Story:** As the system, I want to generate code fixes using LLM, so that I can automatically resolve identified issues.

#### Acceptance Criteria

1. WHEN a failure is diagnosed, THE Fix_Generation_Agent SHALL construct a prompt containing file, line, error type, and stack trace
2. WHEN the prompt is ready, THE Fix_Generation_Agent SHALL send it to the configured LLM (GPT-4, Claude, or DeepSeek-Coder)
3. WHEN the LLM responds, THE Fix_Generation_Agent SHALL extract the corrected code snippet
4. THE Fix_Generation_Agent SHALL generate minimal patches without explanatory text
5. WHEN multiple failures exist in the same file, THE Fix_Generation_Agent SHALL generate fixes that do not conflict with each other

### Requirement 7: Code Patching

**User Story:** As the system, I want to apply generated fixes to source files, so that I can resolve the identified issues.

#### Acceptance Criteria

1. WHEN a fix is generated, THE Code_Patch_Agent SHALL apply the fix to the target file at the specified line
2. WHEN the patch is applied, THE Code_Patch_Agent SHALL validate syntax correctness for the file's language
3. IF syntax validation fails, THEN THE Code_Patch_Agent SHALL revert the change and mark the fix as failed
4. WHEN syntax is valid, THE Code_Patch_Agent SHALL save the modified file
5. THE Code_Patch_Agent SHALL maintain a log of all applied patches

### Requirement 8: Git Branch Management

**User Story:** As the system, I want to create properly named branches and commit fixes, so that changes are tracked and can be reviewed.

#### Acceptance Criteria

1. WHEN fixes are ready to commit, THE Git_Agent SHALL create a new branch following the Branch_Name format
2. THE Git_Agent SHALL convert team name and leader name to UPPERCASE
3. THE Git_Agent SHALL replace all spaces with underscores
4. THE Git_Agent SHALL append "_AI_Fix" to the branch name
5. THE Git_Agent SHALL validate that the branch name contains only uppercase letters, underscores, and numbers
6. WHEN creating commits, THE Git_Agent SHALL prefix all commit messages with "[AI-AGENT]"
7. WHEN committing a fix, THE Git_Agent SHALL include the bug type and file name in the commit message
8. WHEN commits are created, THE Git_Agent SHALL push the branch to the remote repository
9. THE Git_Agent SHALL NOT push to the main branch

### Requirement 9: CI/CD Pipeline Monitoring

**User Story:** As the system, I want to monitor CI/CD pipeline status, so that I can verify fixes and iterate if needed.

#### Acceptance Criteria

1. WHEN a branch is pushed, THE CI_Monitor_Agent SHALL poll the GitHub Actions API for pipeline status
2. WHEN the pipeline is running, THE CI_Monitor_Agent SHALL wait and continue polling at regular intervals
3. WHEN the pipeline completes with PASSED status, THE CI_Monitor_Agent SHALL signal success to the Orchestrator_Agent
4. WHEN the pipeline completes with FAILED status, THE CI_Monitor_Agent SHALL signal failure to the Orchestrator_Agent
5. THE CI_Monitor_Agent SHALL include timestamps for each status check

### Requirement 10: Orchestration and Retry Logic

**User Story:** As the system, I want to orchestrate the multi-agent workflow with retry capability, so that I can iteratively fix issues until tests pass.

#### Acceptance Criteria

1. WHEN the healing process starts, THE Orchestrator_Agent SHALL initialize the retry counter to zero
2. WHEN an iteration begins, THE Orchestrator_Agent SHALL call agents in sequence: Repo_Analyzer_Agent, Test_Discovery_Agent, Failure_Diagnosis_Agent, Fix_Generation_Agent, Code_Patch_Agent, Git_Agent, CI_Monitor_Agent
3. WHEN CI_Monitor_Agent reports PASSED, THE Orchestrator_Agent SHALL stop the retry loop and generate results
4. WHEN CI_Monitor_Agent reports FAILED and retry counter is less than Retry_Limit, THE Orchestrator_Agent SHALL increment the counter and start a new iteration
5. WHEN retry counter reaches Retry_Limit, THE Orchestrator_Agent SHALL stop and generate results with final status
6. THE Orchestrator_Agent SHALL use a default Retry_Limit of 5
7. THE Orchestrator_Agent SHALL track total execution time from start to finish

### Requirement 11: Results Generation

**User Story:** As the system, I want to generate a comprehensive results file, so that the dashboard can display detailed information.

#### Acceptance Criteria

1. WHEN the healing process completes, THE AutoHeal_System SHALL generate a Results_JSON file
2. THE Results_JSON SHALL include repository URL, team name, leader name, and branch name
3. THE Results_JSON SHALL include total failures detected, fixes applied, and iterations used
4. THE Results_JSON SHALL include final CI status (PASSED or FAILED)
5. THE Results_JSON SHALL include total time taken in minutes and seconds format
6. THE Results_JSON SHALL include an array of fix objects with file, bug_type, line, commit_message, and status fields
7. THE Results_JSON SHALL be valid JSON format

### Requirement 12: Dashboard Results Visualization

**User Story:** As a user, I want to view comprehensive results in the dashboard, so that I can understand what the agent accomplished.

#### Acceptance Criteria

1. WHEN results are available, THE Dashboard SHALL display a Run Summary Card with repository, team name, leader name, branch name, total failures, total fixes, CI status badge, and total time
2. WHEN displaying CI status, THE Dashboard SHALL show a green badge for PASSED and red badge for FAILED
3. WHEN results are available, THE Dashboard SHALL display a Score Breakdown Panel with base score, speed bonus, efficiency penalty, and final score
4. THE Dashboard SHALL calculate speed bonus as +10 points if total time is less than 5 minutes
5. THE Dashboard SHALL calculate efficiency penalty as -2 points per commit over 20 commits
6. THE Dashboard SHALL display the base score as 100 points
7. WHEN results are available, THE Dashboard SHALL display a Fixes Applied Table with columns: File, Bug Type, Line Number, Commit Message, Status
8. WHEN displaying fix status, THE Dashboard SHALL use green color for "Fixed" and red color for "Failed"
9. WHEN results are available, THE Dashboard SHALL display a CI/CD Status Timeline showing each iteration with pass/fail badge and timestamp
10. THE Dashboard SHALL display the number of iterations used out of the retry limit

### Requirement 13: Dashboard Responsiveness

**User Story:** As a user, I want the dashboard to work on different devices, so that I can access it from desktop or mobile.

#### Acceptance Criteria

1. WHEN the Dashboard is accessed on desktop, THE Dashboard SHALL display all components in a multi-column layout
2. WHEN the Dashboard is accessed on mobile, THE Dashboard SHALL display all components in a single-column layout
3. WHEN the viewport width changes, THE Dashboard SHALL adjust layout smoothly without content overflow
4. THE Dashboard SHALL use responsive CSS units and breakpoints
5. THE Dashboard SHALL maintain readability on screens from 320px to 1920px width

### Requirement 14: State Management

**User Story:** As a developer, I want centralized state management, so that the dashboard components can share data efficiently.

#### Acceptance Criteria

1. THE Dashboard SHALL use a state management library (Zustand, Redux, or Context API)
2. WHEN the agent starts running, THE Dashboard SHALL update the loading state globally
3. WHEN results are received, THE Dashboard SHALL update the results state globally
4. WHEN errors occur, THE Dashboard SHALL update the error state globally
5. THE Dashboard SHALL allow any component to access shared state without prop drilling

### Requirement 15: API Integration

**User Story:** As the dashboard, I want to communicate with the backend API, so that I can trigger the agent and receive results.

#### Acceptance Criteria

1. THE Dashboard SHALL provide an API endpoint POST /api/heal that accepts repository URL, team name, and leader name
2. WHEN the endpoint is called, THE AutoHeal_System SHALL return a job ID immediately
3. THE Dashboard SHALL provide an API endpoint GET /api/status/{job_id} that returns current job status
4. WHEN the job is complete, THE status endpoint SHALL return the complete Results_JSON
5. THE Dashboard SHALL poll the status endpoint until the job completes or times out

### Requirement 16: Deployment

**User Story:** As a user, I want to access the dashboard online, so that I don't need to run it locally.

#### Acceptance Criteria

1. THE Dashboard SHALL be deployed to a publicly accessible URL
2. THE Dashboard SHALL be deployed on Vercel or equivalent platform
3. WHEN the deployment is complete, THE Dashboard SHALL be accessible via HTTPS
4. THE Dashboard SHALL load within 3 seconds on standard broadband connections
5. THE Dashboard SHALL handle CORS properly for API requests

### Requirement 17: Error Handling

**User Story:** As a user, I want clear error messages when things go wrong, so that I can understand what happened.

#### Acceptance Criteria

1. WHEN the repository cannot be cloned, THE Dashboard SHALL display an error message explaining the issue
2. WHEN the API request fails, THE Dashboard SHALL display a user-friendly error message
3. WHEN the agent times out, THE Dashboard SHALL display a timeout message with partial results if available
4. WHEN network errors occur, THE Dashboard SHALL display a retry option
5. THE AutoHeal_System SHALL log all errors with timestamps and context for debugging

### Requirement 18: Security

**User Story:** As a system administrator, I want secure handling of credentials, so that GitHub tokens are not exposed.

#### Acceptance Criteria

1. THE AutoHeal_System SHALL store GitHub tokens in environment variables
2. THE AutoHeal_System SHALL NOT include tokens in logs or error messages
3. THE AutoHeal_System SHALL NOT commit tokens to the repository
4. THE Docker_Sandbox SHALL run with minimal privileges
5. THE AutoHeal_System SHALL validate all user inputs to prevent injection attacks

### Requirement 19: Documentation

**User Story:** As a developer, I want comprehensive documentation, so that I can understand, deploy, and maintain the system.

#### Acceptance Criteria

1. THE AutoHeal_System SHALL include a README.md file with project overview, setup instructions, and usage examples
2. THE README SHALL include an architecture diagram showing all agents and their interactions
3. THE README SHALL include environment variable configuration instructions
4. THE README SHALL include deployment instructions for both frontend and backend
5. THE README SHALL include API endpoint documentation
6. THE AutoHeal_System SHALL include inline code comments for complex logic
7. THE README SHALL include troubleshooting section for common issues

### Requirement 20: Test Framework Support

**User Story:** As the system, I want to support multiple test frameworks, so that I can work with diverse repositories.

#### Acceptance Criteria

1. WHEN a Python repository uses pytest, THE AutoHeal_System SHALL execute tests using "pytest --json-report"
2. WHEN a Python repository uses unittest, THE AutoHeal_System SHALL execute tests using "python -m unittest discover"
3. WHEN a JavaScript repository uses jest, THE AutoHeal_System SHALL execute tests using "npm test" or "jest --json"
4. WHEN a JavaScript repository uses mocha, THE AutoHeal_System SHALL execute tests using "npm test" or "mocha --reporter json"
5. THE AutoHeal_System SHALL parse test output format specific to each framework
