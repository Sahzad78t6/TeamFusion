import asyncio
from datetime import datetime, timezone
import logging
import os
import random
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.db import get_db
from app.models import CodeSubmitRequest, CodeSubmitResponse, ContestCreateRequest, TestCaseResult

logger = logging.getLogger("growthos.contests")

router = APIRouter(tags=["contests"])

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") not in ["INSTITUTION_ADMIN", "PLATFORM_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

RUNNER_WRAPPER = """import sys

def _audit_hook(event, args):
    if any(event.startswith(prefix) for prefix in ("socket.", "http.", "urllib.")):
        raise PermissionError("Network access blocked in contest sandbox: " + str(event))

sys.addaudithook(_audit_hook)

with open(r"__SOLUTION_PATH__", "r", encoding="utf-8") as _f:
    _code = _f.read()

exec(compile(_code, "solution.py", "exec"), {})
"""

def _execute_test_case_sync(code: str, test_input: str, expected_output: str, timeout_sec: float = 2.0) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir:
        solution_path = os.path.join(tmpdir, "solution.py")
        wrapper_path = os.path.join(tmpdir, "wrapper.py")

        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)

        with open(wrapper_path, "w", encoding="utf-8") as f:
            f.write(RUNNER_WRAPPER.replace("__SOLUTION_PATH__", solution_path))

        env = {
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": "",
            "PYTHONNOUSERSITE": "1",
        }

        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-s", wrapper_path],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=tmpdir,
                env=env,
            )
            actual = proc.stdout.strip()
            expected = expected_output.strip()
            return (proc.returncode == 0) and (actual == expected)
        except subprocess.TimeoutExpired:
            return False
        except Exception as exc:
            logger.warning("Sandbox execution error: %s", exc)
            return False

def _parse_datetime(dt_val: Any) -> datetime:
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is None:
            return dt_val.replace(tzinfo=timezone.utc)
        return dt_val
    if isinstance(dt_val, str):
        cleaned = dt_val.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    raise ValueError(f"Cannot parse datetime from {dt_val}")

# POST /institutions/contests (Admin)
@router.post("/institutions/contests")
@router.post("/contests")
async def create_contest_session(
    payload: ContestCreateRequest,
    current_user: dict = Depends(require_admin),
):
    db = get_db()

    try:
        start_dt = _parse_datetime(payload.start_time)
        end_dt = _parse_datetime(payload.end_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid start_time or end_time format: {e}")

    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    # Randomly sample question_count from coding_bank
    all_questions = await db["coding_bank"].find({}).to_list(100)
    if not all_questions:
        raise HTTPException(status_code=404, detail="No questions available in coding_bank")

    sample_size = min(payload.question_count, len(all_questions))
    selected_questions = random.sample(all_questions, sample_size)
    question_ids = [ObjectId(q["_id"]) for q in selected_questions]

    session_doc = {
        "cohort_id": payload.cohort_id,
        "question_ids": question_ids,
        "start_time": start_dt,
        "end_time": end_dt,
        "created_at": datetime.now(timezone.utc),
    }

    res = await db["contest_sessions"].insert_one(session_doc)
    session_id = str(res.inserted_id)

    # Return created session details without expected_output
    return {
        "id": session_id,
        "cohort_id": payload.cohort_id,
        "question_ids": [str(qid) for qid in question_ids],
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "created_at": session_doc["created_at"].isoformat(),
    }

# GET /contests/active (Student)
@router.get("/contests/active")
async def get_active_contest(
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    cohort_id = current_user.get("cohort_id")
    if not cohort_id:
        return None

    now = datetime.now(timezone.utc)

    # Look for sessions assigned to student's cohort
    cohort_queries = [str(cohort_id)]
    if ObjectId.is_valid(cohort_id):
        cohort_queries.append(ObjectId(cohort_id))

    sessions = await db["contest_sessions"].find(
        {"cohort_id": {"$in": cohort_queries}}
    ).sort("created_at", -1).to_list(50)

    active_session = None
    for s in sessions:
        try:
            s_start = _parse_datetime(s.get("start_time"))
            s_end = _parse_datetime(s.get("end_time"))
            if s_start <= now <= s_end:
                active_session = s
                break
        except Exception:
            continue

    if not active_session:
        return None

    # Fetch questions for active session
    q_docs = await db["coding_bank"].find(
        {"_id": {"$in": active_session.get("question_ids", [])}}
    ).to_list(100)

    # Map preserving question order, and never expose expected_output
    q_map = {str(q["_id"]): q for q in q_docs}
    formatted_questions = []
    for qid in active_session.get("question_ids", []):
        q = q_map.get(str(qid))
        if q:
            formatted_questions.append({
                "id": str(q["_id"]),
                "title": q.get("title", ""),
                "description": q.get("description", ""),
                "difficulty": q.get("difficulty", "Easy"),
                "starter_code": q.get("starter_code", ""),
            })

    s_start_dt = _parse_datetime(active_session["start_time"])
    s_end_dt = _parse_datetime(active_session["end_time"])

    return {
        "id": str(active_session["_id"]),
        "cohort_id": str(active_session.get("cohort_id")),
        "start_time": s_start_dt.isoformat(),
        "end_time": s_end_dt.isoformat(),
        "questions": formatted_questions,
    }

# POST /contests/{id}/submit (Student)
@router.post("/contests/{id}/submit", response_model=CodeSubmitResponse)
async def submit_contest_code(
    id: str,
    payload: CodeSubmitRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()

    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid contest session id")
    if not ObjectId.is_valid(payload.question_id):
        raise HTTPException(status_code=400, detail="Invalid question_id")

    session = await db["contest_sessions"].find_one({"_id": ObjectId(id)})
    if not session:
        raise HTTPException(status_code=404, detail="Contest session not found")

    question = await db["coding_bank"].find_one({"_id": ObjectId(payload.question_id)})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    test_cases = question.get("test_cases", [])
    results: List[TestCaseResult] = []

    # Execute code asynchronously in threadpool to prevent blocking the event loop
    for index, tc in enumerate(test_cases):
        tc_input = tc.get("input", "")
        tc_expected = tc.get("expected_output", "")
        passed = await asyncio.to_thread(
            _execute_test_case_sync,
            payload.code,
            tc_input,
            tc_expected,
            2.0,
        )
        results.append(TestCaseResult(test_case_index=index, passed=passed))

    overall_passed = bool(results) and all(r.passed for r in results)

    # Persist in code_submissions
    submission_doc = {
        "contest_id": ObjectId(id),
        "question_id": ObjectId(payload.question_id),
        "user_id": ObjectId(current_user["_id"]),
        "code": payload.code,
        "passed": overall_passed,
        "results": [r.model_dump() for r in results],
        "submitted_at": datetime.now(timezone.utc),
    }
    await db["code_submissions"].insert_one(submission_doc)

    return CodeSubmitResponse(passed=overall_passed, results=results)
