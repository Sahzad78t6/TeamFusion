import React, { useEffect, useState } from 'react';
import { Building2, Plus, Users, Code2 } from 'lucide-react';
import {
  createAssessmentApi,
  createCohortApi,
  getCohortsApi,
  getInstitutionAnalyticsApi,
  createContestApi,
} from '../../services/api';
import { useApp } from '../../context/AppContext';
import { Button } from '../../components/common/Button';

export const InstitutionAdmin: React.FC = () => {
  const { authToken } = useApp();
  const [analytics, setAnalytics] = useState<any>();
  const [cohorts, setCohorts] = useState<any[]>([]);
  const [message, setMessage] = useState('');
  const [cohort, setCohort] = useState({ name: '', year: '', branch: '', section: '' });
  const [assessment, setAssessment] = useState({
    title: '',
    description: '',
    cohort_id: '',
    skill: '',
    year: '',
    topic_code: '',
    question_count: '',
    prompt: '',
    optionA: '',
    optionB: '',
  });
  const [contestForm, setContestForm] = useState({
    cohort_id: '',
    question_count: 2,
    duration_minutes: 60,
  });

  const addContest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authToken) return;
    try {
      const now = new Date();
      const endTime = new Date(now.getTime() + (contestForm.duration_minutes || 60) * 60 * 1000);
      await createContestApi(authToken, {
        cohort_id: contestForm.cohort_id,
        question_count: Number(contestForm.question_count) || 2,
        start_time: now.toISOString(),
        end_time: endTime.toISOString(),
      });
      setMessage('Coding Contest launched successfully! Cohort students can now enter from the Coding Contest tab.');
    } catch (e: any) {
      setMessage(`Contest launch failed: ${e.message}`);
    }
  };

  const refresh = () => {
    if (authToken) {
      Promise.all([getInstitutionAnalyticsApi(authToken), getCohortsApi(authToken)])
        .then(([a, c]) => {
          setAnalytics(a);
          setCohorts(c);
        })
        .catch(e => setMessage(e.message));
    }
  };

  useEffect(refresh, [authToken]);

  const addCohort = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authToken) return;
    try {
      await createCohortApi(authToken, cohort);
      setCohort({ name: '', year: '', branch: '', section: '' });
      setMessage('Cohort created successfully.');
      refresh();
    } catch (e: any) {
      setMessage(e.message);
    }
  };

  const addAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authToken) return;
    try {
      const isModeB = Boolean(assessment.year && assessment.topic_code && assessment.question_count);
      const payload = isModeB
        ? {
            title: assessment.title,
            description: assessment.description,
            cohort_id: assessment.cohort_id,
            skill: assessment.skill,
            year: assessment.year,
            topic_code: assessment.topic_code,
            question_count: parseInt(assessment.question_count, 10),
          }
        : {
            title: assessment.title,
            description: assessment.description,
            cohort_id: assessment.cohort_id,
            skill: assessment.skill,
            questions: [
              {
                id: 'q1',
                prompt: assessment.prompt,
                options: [assessment.optionA, assessment.optionB],
                correct_option: 0,
                skill: assessment.skill,
              },
            ],
          };

      await createAssessmentApi(authToken, payload);
      setMessage('Assessment published to the selected cohort.');
      setAssessment({
        title: '',
        description: '',
        cohort_id: '',
        skill: '',
        year: '',
        topic_code: '',
        question_count: '',
        prompt: '',
        optionA: '',
        optionB: '',
      });
      refresh();
    } catch (e: any) {
      setMessage(e.message);
    }
  };

  const isBankMode = Boolean(assessment.year || assessment.topic_code || assessment.question_count);

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold text-white">Institution Admin</h1>
        <p className="text-xs text-slate-400">Tenant-scoped cohorts, assessments, and participation analytics.</p>
      </div>
      {message && <p className="p-3 bg-indigo-500/10 rounded-xl text-indigo-200">{message}</p>}
      <div className="grid sm:grid-cols-3 gap-4">
        {[
          ['Students', analytics?.total_students],
          ['Cohorts', analytics?.cohort_count],
          ['Submissions', analytics?.assessment_submissions],
        ].map(([label, value]) => (
          <div key={String(label)} className="glass-panel rounded-2xl p-5 border border-white/10">
            <p className="text-slate-400 text-sm">{label}</p>
            <p className="text-3xl font-bold text-white">{value ?? '—'}</p>
          </div>
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-6">
        <form onSubmit={addCohort} className="glass-panel p-6 rounded-2xl border border-white/10 space-y-3">
          <h2 className="text-white font-bold flex gap-2">
            <Users className="w-5 h-5" />Create cohort
          </h2>
          {(['name', 'year', 'branch', 'section'] as const).map(key => (
            <input
              key={key}
              required={key !== 'section'}
              placeholder={key.replace('_', ' ')}
              value={cohort[key]}
              onChange={e => setCohort({ ...cohort, [key]: e.target.value })}
              className="w-full p-3 rounded-xl bg-white/5 text-white border border-white/10"
            />
          ))}
          <Button type="submit" variant="glow" leftIcon={<Plus className="w-4 h-4" />}>
            Create cohort
          </Button>
        </form>

        <form onSubmit={addAssessment} className="glass-panel p-6 rounded-2xl border border-white/10 space-y-3">
          <h2 className="text-white font-bold flex gap-2">
            <Building2 className="w-5 h-5" />Publish assessment
          </h2>
          <input
            required
            placeholder="Title"
            value={assessment.title}
            onChange={e => setAssessment({ ...assessment, title: e.target.value })}
            className="w-full p-3 rounded-xl bg-white/5 text-white border border-white/10"
          />
          <select
            required
            value={assessment.cohort_id}
            onChange={e => setAssessment({ ...assessment, cohort_id: e.target.value })}
            className="w-full p-3 rounded-xl bg-[#12141d] text-white border border-white/10"
          >
            <option value="">Select cohort</option>
            {cohorts.map(c => (
              <option key={c.id} value={c.id}>
                {c.name} · {c.branch}
              </option>
            ))}
          </select>
          <input
            required
            placeholder="Skill (e.g. DSA, Python)"
            value={assessment.skill}
            onChange={e => setAssessment({ ...assessment, skill: e.target.value })}
            className="w-full p-3 rounded-xl bg-white/5 text-white border border-white/10"
          />

          {/* Mode B: Question Bank Fields */}
          <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <p className="text-xs font-semibold text-indigo-300">Option 1: Pull from Question Bank (Mode B)</p>
            <select
              value={assessment.year}
              onChange={e => setAssessment({ ...assessment, year: e.target.value })}
              className="w-full p-2.5 rounded-xl bg-[#12141d] text-white border border-white/10 text-sm"
            >
              <option value="">Select Year (1st/2nd/3rd/4th Year)</option>
              <option value="1st Year">1st Year</option>
              <option value="2nd Year">2nd Year</option>
              <option value="3rd Year">3rd Year</option>
              <option value="4th Year">4th Year</option>
            </select>
            <input
              placeholder="Topic code (e.g. dsa)"
              value={assessment.topic_code}
              onChange={e => setAssessment({ ...assessment, topic_code: e.target.value })}
              className="w-full p-2.5 rounded-xl bg-white/5 text-white border border-white/10 text-sm"
            />
            <input
              type="number"
              min="1"
              max="50"
              placeholder="Question count (e.g. 5)"
              value={assessment.question_count}
              onChange={e => setAssessment({ ...assessment, question_count: e.target.value })}
              className="w-full p-2.5 rounded-xl bg-white/5 text-white border border-white/10 text-sm"
            />
          </div>

          {/* Mode A: Manual Question Fields */}
          <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <p className="text-xs font-semibold text-slate-400">Option 2: Or add manual question (Mode A)</p>
            {(['prompt', 'optionA', 'optionB'] as const).map(key => (
              <input
                key={key}
                required={!isBankMode}
                placeholder={key === 'optionA' ? 'Correct option' : key === 'optionB' ? 'Alternative option' : key}
                value={assessment[key]}
                onChange={e => setAssessment({ ...assessment, [key]: e.target.value })}
                className="w-full p-2.5 rounded-xl bg-white/5 text-white border border-white/10 text-sm"
              />
            ))}
          </div>

          <Button type="submit" variant="glow">
            Publish
          </Button>
        </form>

        {/* Launch Coding Contest Card */}
        <form onSubmit={addContest} className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <div className="flex items-center gap-2">
            <Code2 className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-bold text-white">Schedule Coding Contest</h2>
          </div>
          <p className="text-xs text-slate-400">
            Randomly sample algorithmic questions from the coding question bank and assign to a cohort.
          </p>

          <select
            required
            value={contestForm.cohort_id}
            onChange={e => setContestForm({ ...contestForm, cohort_id: e.target.value })}
            className="w-full p-3 rounded-xl bg-[#12141d] text-white border border-white/10"
          >
            <option value="">Select target cohort</option>
            {cohorts.map(c => (
              <option key={c.id} value={c.id}>
                {c.name} · {c.branch}
              </option>
            ))}
          </select>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Question Count</label>
              <input
                type="number"
                min="1"
                max="5"
                required
                value={contestForm.question_count}
                onChange={e => setContestForm({ ...contestForm, question_count: Number(e.target.value) })}
                className="w-full p-3 rounded-xl bg-white/5 text-white border border-white/10 text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Duration (Minutes)</label>
              <input
                type="number"
                min="5"
                max="360"
                required
                value={contestForm.duration_minutes}
                onChange={e => setContestForm({ ...contestForm, duration_minutes: Number(e.target.value) })}
                className="w-full p-3 rounded-xl bg-white/5 text-white border border-white/10 text-sm"
              />
            </div>
          </div>

          <Button type="submit" variant="glow" leftIcon={<Code2 className="w-4 h-4" />}>
            Launch Live Contest
          </Button>
        </form>
      </div>
    </div>
  );
};
