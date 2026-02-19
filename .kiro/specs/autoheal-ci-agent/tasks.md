# Implementation Plan: AutoHeal CI

## Overview

This implementation plan breaks down the AutoHeal CI system into incremental, testable tasks. The system consists of a React frontend dashboard and a Python FastAPI backend with multi-agent orchestration using LangGraph. Each task builds on previous work, with property-based tests integrated throughout to catch errors early.

## Tasks

- [x] 1. Set up project structure and development environment
  - Create monorepo structure with /frontend and /backend directories
  - Initialize React project with Vite and TypeScript in /frontend
  - Initialize Python project with FastAPI in /backend
  - Set up package managers (npm for frontend, poetry/pip for backend)
  - Create .env.example files for configuration
  - Set up .gitignore for both projects
  - _Requirements: All_

- [ ] 2. Implement backend core data models and types
  - [ ] 2.1 Create Pydantic models for all data structures
    - Define BugType, CIStatus, Language, TestFramework enums
    - Define Failure, Fix, IterationStatus, HealingResults models
    - Define OrchestratorState TypedDict for LangGraph
    - Define API request/response models (HealRequest, HealResponse, StatusResponse)
    - _Requirements: Data Models section_
  
  - [ ]* 2.2 Write property test for Results JSON validity
    - **Property 11: Results JSON Validity**
    - **Validates: Requirements 11.7**
  
  - [ ]* 2.3 Write property test for Results JSON completeness
    - **Property 12: Results JSON Completeness**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6**

- [ ] 3. Implement Git Agent with branch naming and commit logic
  - [ ] 3.1 Create GitAgent class with branch name generation
    - Implement create_branch_name() function
    - Convert team/leader names to uppercase
    - Replace spaces with underscores
    - Remove special characters except underscores
    - Append "_AI_Fix" suffix
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 3.2 Write property test for branch name format compliance
    - **Property 2: Branch Name Format Compliance**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
  
  - [ ] 3.3 Implement commit message formatting
    - Create create_commit_message() function
    - Prefix with "[AI-AGENT]"
    - Include bug type and filename
    - _Requirements: 8.6, 8.7_
  
  - [ ]* 3.4 Write property test for commit message prefix
    - **Property 3: Commit Message Prefix**
    - **Validates: Requirements 8.6, 8.7**
  
  - [ ] 3.5 Implement git operations (branch, commit, push)
    - Use GitPython library
    - Create branch from main/master
    - Stage and commit files
    - Push to remote repository
    - Validate no pushes to main branch
    - _Requirements: 8.8, 8.9_
  
  - [ ]* 3.6 Write property test for main branch protection
    - **Property 16: Main Branch Protection**
    - **Validates: Requirements 8.9**

- [ ] 4. Implement Repository Analyzer Agent
  - [ ] 4.1 Create RepoAnalyzerAgent class
    - Implement repository cloning with GitPython
    - Detect programming language by file extensions
    - Detect test framework by checking config files and imports
    - Parse directory tree with os.walk()
    - Handle clone errors gracefully
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 4.2 Write unit tests for language detection
    - Test Python detection
    - Test JavaScript detection
    - Test Java detection
    - _Requirements: 2.2_
  
  - [ ]* 4.3 Write unit tests for framework detection
    - Test pytest detection
    - Test unittest detection
    - Test jest detection
    - Test mocha detection
    - _Requirements: 2.3_
  
  - [ ]* 4.4 Write property test for repository clone error handling
    - **Property 21: Repository Clone Error Handling**
    - **Validates: Requirements 2.5**

- [ ] 5. Implement Test Discovery Agent
  - [ ] 5.1 Create TestDiscoveryAgent class
    - Define test file patterns for each language
    - Implement glob-based file discovery
    - Recursively search from repository root
    - Exclude node_modules, venv, .git directories
    - Return list of absolute test file paths
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [ ]* 5.2 Write property test for test file discovery completeness
    - **Property 4: Test File Discovery Completeness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
  
  - [ ]* 5.3 Write unit tests for pattern matching
    - Test Python test_*.py pattern
    - Test Python *_test.py pattern
    - Test JavaScript *.test.js pattern
    - Test JavaScript *.spec.js pattern
    - Test __tests__/ directory discovery
    - _Requirements: 3.2, 3.3_

