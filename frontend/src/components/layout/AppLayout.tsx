import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { CommandPalette } from '../common/CommandPalette';
import { CopilotDrawer } from '../common/CopilotDrawer';
import { ParticleCanvas } from '../common/ParticleCanvas';
import { CustomCursor } from '../common/CustomCursor';

export const AppLayout: React.FC = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#090a0f] text-slate-100 relative">
      {/* Interactive WebGL/Canvas Particle Mesh Background */}
      <ParticleCanvas />

      {/* Custom Glowing Cursor Follower */}
      <CustomCursor />

      {/* Collapsible Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative z-10">
        <Header />

        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-8 bg-hero-gradient">
          <Outlet />
        </main>
      </div>

      {/* Global Modals & Drawers */}
      <CommandPalette />
      <CopilotDrawer />
    </div>
  );
};
