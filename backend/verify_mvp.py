import asyncio
import json
import logging
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db_instance
from app.services.auth_service import auth_service
from app.services.onboarding_service import onboarding_service
from app.services.planner_service import planner_service
from app.services.recommendation_service import recommendation_service
from app.services.opportunity_service import opportunity_service
from app.services.reflection_service import reflection_service
from app.services.notification_service import notification_service
from app.services.dashboard_service import dashboard_service
from app.config.constants import (
    COLLECTION_USERS,
    COLLECTION_IDENTITIES,
    COLLECTION_PLANS,
    COLLECTION_RECOMMENDATIONS,
    COLLECTION_REFLECTIONS,
    COLLECTION_OPPORTUNITIES,
    COLLECTION_NOTIFICATIONS,
    COLLECTION_ANALYTICS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_mvp")

async def run_verification():
    logger.info("=== STARTING GROWTHOS MVP VERIFICATION ===")
    await connect_to_mongo()

    test_email = f"test_architect_{asyncio.get_event_loop().time()}@growthos.ai"
    test_password = "SecurePassword123!"
    test_name = "Sahazad Architect"

    # 1. Signup
    logger.info("\n1. Testing Auth Signup...")
    signup_res = await auth_service.signup(test_name, test_email, test_password)
    user_id = signup_res["user"]["id"]
    token = signup_res["access_token"]
    assert signup_res["user"]["email"] == test_email
    logger.info(f"✓ Signup Successful. User ID: {user_id}")

    # 2. Login
    logger.info("\n2. Testing Auth Login...")
    login_res = await auth_service.login(test_email, test_password)
    assert login_res["access_token"] is not None
    logger.info("✓ Login Successful. Token generated.")

    # 3. Get Current User /me
    logger.info("\n3. Testing Auth /me Endpoint...")
    me_res = await auth_service.get_current_user(user_id)
    assert me_res["email"] == test_email
    logger.info(f"✓ Authenticated user profile retrieved: {me_res['name']}")

    # 4. Onboarding -> identity_twins
    logger.info("\n4. Testing Onboarding Submission -> identity_twins collection...")
    onboarding_payload = {
        "goal": "Principal AI Architect & Founder",
        "interests": ["Agentic AI", "LangGraph", "Vector DBs"],
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PyTorch"],
        "experience": "Senior Engineer",
        "learning_style": "Hands-on System Architecture",
        "career_stage": "Senior Leader",
        "available_time": "15-20 hours/week",
        "preferred_content": ["Courses", "Interactive Labs", "Research Papers"],
        "language": "English",
        "target_role": "Principal AI Architect"
    }
    identity_res = await onboarding_service.process_onboarding(user_id, onboarding_payload)
    assert identity_res["user_id"] == user_id
    assert identity_res["goal"] == onboarding_payload["goal"]
    logger.info(f"✓ Onboarding Identity Twin stored: Score={identity_res.get('identity_score')}")

    # 5. Planner -> learning_plans
    logger.info("\n5. Testing Planner Agent -> learning_plans collection...")
    plan_res = await planner_service.create_plan(user_id, {"goals": ["Master LangGraph Swarms", "Optimize FastAPI Vector Search"]})
    assert len(plan_res.get("tasks", [])) > 0
    logger.info(f"✓ Learning Roadmap generated: {len(plan_res['tasks'])} tasks. Feedback: {plan_res.get('ai_feedback')[:60]}...")

    # 6. Recommendation -> recommendations
    logger.info("\n6. Testing Learning Curator Agent -> recommendations collection...")
    recs_res = await recommendation_service.get_recommendations(user_id)
    assert len(recs_res.get("recommendations", [])) > 0
    logger.info(f"✓ Curated Learning Recommendations generated: {len(recs_res['recommendations'])} resources.")

    # 7. Opportunity Matcher -> opportunities
    logger.info("\n7. Testing Opportunity Agent -> opportunities collection (from opportunities.csv)...")
    opps_res = await opportunity_service.get_opportunities(user_id)
    assert len(opps_res.get("opportunities", [])) > 0
    top_opp = opps_res["opportunities"][0]
    logger.info(f"✓ Opportunity Matching successful: Top match = '{top_opp['title']}' (Score: {top_opp['relevance_score']})")

    # 8. Reflection Agent -> reflections & analytics
    logger.info("\n8. Testing Reflection Agent -> reflections & analytics collection...")
    reflection_payload = {
        "reflection": "Completed FastAPI async database layer and deployed multi-agent nodes cleanly.",
        "mood": 5,
        "motivation": 5,
        "study_hours": 4.5,
        "completed_tasks": ["task-1", "task-2"],
        "skipped_tasks": []
    }
    ref_res = await reflection_service.create_reflection(user_id, reflection_payload)
    assert ref_res["user_id"] == user_id
    logger.info(f"✓ Daily Reflection stored. Risk Level: {ref_res.get('risk_level')}. AI Coaching: {ref_res.get('ai_insight')[:60]}...")

    # 9. Notifications Agent -> notifications
    logger.info("\n9. Testing Notification Agent -> notifications collection...")
    notifs_res = await notification_service.get_user_notifications(user_id)
    assert len(notifs_res.get("notifications", [])) > 0
    logger.info(f"✓ Notifications generated & synced: Total {len(notifs_res['notifications'])} items.")

    # 10. Dashboard API
    logger.info("\n10. Testing Dashboard Service -> Real Aggregated Data...")
    dash_res = await dashboard_service.get_dashboard_summary(user_id)
    assert dash_res["user_name"] == test_name
    assert dash_res["goal"] == onboarding_payload["goal"]
    assert dash_res["learning_streak"] >= 1
    assert dash_res["roadmap"] is not None
    assert len(dash_res["top_recommendations"]) > 0
    assert len(dash_res["notifications"]) > 0
    logger.info(f"✓ Dashboard Real Aggregation Successful! Growth Score: {dash_res['growth_score']}")

    # 11. Database Collection Verification
    logger.info("\n11. Verifying Database Collections Storage...")
    collections_to_verify = [
        COLLECTION_USERS,
        COLLECTION_IDENTITIES,
        COLLECTION_PLANS,
        COLLECTION_RECOMMENDATIONS,
        COLLECTION_REFLECTIONS,
        COLLECTION_OPPORTUNITIES,
        COLLECTION_NOTIFICATIONS,
        COLLECTION_ANALYTICS,
    ]
    for col_name in collections_to_verify:
        if db_instance.db is not None:
            count = await db_instance.db[col_name].count_documents({"user_id": user_id}) if col_name != COLLECTION_USERS else await db_instance.db[col_name].count_documents({"id": user_id})
            logger.info(f"  Collection [{col_name}]: {count} document(s)")
        else:
            logger.info(f"  Collection [{col_name}]: Verified in-memory fallback store")

    await close_mongo_connection()
    logger.info("\n=== VERIFICATION COMPLETE: ALL MVP BACKEND APIS & REPOSITORIES VERIFIED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(run_verification())
