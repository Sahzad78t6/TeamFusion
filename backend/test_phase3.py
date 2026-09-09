import time
import requests
from pymongo import MongoClient

BASE_URL = 'http://127.0.0.1:8000'

def run_tests():
    # 1. Sign up/login Admin
    uid = int(time.time())
    admin_signup = requests.post(f'{BASE_URL}/auth/signup', json={
        'name': f'Admin {uid}',
        'email': f'admin_{uid}@growthos.io',
        'password': 'Password123!',
        'role': 'INSTITUTION_ADMIN'
    })
    assert admin_signup.status_code == 200, admin_signup.text
    admin_token = admin_signup.json()['access_token']

    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    print('1. Admin Token obtained successfully.')

    # 2. Create Cohort
    cohort_resp = requests.post(f'{BASE_URL}/institutions/cohorts', headers=admin_headers, json={
        'name': f'Alpha {uid}',
        'year': '1st Year',
        'branch': 'Computer Science & Engineering',
        'section': 'A'
    })
    print('2. Create Cohort Status:', cohort_resp.status_code)
    assert cohort_resp.status_code == 200, cohort_resp.text
    cohort = cohort_resp.json()
    cohort_id = cohort['id']
    print(f'   Created Cohort: {cohort["name"]} (ID: {cohort_id})')

    # 3. Create Mode B Assessment
    mode_b_resp = requests.post(f'{BASE_URL}/institutions/assessments', headers=admin_headers, json={
        'title': f'DSA Benchmark Quiz {uid}',
        'description': 'Mid-term DSA foundational assessment',
        'cohort_id': cohort_id,
        'skill': 'Data Structures',
        'year': '1st Year',
        'topic_code': 'dsa',
        'question_count': 5
    })
    print('3. Create Assessment (Mode B) Status:', mode_b_resp.status_code)
    assert mode_b_resp.status_code == 200, mode_b_resp.text
    assessment = mode_b_resp.json()
    assessment_id = assessment['id']
    question_ids = assessment['question_ids']
    print(f'   Created Assessment: {assessment["title"]} with {len(question_ids)} questions sampled.')
    assert len(question_ids) == 5

    # 4. Student Auth & Cohort Link
    student_signup = requests.post(f'{BASE_URL}/auth/signup', json={
        'name': f'Student {uid}',
        'email': f'student_{uid}@growthos.io',
        'password': 'Password123!',
        'role': 'STUDENT',
        'cohort_id': cohort_id
    })
    assert student_signup.status_code == 200, student_signup.text
    student_token = student_signup.json()['access_token']
    student_headers = {'Authorization': f'Bearer {student_token}'}
    print(f'4. Student Token obtained successfully (Cohort ID: {cohort_id}).')

    # 5. Fetch Assessments as Student
    assessments_resp = requests.get(f'{BASE_URL}/institutions/assessments', headers=student_headers)
    print('5. Get Assessments Status:', assessments_resp.status_code)
    assert assessments_resp.status_code == 200
    student_assessments = assessments_resp.json()
    print('   Returned assessments count:', len(student_assessments))
    assert len(student_assessments) >= 1, f"Expected at least 1 assessment, got: {student_assessments}"
    sample_a = next(a for a in student_assessments if a['id'] == assessment_id)
    print(f'   Retrieved assessment "{sample_a["title"]}" with {len(sample_a["questions"])} questions.')

    # Verify no correct_option leak
    has_leak = any('correct_option' in q for q in sample_a['questions'])
    print('   Security Check: correct_option exposed in response?', has_leak)
    assert not has_leak, 'CRITICAL: correct_option is exposed to student!'

    # 6. Test Submissions
    # A) All wrong
    wrong_answers = {q['id']: 99 for q in sample_a['questions']}
    sub_wrong = requests.post(f'{BASE_URL}/institutions/assessments/{assessment_id}/submissions', headers=student_headers, json={'answers': wrong_answers})
    print('6A. Submission (all wrong) Status:', sub_wrong.status_code, 'Score:', sub_wrong.json().get('score'))
    assert sub_wrong.json().get('score') == 0.0

    # B) All correct (fetch answer key directly from MongoDB via pymongo)
    client = MongoClient('mongodb://localhost:27017')
    db = client['growthos_v2']
    from bson import ObjectId
    q_docs = list(db['quiz_bank'].find({'_id': {'$in': [ObjectId(qid) for qid in question_ids]}}))
    correct_answers = {str(doc['_id']): doc['correct_option'] for doc in q_docs}

    sub_correct = requests.post(f'{BASE_URL}/institutions/assessments/{assessment_id}/submissions', headers=student_headers, json={'answers': correct_answers})
    print('6B. Submission (all correct) Status:', sub_correct.status_code, 'Score:', sub_correct.json().get('score'))
    assert sub_correct.json().get('score') == 100.0

    # 7. Check Analytics as Admin
    analytics_resp = requests.get(f'{BASE_URL}/institutions/analytics', headers=admin_headers)
    print('7. Institution Analytics Status:', analytics_resp.status_code)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    print('   Analytics:', analytics)
    assert analytics['cohort_count'] >= 1
    assert analytics['assessment_submissions'] >= 2

    # 8. Test Join Cohort endpoint
    join_resp = requests.post(f'{BASE_URL}/institutions/cohorts/join', headers=student_headers, json={'cohort_id': cohort_id})
    print('8. Join Cohort Status:', join_resp.status_code, join_resp.json())
    assert join_resp.status_code == 200

    print('\nALL PHASE 3 BACKEND API CHECKS PASSED SUCCESSFULLY!')

if __name__ == '__main__':
    run_tests()
