from app.agents.learning_curator.tools import fetch_curated_resources

class LearningCuratorAgent:
    def curate(self, user_id: str, target_role: str) -> list[dict]:
        return fetch_curated_resources(target_role)

learning_curator_agent = LearningCuratorAgent()
