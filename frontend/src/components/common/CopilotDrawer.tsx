import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { chatWithCopilotApi } from '../../services/api';

interface Message { id: string; sender: 'ai' | 'user'; text: string; timestamp: string; }

export const CopilotDrawer: React.FC = () => {
  const { isCopilotOpen, setIsCopilotOpen, identityTwin, user, authToken, refreshDashboard } = useApp();
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    setMessages([{ id: 'welcome', sender: 'ai', timestamp: 'Just now', text: `Hi ${user.name}! I can create a plan, curate learning resources, find opportunities, or process a reflection. Your alignment is ${identityTwin.alignmentPercentage}%.` }]);
  }, [user.name, identityTwin.alignmentPercentage]);

  const handleSend = async (suggestion?: string) => {
    const text = (suggestion || input).trim();
    if (!text || isSending) return;
    setMessages((current) => [...current, { id: `user-${Date.now()}`, sender: 'user', text, timestamp: 'Just now' }]);
    setInput('');
    if (!authToken) {
      setMessages((current) => [...current, { id: `error-${Date.now()}`, sender: 'ai', text: 'Please sign in first so I can use your saved profile and run the right agent.', timestamp: 'Just now' }]);
      return;
    }
    setIsSending(true);
    try {
      const response = await chatWithCopilotApi(authToken, text);
      setMessages((current) => [...current, { id: `ai-${Date.now()}`, sender: 'ai', text: response.message, timestamp: `Handled by ${response.agent.replace('_', ' ')}` }]);
      await refreshDashboard();
    } catch (error) {
      const text = error instanceof Error ? error.message : 'Something went wrong while contacting the Copilot.';
      setMessages((current) => [...current, { id: `error-${Date.now()}`, sender: 'ai', text, timestamp: 'Just now' }]);
    } finally { setIsSending(false); }
  };

  if (!isCopilotOpen) return null;
  return <AnimatePresence><div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
    <motion.div initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'spring', damping: 25 }} className="flex h-full w-full max-w-md flex-col border-l border-white/10 bg-[#12141d] shadow-2xl">
      <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-5 py-4"><div className="flex items-center gap-3"><Sparkles className="h-5 w-5 text-amber-300" /><div><h3 className="text-sm font-bold text-white">GrowthOS Copilot</h3><p className="text-[10px] text-slate-400">Live multi-agent growth assistant</p></div></div><button onClick={() => setIsCopilotOpen(false)} className="rounded-lg p-2 text-slate-400 hover:bg-white/10 hover:text-white"><X className="h-5 w-5" /></button></div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">{messages.map((message) => <div key={message.id} className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : ''}`}>{message.sender === 'ai' && <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-600/30"><Bot className="h-4 w-4 text-indigo-300" /></div>}<div className={`max-w-[82%] rounded-2xl p-3 text-xs leading-relaxed ${message.sender === 'user' ? 'bg-indigo-600 text-white' : 'border border-white/10 bg-white/5 text-slate-200'}`}><p>{message.text}</p><span className="mt-2 block text-[9px] opacity-60">{message.timestamp}</span></div>{message.sender === 'user' && <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-purple-600"><User className="h-4 w-4 text-white" /></div>}</div>)}{isSending && <div className="flex items-center gap-2 text-xs text-indigo-300"><Loader2 className="h-4 w-4 animate-spin" /> Running your agent…</div>}</div>
      <div className="border-t border-white/10 bg-white/5 p-4"><div className="mb-3 flex flex-wrap gap-2">{['Make a plan for today', 'Recommend courses for me', 'Find career opportunities', 'I need a reflection check-in'].map((item) => <button key={item} onClick={() => handleSend(item)} disabled={isSending} className="rounded-full border border-purple-500/30 bg-purple-500/10 px-2 py-1 text-[10px] text-purple-200 disabled:opacity-50">{item}</button>)}</div><form onSubmit={(event) => { event.preventDefault(); handleSend(); }} className="flex gap-2"><input value={input} onChange={(event) => setInput(event.target.value)} disabled={isSending} placeholder="Ask about plans, learning, opportunities..." className="flex-1 rounded-xl border border-white/10 bg-black/40 px-3 py-2.5 text-xs text-white placeholder:text-slate-500" /><button disabled={isSending} type="submit" className="rounded-xl bg-indigo-600 p-2.5 text-white disabled:opacity-50"><Send className="h-4 w-4" /></button></form></div>
    </motion.div></div></AnimatePresence>;
};