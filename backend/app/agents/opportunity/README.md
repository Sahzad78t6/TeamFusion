# Opportunity Agent

Autonomous agent responsible for matching users with relevant career opportunities (hackathons, open-source projects, internships, and events) based on their Identity Twin profile and skills.

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing `user_id`. Reads current Identity Twin from database.

## Output
`AgentResponse` with `data` containing the OpportunityBundle (list of matched opportunities).
