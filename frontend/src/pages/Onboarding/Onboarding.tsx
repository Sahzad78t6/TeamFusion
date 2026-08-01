import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, ArrowRight, ArrowLeft, Check, Target, Clock, Loader2 } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { useApp } from '../../context/AppContext';

export const Onboarding: React.FC = () => {
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();
  const { submitOnboarding } = useApp();

  // Onboarding Form State
  const [formData, setFormData] = useState({
    dreamCareer: 'AI Startup Founder & Chief Architect',
    currentLevel: 'Senior (6+ Years)',
    skills: ['LangGraph', 'Python', 'System Design', 'React'],
    interests: ['Agentic AI', 'Venture Capital', 'Cognitive Science', 'Open Source'],
    timeCommitment: '2 Hours / Day',
    learningStyle: 'Project-Based & Video Deep Dives',
  });

  const totalSteps = 4;

  const toggleSkill = (skill: string) => {
    setFormData((prev) => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter((s) => s !== skill)
        : [...prev.skills, skill],
    }));
  };

  const toggleInterest = (interest: string) => {
    setFormData((prev) => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter((i) => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const handleNext = async () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      setIsSubmitting(true);
      setErrorMsg('');
      try {
        await submitOnboarding({
          goal: formData.dreamCareer,
          target_role: formData.dreamCareer,
          current_role: formData.currentLevel,
          skills: formData.skills,
          interests: formData.interests,
          experience: formData.currentLevel,
          learning_style: formData.learningStyle,
          available_time: formData.timeCommitment,
          preferred_content: ['Courses', 'Interactive Labs'],
          language: 'English',
        });
        navigate('/dashboard');
      } catch (err: any) {
        console.error('Onboarding submission error:', err);
        setErrorMsg(err.message || 'Failed to calibrate identity twin. Proceeding to dashboard.');
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="min-h-screen w-screen bg-[#090a0f] flex items-center justify-center p-4 selection:bg-purple-500 selection:text-white relative overflow-hidden">
      <div className="absolute -top-40 left-1/3 w-[500px] h-[500px] bg-purple-600/15 rounded-full blur-[140px] pointer-events-none" />

      <div className="w-full max-w-2xl bg-[#12141d]/90 border border-white/10 rounded-3xl p-6 md:p-10 shadow-2xl backdrop-blur-2xl space-y-8 relative">
        {/* Wizard Top Bar */}
        <div className="flex items-center justify-between border-b border-white/10 pb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">GrowthOS Identity Calibration</h2>
              <p className="text-[11px] text-slate-400">Step {step} of {totalSteps}</p>
            </div>
          </div>

          {/* Progress Indicator Bar */}
          <div className="flex items-center gap-1.5">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`h-2 rounded-full transition-all duration-300 ${
                  s === step
                    ? 'w-8 bg-gradient-to-r from-purple-500 to-indigo-500'
                    : s < step
                    ? 'w-3 bg-purple-500/40'
                    : 'w-3 bg-white/10'
                }`}
              />
            ))}
          </div>
        </div>

        {errorMsg && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-300">
            {errorMsg}
          </div>
        )}

        {/* Step Contents */}
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <span className="px-2.5 py-1 text-[10px] font-extrabold bg-purple-500/20 text-purple-300 rounded-full uppercase border border-purple-500/30">
                  Phase 1 — Vision
                </span>
                <h3 className="text-xl font-bold text-white">What is your Dream Role or Career Goal?</h3>
                <p className="text-xs text-slate-400">This forms the target state of your Identity Twin model.</p>
              </div>

              <div className="space-y-3">
                {[
                  'AI Startup Founder & Chief Architect',
                  'Staff Machine Learning Engineer',
                  'VP of Product & AI Strategy',
                  'Autonomous Systems Researcher',
                  'Custom / Other Role',
                ].map((role) => (
                  <button
                    key={role}
                    onClick={() => setFormData({ ...formData, dreamCareer: role })}
                    className={`w-full flex items-center justify-between p-4 rounded-xl text-xs font-semibold text-left transition-all border ${
                      formData.dreamCareer === role
                        ? 'bg-purple-600/20 border-purple-500 text-white shadow-lg shadow-purple-500/10'
                        : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Target className="w-4 h-4 text-purple-400" />
                      <span>{role}</span>
                    </div>
                    {formData.dreamCareer === role && <Check className="w-4 h-4 text-purple-400" />}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <span className="px-2.5 py-1 text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 rounded-full uppercase border border-indigo-500/30">
                  Phase 2 — Skill Baseline
                </span>
                <h3 className="text-xl font-bold text-white">Select Your Core Technical & Business Skills</h3>
                <p className="text-xs text-slate-400">Click to add/remove your existing strengths.</p>
              </div>

              <div className="flex flex-wrap gap-2.5">
                {[
                  'LangGraph',
                  'Python',
                  'System Design',
                  'React & TypeScript',
                  'FastAPI',
                  'Vector DBs',
                  'Pitching & Storytelling',
                  'Venture Capital',
                  'Product Strategy',
                  'Rust',
                  'Deep RL',
                  'PyTorch',
                ].map((skill) => {
                  const isSelected = formData.skills.includes(skill);
                  return (
                    <button
                      key={skill}
                      onClick={() => toggleSkill(skill)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-medium transition-all border ${
                        isSelected
                          ? 'bg-indigo-600 text-white border-indigo-400 shadow-md shadow-indigo-500/30'
                          : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      {skill} {isSelected ? '✓' : '+'}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <span className="px-2.5 py-1 text-[10px] font-extrabold bg-cyan-500/20 text-cyan-300 rounded-full uppercase border border-cyan-500/30">
                  Phase 3 — Interests & Topics
                </span>
                <h3 className="text-xl font-bold text-white">What growth areas excite you most?</h3>
                <p className="text-xs text-slate-400">Used by autonomous agents to fetch relevant papers, courses & opportunities.</p>
              </div>

              <div className="flex flex-wrap gap-2.5">
                {[
                  'Agentic AI',
                  'Venture Capital',
                  'Cognitive Science',
                  'Open Source',
                  'Global Hackathons',
                  'High-Performance Computing',
                  'Public Speaking',
                  'Habit Regularity',
                ].map((topic) => {
                  const isSelected = formData.interests.includes(topic);
                  return (
                    <button
                      key={topic}
                      onClick={() => toggleInterest(topic)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-medium transition-all border ${
                        isSelected
                          ? 'bg-cyan-600 text-white border-cyan-400 shadow-md shadow-cyan-500/30'
                          : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      {topic}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {step === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="space-y-2">
                <span className="px-2.5 py-1 text-[10px] font-extrabold bg-emerald-500/20 text-emerald-300 rounded-full uppercase border border-emerald-500/30">
                  Phase 4 — Daily Cadence
                </span>
                <h3 className="text-xl font-bold text-white">How much daily time can you commit to deep learning?</h3>
                <p className="text-xs text-slate-400">Prevents ML burnout prediction triggers.</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {['30 Mins / Day', '1 Hour / Day', '2 Hours / Day', '3+ Hours / Day'].map((time) => (
                  <button
                    key={time}
                    onClick={() => setFormData({ ...formData, timeCommitment: time })}
                    className={`p-4 rounded-xl text-xs font-semibold text-center border transition-all ${
                      formData.timeCommitment === time
                        ? 'bg-emerald-600/20 border-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                        : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
                    }`}
                  >
                    <Clock className="w-5 h-5 mx-auto mb-2 text-emerald-400" />
                    <span>{time}</span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Wizard Bottom Controls */}
        <div className="flex items-center justify-between border-t border-white/10 pt-6">
          {step > 1 ? (
            <Button
              variant="ghost"
              size="sm"
              disabled={isSubmitting}
              onClick={() => setStep(step - 1)}
              leftIcon={<ArrowLeft className="w-4 h-4" />}
            >
              Back
            </Button>
          ) : <div />}

          <Button
            variant="glow"
            size="md"
            disabled={isSubmitting}
            onClick={handleNext}
            rightIcon={isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
          >
            {isSubmitting
              ? 'Calibrating Twin via Groq...'
              : step === totalSteps
              ? 'Calibrate & Launch Dashboard'
              : 'Continue'}
          </Button>
        </div>
      </div>
    </div>
  );
};
