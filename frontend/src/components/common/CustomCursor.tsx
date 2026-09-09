import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export const CustomCursor: React.FC = () => {
  const [mousePos, setMousePos] = useState({ x: -100, y: -100 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });

      // Check if mouse is hovering an interactive element (button, link, input, card)
      const target = e.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === 'BUTTON' ||
          target.tagName === 'A' ||
          target.tagName === 'INPUT' ||
          target.closest('button') ||
          target.closest('a') ||
          target.closest('.glass-card') ||
          target.closest('.glass-panel'))
      ) {
        setIsHovered(true);
      } else {
        setIsHovered(false);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <>
      {/* Outer Glowing Cursor Spotlight */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-50 rounded-full bg-gradient-to-r from-purple-500/20 via-indigo-500/15 to-pink-500/20 blur-xl transition-transform duration-75 ease-out"
        animate={{
          x: mousePos.x - (isHovered ? 45 : 30),
          y: mousePos.y - (isHovered ? 45 : 30),
          width: isHovered ? 90 : 60,
          height: isHovered ? 90 : 60,
        }}
      />

      {/* Small Glowing Center Point */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-50 rounded-full bg-purple-400 shadow-[0_0_12px_#8b5cf6]"
        animate={{
          x: mousePos.x - 4,
          y: mousePos.y - 4,
          width: isHovered ? 12 : 8,
          height: isHovered ? 12 : 8,
          opacity: isHovered ? 0.9 : 0.6,
        }}
        transition={{ type: 'spring', damping: 30, stiffness: 400 }}
      />
    </>
  );
};
