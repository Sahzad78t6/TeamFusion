# Learning Curator Agent

Autonomous agent responsible for curating personalized learning resources based on the user's roadmap, target role, and identified skill gaps.

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing `user_id`. Reads current roadmap from database.

## Output
`AgentResponse` with `data` containing the updated LearningBundle (list of curated resources).
