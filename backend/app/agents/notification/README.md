# Notification Agent

Autonomous agent responsible for generating contextual push notifications and alerts based on system events, user progress, and risk factors (e.g., burnout alerts).

## Interface
All agents follow the standard `execute(input_data: dict) -> AgentResponse` interface.

## Input
`input_data` containing the `event_type` and relevant context.

## Output
`AgentResponse` with `data` containing the NotificationBundle.
