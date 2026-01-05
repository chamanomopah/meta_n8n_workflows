# Feature Planning - Universal

Create a new plan in specs/*.md to implement the `Feature` for any project/application using the exact specified markdown `Plan Format`. The system will automatically analyze the project structure to identify relevant files.

**CRITICAL OUTPUT REQUIREMENT:**
- Your response must contain ONLY the full absolute path of the created specs file
- Example: `C:\.n8n_workflows\projects\002-app-modifier\specs\feature-name.md`
- No additional text, explanations, or summaries - ONLY the file path

**SPECS FOLDER REQUIREMENT:**
- The file MUST be created at: `$PROJECT_PATH\specs`
- Full path for this project: `C:\.n8n_workflows\projects\002-app-modifier\specs`
- If the `specs` folder does not exist, create it FIRST before creating the file

## Instructions

- You're writing a plan to implement a net new feature that will add value to the application.
- Create the plan in the `specs/*.md` file. Name it appropriately based on the `Feature`.
- Use the `Plan Format` below to create the plan.
- **PROJECT PATH**: The project to analyze is located at: `$PROJECT_PATH`
- Research the codebase to understand existing patterns, architecture, and conventions before planning the feature. and each folder of the especificy code base.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to implement the feature successfully.
- Use your reasoning model: THINK HARD about the feature requirements, design, and implementation approach.
- Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
- Design for extensibility and maintainability.
- **DISCOVERY PHASE REQUIRED**: Before creating the plan, you MUST:
  0. focus to find the readme.md file of `$PROJECT_PATH` , cause it will guide you to discover easily the project structure
  1. Explore the project structure at `$PROJECT_PATH` to understand the architecture including folders
  2. Identify the main entry points (main files, index files, app root, readme.md)
  3. Detect the technology stack (language, framework, build tools)
  4. Find configuration files (package.json, requirements.txt, pom.xml, go.mod, etc.)
  5. Locate documentation (README.md, docs folder, CONTRIBUTING.md)
  6. Identify the source code organization (src/, app/, lib/, etc.)
  7. Find existing tests and their location
  8. Determine the dependency management system
- Based on the discovery, adapt the plan format to match the project's structure and conventions
- If you need a new library, use the project's dependency manager (npm, pip, cargo, go get, maven, etc.) and report it in the `Notes` section

## Discovery Phase

Before creating the plan, perform automated analysis of the project at `$PROJECT_PATH`:

1. **Project Structure Analysis**
   - Use `Glob` and `Grep` to map the directory structure
   - Identify main source code directories
   - Find configuration and build files
   - Locate test directories

2. **Technology Stack Detection**
   - Detect programming language from file extensions
   - Identify frameworks from dependencies and imports
   - Determine build system and tools

3. **Entry Points Identification**
   - Find main application files
   - Locate API routes/controllers
   - Identify UI components (if applicable)
   - Find database schemas/models

4. **Convention Discovery**
   - Identify coding patterns from existing code
   - Determine testing framework used
   - Find linting/formatting configuration
   - Understand the project's architectural pattern

## Plan Format

```md
# Feature: <feature name>

## Feature Description
<describe the feature in detail, including its purpose and value to users>

## User Story
As a <type of user>
I want to <action/goal>
So that <benefit/value>

## Problem Statement
<clearly define the specific problem or opportunity this feature addresses>

## Solution Statement
<describe the proposed solution approach and how it solves the problem>

## Relevant Files
Use these files to implement the feature:

<find and list the files that are relevant to the feature describe why they are relevant in bullet points. If there are new files that need to be created to implement the feature, list them in an h3 'New Files' section.>

## Implementation Plan
### Phase 1: Foundation
<describe the foundational work needed before implementing the main feature>

### Phase 2: Core Implementation
<describe the main implementation work for the feature>

### Phase 3: Integration
<describe how the feature will integrate with existing functionality>

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. use as many h3 headers as needed to implement the feature. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include creating tests throughout the implementation process. Your last step should be running the `Validation Commands` to validate the feature works correctly with zero regressions.>

## Testing Strategy
### Unit Tests
<describe unit tests needed for the feature>

### Integration Tests
<describe integration tests needed for the feature>

### Edge Cases
<list edge cases that need to be tested>

## Acceptance Criteria
<list specific, measurable criteria that must be met for the feature to be considered complete>

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

<list commands you'll use to validate with 100% confidence the feature is implemented correctly with zero regressions. every command must execute without errors so be specific about what you want to run to validate the feature works as expected. Include commands to test the feature end-to-end. ADAPT these commands based on the project's testing framework and build system discovered in the Discovery Phase.>
- `<adapt to project's test command>` - Run tests to validate the feature works with zero regressions
- `<adapt to project's lint/typecheck command>` - Run linting/type checking to ensure code quality
- `<adapt to project's build command>` - Build the project to ensure no build errors

## Notes
<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the developer>

**Technology Stack Discovered:**
<list the technologies, frameworks, and tools discovered during the Discovery Phase>

**Project-Specific Conventions:**
<document any project-specific conventions, patterns, or configurations discovered>
```

## Variables

**Feature to Implement:**
$ARGUMENTS

**Project Path:**
$PROJECT_PATH