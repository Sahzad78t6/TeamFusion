# Reflection Agent

Autonomous agent responsible for analyzing user reflections, updating ML burnout metrics, and storing significant emotional state changes to vector memory.

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing reflection data (mood, energy, tasks completed, summary).

## Output
`AgentResponse` with `data` containing the Reflection object, AI insights, and updated burnout risk levels.
