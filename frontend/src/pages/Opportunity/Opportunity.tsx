import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Compass, Star, MapPin, Calendar, Award, ArrowUpRight, Heart, Filter, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export const Opportunity: React.FC = () => {
  const { opportunities, toggleFavoriteOpportunity } = useApp();
  const [selectedType, setSelectedType] = useState('all');

  const types = [
    { label: 'All Opportunities', value: 'all' },
    { label: 'Hackathons', value: 'hackathon' },
    { label: 'Internships / Roles', value: 'internship' },
    { label: 'Communities', value: 'community' },
    { label: 'Mentorship', value: 'mentor' },
    { label: 'Conferences', value: 'conference' },
  ];

  const filtered = opportunities.filter((o) => selectedType === 'all' || o.type === selectedType);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="cyan" icon={<Sparkles className="w-3.5 h-3.5" />}>
              Opportunity Radar Active
            </Badge>
            <Badge variant="purple">98% Highest Match</Badge>
          </div>
          <h1 className="text-3xl font-extrabold text-white mt-2">Growth Opportunities</h1>
          <p className="text-xs text-slate-400">Scanned globally to match your Identity Twin skill gaps.</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {types.map((t) => (
          <button
            key={t.value}
            onClick={() => setSelectedType(t.value)}
            className={`px-4 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all border ${
              selectedType === t.value
                ? 'bg-cyan-600 text-white border-cyan-400 shadow-md shadow-cyan-500/20'
                : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Opportunities List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filtered.map((opp) => (
          <motion.div
            key={opp.id}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4 hover:border-cyan-500/40 transition-all flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between">
                <Badge variant="cyan" icon={<Sparkles className="w-3 h-3" />}>
                  {opp.matchScore}% Match Score
                </Badge>

                <button
                  onClick={() => toggleFavoriteOpportunity(opp.id)}
                  className={`p-2 rounded-xl border backdrop-blur-md transition-colors ${
                    opp.isFavorite ? 'bg-rose-500/20 border-rose-500/40 text-rose-400' : 'bg-white/5 border-white/10 text-slate-400 hover:text-white'
                  }`}
                >
                  <Heart className={`w-4 h-4 ${opp.isFavorite ? 'fill-rose-400' : ''}`} />
                </button>
              </div>

              <h3 className="text-lg font-bold text-white mt-3 group-hover:text-cyan-300 transition-colors">
                {opp.title}
              </h3>
              <p className="text-xs text-slate-400 font-semibold">{opp.organization}</p>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">{opp.description}</p>
            </div>

            <div className="space-y-4 pt-3 border-t border-white/10">
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" />
                  <span>Deadline: <strong className="text-slate-200">{opp.deadline}</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-500" />
                  <span className="truncate">{opp.location}</span>
                </div>
              </div>

              {/* Reward & Skills Required */}
              <div className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                  <Award className="w-4 h-4" />
                  <span>{opp.reward}</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {opp.skillsRequired.map((skill, i) => (
                    <span key={i} className="px-2 py-0.5 text-[10px] font-mono rounded bg-white/5 text-slate-300 border border-white/10">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <Button
                variant="glow"
                size="sm"
                className="w-full"
                rightIcon={<ArrowUpRight className="w-4 h-4" />}
                onClick={() => window.open(opp.applyUrl, '_blank')}
              >
                Apply / Register Now
              </Button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
