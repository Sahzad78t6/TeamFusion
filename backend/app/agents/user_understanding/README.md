# User Understanding Agent

Autonomous agent responsible for analyzing developer onboarding inputs, computing Identity Twin alignment scores, identifying skill gaps, and persisting cognitive facts to vector memory.

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing onboarding questions and optional chat history.

## Output
`AgentResponse` with `data` containing the updated UserProfile and IdentityTwin objects.
