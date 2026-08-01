# Planner Agent

Autonomous agent responsible for generating structured daily learning roadmaps, prioritizing tasks, and persisting plans to MongoDB.

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing `user_id` and optional `goals`.

## Output
`AgentResponse` with `data` containing the updated Roadmap and daily task list.
