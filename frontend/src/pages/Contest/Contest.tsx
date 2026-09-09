import React, { useState, useEffect, useRef } from 'react';
import {
  Code2,
  Maximize2,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Terminal,
  FileCode,
  ShieldAlert,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import {
  getActiveContestApi,
  submitContestCodeApi,
  ActiveContestResponse,
  ContestSubmitResponse,
} from '../../services/api';

export const Contest: React.FC = () => {
  const { authToken } = useApp();
  const containerRef = useRef<HTMLDivElement>(null);

  const [contest, setContest] = useState<ActiveContestResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [hasEnteredFullscreen, setHasEnteredFullscreen] = useState<boolean>(false);
  const [testEnded, setTestEnded] = useState<boolean>(false);
  const [testEndedReason, setTestEndedReason] = useState<string>('');

  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number>(0);
  const [codeMap, setCodeMap] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [resultsMap, setResultsMap] = useState<Record<string, ContestSubmitResponse>>({});
  const [lastAutoSubmitted, setLastAutoSubmitted] = useState<boolean>(false);

  // Keep latest state in refs for event listener access without closure staleness
  const contestRef = useRef<ActiveContestResponse | null>(null);
  contestRef.current = contest;
  const activeQuestionIndexRef = useRef<number>(0);
  activeQuestionIndexRef.current = activeQuestionIndex;
  const codeMapRef = useRef<Record<string, string>>({});
  codeMapRef.current = codeMap;
  const hasEnteredFullscreenRef = useRef<boolean>(false);
  hasEnteredFullscreenRef.current = hasEnteredFullscreen;
  const testEndedRef = useRef<boolean>(false);
  testEndedRef.current = testEnded;

  // 1. Poll GET /contests/active every 5 seconds
  useEffect(() => {
    let isMounted = true;

    const fetchActiveContest = async () => {
      if (!authToken) return;
      try {
        const active = await getActiveContestApi(authToken);
        if (!isMounted) return;

        setContest(active);
        // Initialize starter code if not already set
        if (active && active.questions && active.questions.length > 0) {
          setCodeMap((prev) => {
            const next = { ...prev };
            active.questions.forEach((q) => {
              if (next[q.id] === undefined) {
                next[q.id] = q.starter_code || '# Write your solution here\n';
              }
            });
            return next;
          });
        }
      } catch (err) {
        console.error('Failed to poll active contest:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchActiveContest();
    const interval = setInterval(fetchActiveContest, 5000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [authToken]);

  // Helper to immediately auto-submit active question and lock contest
  const terminateAndAutoSubmit = async (reason = 'Test ended — you exited fullscreen') => {
    if (testEndedRef.current) return;
    setTestEnded(true);
    setTestEndedReason(reason);

    const currentContest = contestRef.current;
    if (currentContest && currentContest.questions && currentContest.questions.length > 0) {
      const currentQIndex = activeQuestionIndexRef.current;
      const activeQ = currentContest.questions[currentQIndex];
      if (activeQ && authToken) {
        const currentCode = codeMapRef.current[activeQ.id] || activeQ.starter_code || '';
        try {
          setLastAutoSubmitted(true);
          const res = await submitContestCodeApi(authToken, currentContest.id, {
            question_id: activeQ.id,
            code: currentCode,
          });
          setResultsMap((prev) => ({ ...prev, [activeQ.id]: res }));
        } catch (err) {
          console.error('Error auto-submitting on exit:', err);
        }
      }
    }
  };

  // 5. Add document 'fullscreenchange' listener & Escape key detector:
  // if document.fullscreenElement becomes null or user presses Escape while contest is active and unsubmitted,
  // immediately POST /contests/{id}/submit with the current textarea contents for the active question,
  // then show "Test ended — you exited fullscreen" and lock further input
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isFullscreenNow = !!document.fullscreenElement;
      if (!isFullscreenNow && hasEnteredFullscreenRef.current && !testEndedRef.current) {
        terminateAndAutoSubmit('Test ended — you exited fullscreen');
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && hasEnteredFullscreenRef.current && !testEndedRef.current) {
        terminateAndAutoSubmit('Test ended — you exited fullscreen');
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [authToken]);


  // 4. On click: call container element's requestFullscreen(), then reveal questions
  const handleEnterFullscreen = async () => {
    try {
      if (containerRef.current && containerRef.current.requestFullscreen) {
        await containerRef.current.requestFullscreen();
      } else if (document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
      }
      setHasEnteredFullscreen(true);
    } catch (err) {
      console.warn('Fullscreen request failed or was rejected:', err);
      // Fallback for browsers that block programmatic fullscreen without explicit direct gesture
      setHasEnteredFullscreen(true);
    }
  };

  const handleManualSubmit = async () => {
    if (!contest || testEnded || submitting || !authToken) return;
    const activeQ = contest.questions[activeQuestionIndex];
    if (!activeQ) return;

    setSubmitting(true);
    try {
      const currentCode = codeMap[activeQ.id] || activeQ.starter_code || '';
      const res = await submitContestCodeApi(authToken, contest.id, {
        question_id: activeQ.id,
        code: currentCode,
      });
      setResultsMap((prev) => ({ ...prev, [activeQ.id]: res }));
    } catch (err: any) {
      alert(`Submission error: ${err.message || 'Server error'}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-slate-400 text-sm">Checking for active coding contests...</p>
      </div>
    );
  }

  // 2. If null: show "No active contest right now"
  if (!contest) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-white/10 flex items-center justify-center mx-auto mb-6 text-slate-400">
          <Terminal className="w-8 h-8 text-indigo-400" />
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">No active contest right now</h1>
        <p className="text-slate-400 text-sm max-w-md mx-auto mb-6">
          There are no scheduled coding contests currently open for your cohort. Check back later or notify your institution administrator.
        </p>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-white/5 text-xs text-slate-500">
          <Clock className="w-3.5 h-3.5 animate-pulse text-indigo-400" />
          <span>Auto-polling every 5s</span>
        </div>
      </div>
    );
  }

  // 3. If active and not yet entered: show an "Enter Fullscreen to Begin" button
  if (!hasEnteredFullscreen && !testEnded) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-b from-[#161a29] to-[#0d101d] border border-indigo-500/20 rounded-2xl p-8 shadow-2xl text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto mb-5 text-indigo-400 shadow-lg shadow-indigo-500/10">
            <Code2 className="w-8 h-8" />
          </div>

          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-4">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            CONTEST LIVE NOW
          </div>

          <h1 className="text-2xl font-extrabold text-white mb-3">Live Coding Assessment</h1>
          <p className="text-slate-300 text-sm max-w-md mx-auto mb-6 leading-relaxed">
            You have {contest.questions.length} algorithmic challenge{contest.questions.length > 1 ? 's' : ''} to solve.
            Proctoring requires entering fullscreen mode.
          </p>

          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 mb-8 text-left flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-200/90 leading-relaxed">
              <strong className="font-semibold text-amber-300">Fullscreen Anti-Cheat Rule:</strong> Exiting fullscreen (pressing Esc, switching tabs, or un-maximizing) will immediately trigger auto-submission of your current code and end the test.
            </div>
          </div>

          <button
            id="enter-fullscreen-btn"
            onClick={handleEnterFullscreen}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/25 transition-all transform active:scale-95"
          >
            <Maximize2 className="w-4 h-4" />
            <span>Enter Fullscreen to Begin</span>
          </button>
        </div>
      </div>
    );
  }

  const activeQuestion = contest.questions[activeQuestionIndex];
  const activeCode = codeMap[activeQuestion?.id] || activeQuestion?.starter_code || '';
  const currentResult = resultsMap[activeQuestion?.id];

  return (
    <div
      ref={containerRef}
      id="contest-fullscreen-container"
      className="flex flex-col h-full min-h-screen bg-[#090b11] text-white p-4 lg:p-6 select-none overflow-auto"
    >
      {/* Test Ended Banner if exited fullscreen */}
      {testEnded && (
        <div id="test-ended-banner" className="mb-6 p-4 rounded-xl bg-red-500/15 border border-red-500/40 text-red-200 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-red-400 shrink-0" />
            <div>
              <h2 className="font-bold text-red-300 text-base">{testEndedReason || 'Test ended — you exited fullscreen'}</h2>
              <p className="text-xs text-red-200/80">
                {lastAutoSubmitted
                  ? 'Your active code was automatically submitted to the judge before the session locked.'
                  : 'Your contest session is locked.'}
              </p>
            </div>
          </div>
          <span className="text-xs px-3 py-1 rounded bg-red-950/60 border border-red-800 text-red-300 font-mono">
            SESSION LOCKED
          </span>
        </div>
      )}

      {/* Header bar */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Code2 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Coding Assessment</h1>
            <p className="text-xs text-slate-400">
              Question {activeQuestionIndex + 1} of {contest.questions.length}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Question Selector Tabs */}
          <div className="flex items-center gap-2">
            {contest.questions.map((q, idx) => {
              const hasResult = resultsMap[q.id];
              const isPassed = hasResult?.passed === true;
              return (
                <button
                  key={q.id}
                  id={`question-tab-${idx}`}
                  onClick={() => setActiveQuestionIndex(idx)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                    activeQuestionIndex === idx
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'bg-white/5 hover:bg-white/10 text-slate-300'
                  }`}
                >
                  <span>Q{idx + 1}</span>
                  {hasResult && (
                    isPassed ? (
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    ) : (
                      <XCircle className="w-3 h-3 text-red-400" />
                    )
                  )}
                </button>
              );
            })}
          </div>

          {/* Exit Fullscreen button */}
          {!testEnded && (
            <button
              id="exit-fullscreen-btn"
              onClick={async () => {
                if (document.fullscreenElement) {
                  try {
                    await document.exitFullscreen();
                  } catch (e) {
                    console.warn(e);
                  }
                }
                terminateAndAutoSubmit('Test ended — you exited fullscreen');
              }}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 flex items-center gap-1.5 transition-colors"
              title="Exit Fullscreen & End Test"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Exit Fullscreen</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content Layout: Question Description on Left / Editor on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        {/* Left Column: Question Details */}
        <div className="lg:col-span-5 flex flex-col gap-4 bg-[#0e111a] border border-white/10 rounded-xl p-5 overflow-y-auto max-h-[75vh]">
          {activeQuestion ? (
            <>
              <div className="flex items-center justify-between">
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-medium">
                  {activeQuestion.difficulty || 'Medium'}
                </span>
                <span className="text-xs text-slate-400">Python 3</span>
              </div>

              <h2 className="text-lg font-semibold text-white">{activeQuestion.title}</h2>
              <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                {activeQuestion.description}
              </div>

              {/* Sample Test Cases (Input only - expected_output is NEVER exposed) */}
              {activeQuestion.test_cases && activeQuestion.test_cases.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Sample Test Inputs
                  </h3>
                  <div className="space-y-2">
                    {activeQuestion.test_cases.map((tc, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-black/40 border border-white/5 font-mono text-xs text-slate-300">
                        <span className="text-slate-500">Input: </span>
                        {tc.input.trim()}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Execution Feedback Display */}
              {currentResult && (
                <div id="test-result-box" className="mt-4 pt-4 border-t border-white/10">
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Judge Verdict
                  </h3>
                  <div
                    className={`p-3.5 rounded-xl border flex items-center justify-between mb-3 ${
                      currentResult.passed === true
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                        : currentResult.passed === false
                        ? 'bg-red-500/10 border-red-500/30 text-red-300'
                        : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      {currentResult.passed === true ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      ) : currentResult.passed === false ? (
                        <XCircle className="w-5 h-5 text-red-400" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-amber-400" />
                      )}
                      <div>
                        <div className="text-sm font-bold">
                          {currentResult.passed === true
                            ? 'All Test Cases Passed!'
                            : currentResult.passed === false
                            ? 'Wrong Answer / Timeout'
                            : 'Deferred / Manual Grading'}
                        </div>
                        <div className="text-xs opacity-80">
                          {currentResult.passed === true
                            ? 'Your solution produced the expected standard output.'
                            : currentResult.passed === false
                            ? 'One or more test cases did not match or timed out (>2s).'
                            : 'Submission stored successfully.'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Individual Test Cases breakdown */}
                  {currentResult.results && currentResult.results.length > 0 && (
                    <div className="grid grid-cols-3 gap-2">
                      {currentResult.results.map((r, idx) => (
                        <div
                          key={idx}
                          className={`p-2 rounded-lg text-center font-mono text-xs border ${
                            r.passed
                              ? 'bg-emerald-950/40 border-emerald-800/40 text-emerald-300'
                              : 'bg-red-950/40 border-red-800/40 text-red-300'
                          }`}
                        >
                          Case #{r.test_case_index + 1}: {r.passed ? 'PASS' : 'FAIL'}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <p className="text-slate-400 text-sm">No question selected.</p>
          )}
        </div>

        {/* Right Column: Plain <textarea> Code Editor */}
        <div className="lg:col-span-7 flex flex-col bg-[#0e111a] border border-white/10 rounded-xl overflow-hidden shadow-xl">
          <div className="flex items-center justify-between px-4 py-3 bg-[#0a0d14] border-b border-white/10">
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <FileCode className="w-4 h-4 text-indigo-400" />
              <span>solution.py</span>
            </div>
            {testEnded && (
              <span className="text-[11px] font-semibold text-red-400 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Input Locked
              </span>
            )}
          </div>

          <div className="flex-1 p-3 bg-[#07090e]">
            <textarea
              id="contest-code-editor"
              value={activeCode}
              disabled={testEnded}
              onChange={(e) => {
                const val = e.target.value;
                if (activeQuestion) {
                  setCodeMap((prev) => ({ ...prev, [activeQuestion.id]: val }));
                }
              }}
              onKeyDown={(e) => {
                // Support Tab key indentation
                if (e.key === 'Tab') {
                  e.preventDefault();
                  const target = e.target as HTMLTextAreaElement;
                  const start = target.selectionStart;
                  const end = target.selectionEnd;
                  const newValue = activeCode.substring(0, start) + '    ' + activeCode.substring(end);
                  if (activeQuestion) {
                    setCodeMap((prev) => ({ ...prev, [activeQuestion.id]: newValue }));
                  }
                  setTimeout(() => {
                    target.selectionStart = target.selectionEnd = start + 4;
                  }, 0);
                }
              }}
              placeholder="# Type your Python solution here... Read from sys.stdin or input() and print to stdout."
              rows={18}
              className={`w-full h-full min-h-[380px] p-4 font-mono text-sm leading-relaxed bg-[#0a0d16] text-slate-100 border border-white/5 rounded-lg outline-none focus:border-indigo-500/50 resize-y transition-colors ${
                testEnded ? 'opacity-50 cursor-not-allowed bg-slate-900/50' : ''
              }`}
            />
          </div>

          {/* Editor Footer Action Bar */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#0a0d14] border-t border-white/10">
            <div className="text-xs text-slate-400">
              Standard Python 3 execution • Isolated sandbox • 2s hard timeout
            </div>
            <button
              id="contest-submit-btn"
              onClick={handleManualSubmit}
              disabled={testEnded || submitting}
              className={`inline-flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-xs text-white transition-all shadow-md ${
                testEnded
                  ? 'bg-slate-700/50 cursor-not-allowed text-slate-400'
                  : submitting
                  ? 'bg-indigo-700 cursor-wait'
                  : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/30'
              }`}
            >
              {submitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Executing Solution...</span>
                </>
              ) : (
                <>
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Run & Submit Code</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Contest;
