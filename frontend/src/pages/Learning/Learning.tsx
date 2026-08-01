import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Bookmark, Heart, Star, Search, ExternalLink, Filter, CheckCircle2 } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import { ContentType } from '../../types';

export const Learning: React.FC = () => {
  const { learningResources, toggleBookmarkResource, toggleLikeResource } = useApp();
  const [selectedType, setSelectedType] = useState<string>('all');
  const [search, setSearch] = useState('');

  const types = [
    { label: 'All Media', value: 'all' },
    { label: 'Courses', value: 'course' },
    { label: 'Books', value: 'book' },
    { label: 'Papers', value: 'paper' },
    { label: 'Videos', value: 'video' },
    { label: 'Articles', value: 'article' },
    { label: 'Podcasts', value: 'podcast' },
  ];

  const filtered = learningResources.filter((r) => {
    const matchesType = selectedType === 'all' || r.type === selectedType;
    const matchesSearch =
      r.title.toLowerCase().includes(search.toLowerCase()) ||
      r.author.toLowerCase().includes(search.toLowerCase()) ||
      r.category.toLowerCase().includes(search.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="purple">AI Curator Active</Badge>
            <Badge variant="cyan">{learningResources.length} Curated Resources</Badge>
          </div>
          <h1 className="text-3xl font-extrabold text-white mt-2">Learning Curation</h1>
          <p className="text-xs text-slate-400">High-ROI knowledge tailored to bridge your skill gaps.</p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search resources, topics..."
            className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {types.map((t) => (
          <button
            key={t.value}
            onClick={() => setSelectedType(t.value)}
            className={`px-4 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all border ${
              selectedType === t.value
                ? 'bg-purple-600 text-white border-purple-400 shadow-md shadow-purple-500/20'
                : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Resource Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((res) => (
          <motion.div
            key={res.id}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel rounded-3xl border border-white/10 overflow-hidden flex flex-col justify-between hover:border-purple-500/40 transition-all duration-300 group"
          >
            {/* Image Banner */}
            <div className="relative h-44 w-full overflow-hidden">
              <img
                src={res.imageUrl}
                alt={res.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#12141d] via-transparent to-black/30" />

              <span className="absolute top-3 left-3 px-2.5 py-1 text-[10px] font-bold rounded-lg bg-black/70 text-white backdrop-blur-md uppercase tracking-wider border border-white/10">
                {res.type}
              </span>

              {/* Bookmark & Heart Buttons */}
              <div className="absolute top-3 right-3 flex items-center gap-1.5">
                <button
                  onClick={() => toggleLikeResource(res.id)}
                  className={`p-2 rounded-xl backdrop-blur-md border transition-colors ${
                    res.isLiked ? 'bg-rose-500/20 border-rose-500/40 text-rose-400' : 'bg-black/40 border-white/10 text-slate-400 hover:text-white'
                  }`}
                >
                  <Heart className={`w-3.5 h-3.5 ${res.isLiked ? 'fill-rose-400' : ''}`} />
                </button>
                <button
                  onClick={() => toggleBookmarkResource(res.id)}
                  className={`p-2 rounded-xl backdrop-blur-md border transition-colors ${
                    res.isBookmarked ? 'bg-purple-500/20 border-purple-500/40 text-purple-300' : 'bg-black/40 border-white/10 text-slate-400 hover:text-white'
                  }`}
                >
                  <Bookmark className={`w-3.5 h-3.5 ${res.isBookmarked ? 'fill-purple-300' : ''}`} />
                </button>
              </div>
            </div>

            {/* Card Body */}
            <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <span>{res.platform}</span>
                  <span className="flex items-center gap-1 text-amber-400 font-bold">
                    <Star className="w-3 h-3 fill-amber-400" /> {res.rating}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-purple-300 transition-colors line-clamp-2">
                  {res.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1">{res.author} • {res.duration}</p>
              </div>

              <div className="space-y-3 pt-2 border-t border-white/10">
                {/* Progress bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] font-semibold text-slate-400">
                    <span>Completion</span>
                    <span className="text-purple-400">{res.progressPercentage}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full" style={{ width: `${res.progressPercentage}%` }} />
                  </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1.5">
                  {res.tags.map((t, i) => (
                    <span key={i} className="px-2 py-0.5 text-[9px] font-mono rounded-md bg-white/5 text-slate-400 border border-white/5">
                      #{t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