- [ ] 6. Checkpoint - Verify core agents work independently
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Docker Sandbox for test execution
  - [ ] 7.1 Create DockerSandbox class
    - Build Docker image with repository code
    - Install dependencies (pip install or npm install)
    - Execute test command based on framework
    - Capture output logs and test results
    - Destroy container after execution
    - Implement network isolation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 7.2 Write property test for Docker container cleanup
    - **Property 7: Docker Container Cleanup**
    - **Validates: Requirements 4.5**
  
  - [ ]* 7.3 Write property test for test framework command selection
    - **Property 22: Test Framework Command Selection**
    - **Validates: Requirements 20.1, 20.2, 20.3, 20.4**
  
  - [ ]* 7.4 Write unit tests for test execution
    - Test pytest execution with --json-report
    - Test unittest execution
    - Test jest execution with --json
    - Test mocha execution with --reporter json
    - _Requirements: 20.1, 20.2, 20.3, 20.4_

- [ ] 8. Implement Failure Diagnosis Agent
  - [ ] 8.1 Create FailureDiagnosisAgent class
    - Parse test output JSON from different frameworks
    - Extract file path, line number, error message, stack trace
    - Implement categorize_error() function for bug type classification
    - Map error messages to BugType enum values
    - Return structured list of Failure objects
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 8.2 Write property test for bug type categorization uniqueness
    - **Property 5: Bug Type Categorization Uniqueness**
    - **Validates: Requirements 5.3**
  
  - [ ]* 8.3 Write property test for failure extraction completeness
    - **Property 6: Failure Extraction Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.4**
  
  - [ ]* 8.4 Write property test for test output parsing
    - **Property 40: Test Output Parsing Framework-Specific**
    - **Validates: Requirements 20.5**
  
  - [ ]* 8.5 Write unit tests for error categorization
    - Test LINTING categorization (unused import, unused variable)
    - Test SYNTAX categorization (missing colon, invalid syntax)
    - Test LOGIC categorization (assertion error, wrong output)
    - Test TYPE_ERROR categorization (type mismatch, attribute error)
    - Test IMPORT categorization (module not found, import error)
    - Test INDENTATION categorization (indentation error)
    - _Requirements: 5.3_

- [ ] 9. Implement Fix Generation Agent with LLM integration
  - [ ] 9.1 Create FixGenerationAgent class
    - Set up LLM client (OpenAI, Anthropic, or DeepSeek)
    - Implement get_code_context() to extract surrounding code
    - Implement prompt template construction
    - Send prompts to LLM and parse responses
    - Extract corrected code snippets from responses
    - Handle LLM API errors with retries and fallbacks
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 9.2 Write property test for fix prompt construction
    - **Property 32: Fix Prompt Construction**
    - **Validates: Requirements 6.1**
  
  - [ ]* 9.3 Write property test for minimal patch generation
    - **Property 33: Minimal Patch Generation**
    - **Validates: Requirements 6.4**
  
  - [ ] 9.4 Implement rule-based fixes for simple errors
    - Create should_use_llm() decision function
    - Implement apply_rule_based_fix() for LINTING, simple SYNTAX, INDENTATION
    - Remove unused imports
    - Add missing colons
    - Fix indentation
    - Add common missing imports
    - _Requirements: 6.5_
  
  - [ ]* 9.5 Write unit tests for LLM integration
    - Test prompt construction with all required fields
    - Test LLM response parsing
    - Test error handling for API failures
    - Test fallback to rule-based fixes
    - _Requirements: 6.2, 6.3_

- [ ] 10. Implement Code Patch Agent
  - [ ] 10.1 Create CodePatchAgent class
    - Implement apply_patch() to modify files at specific lines
    - Implement validate_syntax() for Python (ast.parse) and JavaScript
    - Implement rollback logic for invalid patches
    - Maintain patch log with all operations
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 10.2 Write property test for syntax validation rollback
    - **Property 8: Syntax Validation Rollback**
    - **Validates: Requirements 7.3**
  
  - [ ]* 10.3 Write property test for patch application correctness
    - **Property 34: Patch Application Correctness**
    - **Validates: Requirements 7.1**
  
  - [ ]* 10.4 Write property test for patch log maintenance
    - **Property 35: Patch Log Maintenance**
    - **Validates: Requirements 7.5**
  
  - [ ]* 10.5 Write unit tests for patching
    - Test patch application to correct line
    - Test Python syntax validation
    - Test JavaScript syntax validation
    - Test rollback on invalid syntax
    - Test patch log recording
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [ ] 11. Checkpoint - Verify fix generation and patching pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement CI Monitor Agent
  - [ ] 12.1 Create CIMonitorAgent class
    - Set up GitHub API client with authentication
    - Implement poll_ci_status() function
    - Extract owner/repo from repository URL
    - Get workflow runs for specific branch
    - Poll every 10 seconds with timeout
    - Detect PASSED and FAILED statuses
    - Record timestamps for each check
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 12.2 Write property test for CI polling timestamp recording
    - **Property 36: CI Polling Timestamp Recording**
    - **Validates: Requirements 9.5**
  
  - [ ]* 12.3 Write unit tests for CI monitoring
    - Test status polling
    - Test PASSED detection
    - Test FAILED detection
    - Test timeout handling
    - _Requirements: 9.1, 9.3, 9.4_

