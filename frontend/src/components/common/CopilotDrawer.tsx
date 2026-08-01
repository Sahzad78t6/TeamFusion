import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Send, Bot, User, Flame, ArrowUpRight, RefreshCw } from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  timestamp: string;
  actions?: { label: string; action: string }[];
}

export const CopilotDrawer: React.FC = () => {
  const { isCopilotOpen, setIsCopilotOpen, identityTwin, user } = useApp();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'm-1',
      sender: 'ai',
      text: `Hello ${user.name}! I am your GrowthOS Copilot. Your Identity Alignment with Founder Archetype is currently at ${identityTwin.alignmentPercentage}%. How can I accelerate your learning or gap resolution today?`,
      timestamp: 'Just now',
      actions: [
        { label: 'Analyze VC Knowledge Gap', action: 'vc_gap' },
        { label: 'Suggest Today\'s Deep Work Plan', action: 'plan' },
        { label: 'Check Burnout Risk Factor', action: 'burnout' },
      ],
    },
  ]);

  if (!isCopilotOpen) return null;

  const handleSend = (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim()) return;

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: 'Just now',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');

    // Simulate AI Copilot Response
    setTimeout(() => {
      let aiText = `I have analyzed your Identity Twin and daily reflections. Here is my strategic recommendation for "${text}": Focus on 45 minutes of agentic routing edge design today, followed by reviewing pitch deck narratives.`;
      if (text.toLowerCase().includes('burnout')) {
        aiText = `Your current Burnout Risk Score is at 14% (Low). However, your sleep window drifted by 45 minutes last night. Recommend taking a 20-minute phone-free walk before your 4 PM deep work block.`;
      } else if (text.toLowerCase().includes('vc') || text.toLowerCase().includes('venture')) {
        aiText = `To bridge your VC & Business knowledge gap (currently 50/100), I've added 'The Founder Playbook: Chapter 4 on SaaS Unit Economics' to your top priority learning queue.`;
      }

      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: aiText,
        timestamp: 'Just now',
      };
      setMessages((prev) => [...prev, aiMsg]);
    }, 800);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="w-full max-w-md h-full bg-[#12141d] border-l border-white/10 flex flex-col shadow-2xl shadow-purple-950/50"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/10 bg-white/5">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center shadow-md shadow-purple-500/30">
                <Sparkles className="w-5 h-5 text-amber-300 fill-amber-300" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                  GrowthOS Copilot <span className="px-1.5 py-0.5 text-[9px] font-extrabold bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">PRO</span>
                </h3>
                <p className="text-[10px] text-slate-400">Autonomous Growth & Identity AI</p>
              </div>
            </div>
            <button
              onClick={() => setIsCopilotOpen(false)}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'ai' && (
                  <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-indigo-400" />
                  </div>
                )}

                <div className={`max-w-[82%] space-y-2`}>
                  <div
                    className={`p-3.5 rounded-2xl text-xs leading-relaxed ${
                      m.sender === 'user'
                        ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-none shadow-md shadow-indigo-500/20'
                        : 'bg-white/5 border border-white/10 text-slate-200 rounded-bl-none backdrop-blur-md'
                    }`}
                  >
                    {m.text}
                  </div>

                  {m.actions && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {m.actions.map((act) => (
                        <button
                          key={act.action}
                          onClick={() => handleSend(act.label)}
                          className="px-2.5 py-1 text-[10px] font-semibold text-purple-300 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 rounded-full transition-colors flex items-center gap-1"
                        >
                          <span>{act.label}</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </button>
                      ))}
                    </div>
                  )}

                  <span className="text-[9px] text-slate-500 block px-1">{m.timestamp}</span>
                </div>

                {m.sender === 'user' && (
                  <img
                    src={user.avatar}
                    alt="User"
                    className="w-7 h-7 rounded-lg object-cover border border-purple-500/30 shrink-0"
                  />
                )}
              </div>
            ))}
          </div>

          {/* Input Footer */}
          <div className="p-4 border-t border-white/10 bg-white/5">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask Copilot about identity, tasks, or courses..."
                className="flex-1 px-3.5 py-2.5 text-xs text-white bg-black/40 border border-white/10 rounded-xl placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
              />
              <button
                type="submit"
                className="p-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl shadow-lg shadow-purple-500/25 transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
