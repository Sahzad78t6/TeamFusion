# Supervisor Agent

Skeleton agent responsible for routing user queries to the appropriate specialized agent.

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing `message` (user query).

## Output
`AgentResponse` with `data` containing `routed_to` (the name of the next agent).