- [ ] 13. Implement Orchestrator Agent with LangGraph
  - [ ] 13.1 Create OrchestratorAgent with LangGraph workflow
    - Define OrchestratorState schema
    - Create StateGraph with all agent nodes
    - Add edges between agents in correct sequence
    - Implement should_retry() conditional routing
    - Initialize retry counter to zero
    - Track total execution time
    - Generate results.json on completion
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 11.1_
  
  - [ ]* 13.2 Write property test for retry loop termination on success
    - **Property 9: Retry Loop Termination on Success**
    - **Validates: Requirements 10.3**
  
  - [ ]* 13.3 Write property test for retry loop termination on limit
    - **Property 10: Retry Loop Termination on Limit**
    - **Validates: Requirements 10.5**
  
  - [ ]* 13.4 Write property test for agent execution sequence
    - **Property 23: Agent Execution Sequence**
    - **Validates: Requirements 10.2**
  
  - [ ]* 13.5 Write property test for orchestrator time tracking
    - **Property 37: Orchestrator Time Tracking**
    - **Validates: Requirements 10.7**
  
  - [ ]* 13.6 Write unit tests for orchestrator logic
    - Test retry counter initialization
    - Test agent sequence execution
    - Test stop on CI PASSED
    - Test stop at retry limit
    - Test time tracking
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7_

- [ ] 14. Implement FastAPI backend endpoints
  - [ ] 14.1 Create FastAPI application with endpoints
    - Implement POST /api/heal endpoint
    - Implement GET /api/status/{job_id} endpoint
    - Set up background task execution for orchestrator
    - Implement job ID generation (UUID)
    - Store job status in memory or Redis
    - Add CORS middleware for frontend
    - Add input validation with Pydantic
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 16.5_
  
  - [ ]* 14.2 Write property test for API job ID response
    - **Property 26: API Job ID Response**
    - **Validates: Requirements 15.2**
  
  - [ ]* 14.3 Write unit tests for API endpoints
    - Test POST /api/heal with valid inputs
    - Test POST /api/heal with invalid inputs
    - Test GET /api/status/{job_id} with valid ID
    - Test GET /api/status/{job_id} with invalid ID
    - Test CORS headers
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 15. Implement error handling and logging
  - [ ] 15.1 Add comprehensive error handling
    - Wrap all agent operations in try-catch
    - Return structured error responses
    - Clean up resources on errors (Docker containers, git clones)
    - Implement error codes for all failure types
    - Add error logging with timestamps and context
    - Ensure tokens are excluded from logs
    - _Requirements: 17.5, 18.2_
  
  - [ ]* 15.2 Write property test for error logging completeness
    - **Property 29: Error Logging Completeness**
    - **Validates: Requirements 17.5**
  
  - [ ]* 15.3 Write property test for token exclusion from logs
    - **Property 30: Token Exclusion from Logs**
    - **Validates: Requirements 18.2**
  
  - [ ]* 15.4 Write property test for input sanitization
    - **Property 31: Input Sanitization**
    - **Validates: Requirements 18.5**

- [ ] 16. Checkpoint - Verify complete backend workflow
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement frontend data models and types
  - [ ] 17.1 Create TypeScript interfaces and types
    - Define JobRequest, JobResponse, StatusResponse interfaces
    - Define HealingResults, Fix, IterationStatus interfaces
    - Define ScoreBreakdown interface
    - Define BugType and CIStatus enums
    - _Requirements: Data Models section_

