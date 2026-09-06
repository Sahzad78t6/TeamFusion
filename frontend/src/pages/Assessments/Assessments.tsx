import React, { useEffect, useState } from 'react';
import { CheckCircle2, ClipboardList, Loader2 } from 'lucide-react';
import { getAssessmentsApi, submitAssessmentApi } from '../../services/api';
import { useApp } from '../../context/AppContext';
import { Button } from '../../components/common/Button';

export const Assessments: React.FC = () => {
  const { authToken } = useApp();
  const [assessments, setAssessments] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>();
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => { if (authToken) getAssessmentsApi(authToken).then(setAssessments).catch(e => setMessage(e.message)).finally(() => setLoading(false)); }, [authToken]);
  const submit = async () => {
    if (!authToken || !selected) return;
    if (Object.keys(answers).length !== selected.questions.length) return setMessage('Answer every question before submitting.');
    try { const result = await submitAssessmentApi(authToken, selected.id, answers); setMessage(`Submitted. Score: ${result.score}%`); setAssessments(items => items.filter(item => item.id !== selected.id)); setSelected(undefined); setAnswers({}); }
    catch (e: any) { setMessage(e.message); }
  };
  if (loading) return <div className="p-8 text-slate-300"><Loader2 className="inline w-4 h-4 animate-spin mr-2" />Loading assessments…</div>;
  return <div className="space-y-6 pb-12"><div><h1 className="text-3xl font-extrabold text-white">Assessments</h1><p className="text-xs text-slate-400 mt-1">Only assessments assigned to your cohort are shown.</p></div>{message && <p className="p-3 rounded-xl bg-indigo-500/10 text-indigo-200 text-sm">{message}</p>}{!selected ? <div className="grid gap-4">{assessments.length ? assessments.map(a => <button key={a.id} onClick={() => setSelected(a)} className="text-left glass-panel p-5 rounded-2xl border border-white/10 hover:border-indigo-400"><ClipboardList className="w-5 h-5 text-indigo-400 mb-2" /><h2 className="font-bold text-white">{a.title}</h2><p className="text-sm text-slate-400">{a.skill} · {a.questions.length} questions</p></button>) : <p className="text-slate-400">No assessments are currently assigned to your cohort.</p>}</div> : <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6"><div><h2 className="text-xl font-bold text-white">{selected.title}</h2><p className="text-sm text-slate-400">{selected.description}</p></div>{selected.questions.map((q: any, index: number) => <fieldset key={q.id} className="space-y-2"><legend className="text-white font-medium">{index + 1}. {q.prompt}</legend>{q.options.map((option: string, optionIndex: number) => <label key={option} className="block p-3 rounded-xl bg-white/5 text-slate-300 cursor-pointer"><input className="mr-2" type="radio" name={q.id} checked={answers[q.id] === optionIndex} onChange={() => setAnswers({ ...answers, [q.id]: optionIndex })} />{option}</label>)}</fieldset>)}<div className="flex gap-3"><Button variant="outline" onClick={() => setSelected(undefined)}>Back</Button><Button variant="glow" onClick={submit} leftIcon={<CheckCircle2 className="w-4 h-4" />}>Submit assessment</Button></div></div>}</div>;
};
