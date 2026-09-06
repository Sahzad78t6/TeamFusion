"""Tools for the Learning Curator Agent."""
import logging
from app.services.curator_engine import curator_engine

logger = logging.getLogger(__name__)


async def curate_resources(target_role: str, tasks: list[dict], user_id: str = "demo_user", topic: str = "") -> list[dict]:
    """Curate personalized resources via CuratorEngine."""
    return await curator_engine.curate_personalized_resources(user_id=user_id, topic=topic, target_role=target_role)