- [ ] 18. Set up frontend state management with Zustand
  - [ ] 18.1 Create Zustand store
    - Define store state shape (loading, results, error)
    - Implement actions (setLoading, setResults, setError, clearError)
    - Export hooks for component access
    - _Requirements: 14.1, 14.2, 14.3, 14.4_
  
  - [ ]* 18.2 Write property test for state update propagation
    - **Property 25: State Update Propagation**
    - **Validates: Requirements 14.2, 14.3, 14.4**

- [ ] 19. Implement API client service
  - [ ] 19.1 Create API service with Axios
    - Implement startHealing() function for POST /api/heal
    - Implement getJobStatus() function for GET /api/status/{job_id}
    - Add error handling for network failures
    - Add request/response interceptors
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 20. Implement InputForm component
  - [ ] 20.1 Create InputForm component with validation
    - Add input fields for repository URL, team name, leader name
    - Implement GitHub URL validation
    - Display validation errors inline
    - Disable submit button when loading
    - Call API on form submission
    - Show loading indicator
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 20.2 Write property test for GitHub URL validation
    - **Property 1: GitHub URL Validation**
    - **Validates: Requirements 1.2**
  
  - [ ]* 20.3 Write property test for loading state prevention
    - **Property 19: Loading State Prevention**
    - **Validates: Requirements 1.4**
  
  - [ ]* 20.4 Write property test for input validation error display
    - **Property 20: Input Validation Error Display**
    - **Validates: Requirements 1.5**
  
  - [ ]* 20.5 Write unit tests for InputForm
    - Test form renders with all fields
    - Test validation on invalid URL
    - Test validation on empty fields
    - Test form submission triggers API call
    - Test loading state disables button
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 21. Implement RunSummaryCard component
  - [ ] 21.1 Create RunSummaryCard component
    - Display repository, team name, leader name, branch name
    - Display total failures, fixes applied, total time
    - Display CI status badge (green for PASSED, red for FAILED)
    - Style with Tailwind CSS
    - _Requirements: 12.1, 12.2_
  
  - [ ]* 21.2 Write property test for CI status badge color
    - **Property 18: CI Status Badge Color**
    - **Validates: Requirements 12.2**
  
  - [ ]* 21.3 Write unit tests for RunSummaryCard
    - Test all fields are displayed
    - Test green badge for PASSED
    - Test red badge for FAILED
    - _Requirements: 12.1, 12.2_

- [ ] 22. Implement ScoreBreakdownPanel component
  - [ ] 22.1 Create ScoreBreakdownPanel component
    - Calculate base score (100)
    - Calculate speed bonus (+10 if < 5 minutes)
    - Calculate commit penalty (-2 per commit over 20)
    - Display score breakdown with Recharts bar chart
    - Display final score prominently
    - _Requirements: 12.3, 12.4, 12.5, 12.6_
  
  - [ ]* 22.2 Write property test for speed bonus calculation
    - **Property 14: Speed Bonus Calculation**
    - **Validates: Requirements 12.4**
  
  - [ ]* 22.3 Write property test for commit penalty calculation
    - **Property 15: Commit Penalty Calculation**
    - **Validates: Requirements 12.5**
  
  - [ ]* 22.4 Write unit tests for ScoreBreakdownPanel
    - Test base score is 100
    - Test speed bonus calculation
    - Test commit penalty calculation
    - Test final score calculation
    - Test chart rendering
    - _Requirements: 12.3, 12.4, 12.5, 12.6_

- [ ] 23. Implement FixesTable component
  - [ ] 23.1 Create FixesTable component
    - Display table with columns: File, Bug Type, Line Number, Commit Message, Status
    - Color code status (green for Fixed, red for Failed)
    - Truncate long file paths with tooltip
    - Make table responsive (stack on mobile)
    - Style with Tailwind CSS
    - _Requirements: 12.7, 12.8_
  
  - [ ]* 23.2 Write property test for fix status color coding
    - **Property 17: Fix Status Color Coding**
    - **Validates: Requirements 12.8**
  
  - [ ]* 23.3 Write unit tests for FixesTable
    - Test table renders with all columns
    - Test green color for Fixed status
    - Test red color for Failed status
    - Test responsive layout
    - _Requirements: 12.7, 12.8_

- [ ] 24. Implement CITimelineComponent
  - [ ] 24.1 Create CITimelineComponent
    - Display vertical timeline with all iterations
    - Show pass/fail badge for each iteration
    - Display timestamp and failure count
    - Show "X/Y" iterations used out of retry limit
    - Style with Tailwind CSS
    - _Requirements: 12.9, 12.10_
  
  - [ ]* 24.2 Write property test for timeline iteration display
    - **Property 39: Timeline Iteration Display**
    - **Validates: Requirements 12.9, 12.10**
  
  - [ ]* 24.3 Write unit tests for CITimelineComponent
    - Test timeline renders all iterations
    - Test pass/fail badges
    - Test timestamps display
    - Test iteration count display
    - _Requirements: 12.9, 12.10_

