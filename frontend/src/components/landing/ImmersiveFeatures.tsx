import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence, useScroll, useSpring, useMotionValueEvent } from 'framer-motion';
import { Immersive3DCanvas } from './Immersive3DCanvas';

interface FeatureItem {
  num: string;
  title: string;
  desc: string;
}

const features: FeatureItem[] = [
  {
    num: "01",
    title: "AI Identity Profiling",
    desc: "Builds a dynamic identity from aspirations, habits, interests and goals.",
  },
  {
    num: "02",
    title: "Personalized Growth Plan",
    desc: "Creates adaptive daily and weekly growth journeys.",
  },
  {
    num: "03",
    title: "Smart Resource Curation",
    desc: "Curates the right knowledge at the right moment.",
  },
  {
    num: "04",
    title: "Opportunity Discovery",
    desc: "Finds hackathons, competitions and internships.",
  },
  {
    num: "05",
    title: "Identity Graph",
    desc: "Visualizes the evolution of your identity.",
  },
  {
    num: "06",
    title: "Explainable AI Recommendations",
    desc: "Every recommendation includes transparent reasoning.",
  },
  {
    num: "07",
    title: "Growth Analytics Dashboard",
    desc: "Measure progress through meaningful growth metrics.",
  },
  {
    num: "08",
    title: "Reflection & Feedback Loop",
    desc: "Continuously learns from your reflections.",
  },
  {
    num: "09",
    title: "AI Mentor Companion",
    desc: "A conversational mentor guiding your journey.",
  },
  {
    num: "10",
    title: "Adaptive Learning Journey",
    desc: "Continuously evolves as you evolve.",
  },
];

export const ImmersiveFeatures: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Custom scroll listener
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  // Create smooth momentum scrolling using useSpring
  const smoothScrollYProgress = useSpring(scrollYProgress, {
    damping: 35,
    stiffness: 70,
    mass: 1.2,
    restDelta: 0.0001
  });

  const [activeIndex, setActiveIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isLight, setIsLight] = useState(false);

  // Detect theme (light class on documentElement or body) using MutationObserver
  useEffect(() => {
    const checkTheme = () => {
      const isLightMode =
        document.documentElement.classList.contains('light') ||
        document.body.classList.contains('light') ||
        document.documentElement.getAttribute('data-theme') === 'light';
      setIsLight(isLightMode);
    };

    checkTheme();

    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    return () => observer.disconnect();
  }, []);

  // Handle smoothed scroll progress change
  useMotionValueEvent(smoothScrollYProgress, "change", (latest) => {
    const val = latest * 9.99;
    const index = Math.min(Math.floor(val), 9);
    const stepProgress = val - index;

    setActiveIndex(index);
    setProgress(stepProgress);
  });

  // Track mouse coordinates for interactive parallax
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) - 0.5;
      const y = (e.clientY / window.innerHeight) - 0.5;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div ref={containerRef} className="relative h-[800vh] w-full bg-white dark:bg-slate-950 transition-colors duration-300 z-20">
      {/* Sticky container pins the viewport during scrolling */}
      <div className="sticky top-0 h-screen w-full flex flex-col justify-between items-center overflow-hidden bg-white dark:bg-slate-950 transition-colors duration-300">

        {/* Soft, premium, ambient background lighting blobs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[70vw] h-[60vh] bg-indigo-500/5 dark:bg-purple-500/5 rounded-full blur-[180px] pointer-events-none" />
        <div className="absolute top-1/3 left-1/4 w-[350px] h-[350px] bg-purple-500/5 dark:bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none" />

        {/* Subtle dot pattern matching theme */}
        <div
          className="absolute inset-0 opacity-[0.035] dark:opacity-[0.05] pointer-events-none transition-opacity duration-300"
          style={{
            backgroundImage: isLight
              ? `radial-gradient(rgba(0,0,0,0.15) 1px, transparent 1px)`
              : `radial-gradient(rgba(255,255,255,0.15) 1px, transparent 1px)`,
            backgroundSize: '32px 32px'
          }}
        />

        {/* Elegant divider borders */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-white/[0.08] to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-white/[0.08] to-transparent" />

        {/* TOP/CENTER: Large floating 3D object */}
        <div className="flex-1 w-full flex items-center justify-center relative z-10 mt-6 select-none pointer-events-none">
          <div className="w-[85vw] h-[52vh] md:w-[65vw] md:h-[58vh] max-w-4xl relative">
            <Immersive3DCanvas
              activeIndex={activeIndex}
              progress={progress}
              mouseX={mousePos.x}
              mouseY={mousePos.y}
              isLight={isLight}
            />
          </div>
        </div>

        {/* BOTTOM: Feature details and Progress indicators */}
        <div className="w-full pb-14 md:pb-16 px-6 relative z-20 flex flex-col items-center select-none">

          {/* Synchronized text details using AnimatePresence */}
          <div className="h-44 md:h-36 flex items-center justify-center text-center">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
                transition={{ duration: 0.5, ease: [0.215, 0.61, 0.355, 1] }}
                className="flex flex-col items-center justify-center text-center max-w-xl mx-auto space-y-3"
              >
                {/* Feature Number */}
                <span className="text-[11px] font-mono tracking-[0.3em] text-slate-400 dark:text-slate-500 font-semibold uppercase">
                  {features[activeIndex].num} / 10
                </span>

                {/* Feature Title */}
                <h3 className="font-display text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-none transition-colors duration-300">
                  {features[activeIndex].title}
                </h3>

                {/* Feature Description */}
                <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-normal max-w-md mx-auto text-balance transition-colors duration-300">
                  {features[activeIndex].desc}
                </p>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Segmented Progress bar */}
          <div className="flex gap-2.5 items-center w-full max-w-md mt-6">
            {features.map((_, idx) => {
              let fillWidth = 0;
              if (idx < activeIndex) {
                fillWidth = 100;
              } else if (idx === activeIndex) {
                fillWidth = progress * 100;
              }
              return (
                <div key={idx} className="h-[2px] flex-1 bg-slate-200 dark:bg-white/[0.08] rounded-full overflow-hidden transition-colors duration-300">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 via-indigo-500 to-cyan-500 rounded-full transition-all duration-[40ms]"
                    style={{ width: `${fillWidth}%` }}
                  />
                </div>
              );
            })}
          </div>

          {/* Hint indicator */}
          <span className="text-[9px] font-mono tracking-[0.25em] text-slate-400 dark:text-slate-600 uppercase mt-5 animate-pulse">
            Scroll to explore features
          </span>
        </div>

      </div>
    </div>
  );
};