- [ ] 25. Implement Dashboard page with all components
  - [ ] 25.1 Create Dashboard page component
    - Integrate InputForm component
    - Integrate RunSummaryCard component
    - Integrate ScoreBreakdownPanel component
    - Integrate FixesTable component
    - Integrate CITimelineComponent component
    - Implement status polling logic
    - Handle loading, success, and error states
    - _Requirements: 12.1, 12.3, 12.7, 12.9, 15.5_
  
  - [ ]* 25.2 Write property test for status polling continuation
    - **Property 27: Status Polling Continuation**
    - **Validates: Requirements 15.5**
  
  - [ ]* 25.3 Write property test for dashboard results display completeness
    - **Property 38: Dashboard Results Display Completeness**
    - **Validates: Requirements 12.1, 12.3, 12.7, 12.9**

- [ ] 26. Implement responsive layout and styling
  - [ ] 26.1 Add responsive design with Tailwind
    - Configure Tailwind breakpoints
    - Implement multi-column layout for desktop
    - Implement single-column layout for mobile
    - Ensure no content overflow at any viewport size
    - Test on screens from 320px to 1920px
    - _Requirements: 13.1, 13.2, 13.3, 13.5_
  
  - [ ]* 26.2 Write property test for responsive layout adaptation
    - **Property 24: Responsive Layout Adaptation**
    - **Validates: Requirements 13.3, 13.5**

- [ ] 27. Implement error handling in frontend
  - [ ] 27.1 Add error handling and user feedback
    - Display error messages for clone failures
    - Display error messages for API failures
    - Display timeout messages with partial results
    - Add retry button for network errors
    - Style error messages with Tailwind
    - _Requirements: 17.1, 17.2, 17.3, 17.4_
  
  - [ ]* 27.2 Write property test for error message user-friendliness
    - **Property 28: Error Message User-Friendliness**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4**
  
  - [ ]* 27.3 Write unit tests for error handling
    - Test clone failure error display
    - Test API failure error display
    - Test timeout error display
    - Test network error retry option
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

- [ ] 28. Checkpoint - Verify complete frontend functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 29. Set up Docker configuration
  - [ ] 29.1 Create Dockerfiles and docker-compose
    - Create Dockerfile for backend
    - Create Dockerfile for frontend (if needed)
    - Create docker-compose.yml for local development
    - Configure environment variables
    - _Requirements: 4.1_

- [ ] 30. Deploy frontend to Vercel
  - [ ] 30.1 Configure Vercel deployment
    - Create vercel.json configuration
    - Set up environment variables in Vercel
    - Configure build command and output directory
    - Deploy to production
    - Verify HTTPS access
    - _Requirements: 16.1, 16.2, 16.3_

- [ ] 31. Create comprehensive documentation
  - [ ] 31.1 Write README.md
    - Add project overview and features
    - Add architecture diagram (use Mermaid or image)
    - Add setup instructions for local development
    - Add environment variable configuration guide
    - Add deployment instructions
    - Add API endpoint documentation
    - Add troubleshooting section
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.7_
  
  - [ ] 31.2 Add inline code comments
    - Comment complex logic in all agents
    - Comment LangGraph workflow setup
    - Comment error handling strategies
    - _Requirements: 19.6_

- [ ] 32. Run integration tests and end-to-end testing
  - [ ]* 32.1 Write integration tests for complete workflow
    - Test successful healing flow with known repository
    - Test retry loop with multiple iterations
    - Test error scenarios (invalid repo, no tests, LLM failure)
    - Test results.json generation
    - _Requirements: All_

- [ ] 33. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.
  - Verify all 40 correctness properties have property-based tests
  - Verify frontend and backend integrate correctly
  - Verify deployment is accessible
  - Verify documentation is complete

## Notes

- Tasks marked with `*` are optional test-related sub-tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- The implementation follows a bottom-up approach: data models → agents → orchestration → API → frontend
- LangGraph provides stateful multi-agent orchestration with built-in retry and error handling
- Docker sandboxing ensures safe code execution
- Responsive design ensures accessibility on all devices
