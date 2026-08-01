import React, { useEffect, useRef } from 'react';

interface Immersive3DCanvasProps {
  activeIndex: number;
  progress: number;
  mouseX: number;
  mouseY: number;
  isLight: boolean;
}

interface Point3D {
  x: number;
  y: number;
  z: number;
}

export const Immersive3DCanvas: React.FC<Immersive3DCanvasProps> = ({
  activeIndex,
  progress,
  mouseX,
  mouseY,
  isLight,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const timeRef = useRef<number>(0);
  const animationFrameRef = useRef<number | null>(null);

  // Smooth mouse coordinates with inertia
  const smoothMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = canvas.clientWidth);
    let height = (canvas.height = canvas.clientHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.clientWidth;
      height = canvas.height = canvas.clientHeight;
    };
    window.addEventListener('resize', handleResize);

    // 3D Math Helper Functions
    const rotateX = (p: Point3D, angle: number): Point3D => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return { x: p.x, y: p.y * cos - p.z * sin, z: p.y * sin + p.z * cos };
    };

    const rotateY = (p: Point3D, angle: number): Point3D => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return { x: p.x * cos + p.z * sin, y: p.y, z: -p.x * sin + p.z * cos };
    };

    const rotateZ = (p: Point3D, angle: number): Point3D => {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      return { x: p.x * cos - p.y * sin, y: p.x * sin + p.y * cos, z: p.z };
    };

    const project = (
      p: Point3D,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      let rotated = rotateZ(p, rot.z);
      rotated = rotateY(rotated, rot.y);
      rotated = rotateX(rotated, rot.x);

      const d = 600; // Camera distance
      const zOffset = rotated.z + d;
      const perspective = d / zOffset;

      const screenX = width / 2 + rotated.x * scale * perspective + parallax.x;
      const screenY = height / 2 + rotated.y * scale * perspective + parallax.y;

      return {
        x: screenX,
        y: screenY,
        z: rotated.z,
        depthAlpha: Math.max(0.1, Math.min(1.0, (rotated.z + 180) / 360)),
        scaleProj: perspective,
      };
    };

    // Style helpers based on theme
    const getWireframeColor = (alpha: number) => {
      return isLight ? `rgba(15, 23, 42, ${alpha * 0.75})` : `rgba(255, 255, 255, ${alpha})`;
    };

    const getPrimaryAccentColor = () => {
      return isLight ? 'rgba(79, 70, 229, 0.85)' : 'rgba(139, 92, 246, 0.85)'; // Violet-600 vs Purple-500
    };

    const getSecondaryAccentColor = () => {
      return isLight ? 'rgba(219, 39, 119, 0.85)' : 'rgba(236, 72, 153, 0.85)'; // Pink-600 vs Pink-500
    };

    const getCyanAccentColor = () => {
      return isLight ? 'rgba(8, 145, 178, 0.9)' : 'rgba(56, 189, 248, 0.9)'; // Cyan-600 vs Cyan-400
    };

    const fillGlassFace = (projV: any[], indices: number[]) => {
      const p1 = projV[indices[0]];
      const p2 = projV[indices[1]];
      const p3 = projV[indices[2]];
      const p4 = projV[indices[3]];

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(p4.x, p4.y);
      ctx.closePath();

      const depthVal = (p1.depthAlpha + p2.depthAlpha + p3.depthAlpha + p4.depthAlpha) / 4;
      const grad = ctx.createLinearGradient(p1.x, p1.y, p3.x, p3.y);

      if (isLight) {
        grad.addColorStop(0, `rgba(255, 255, 255, ${0.75 * depthVal})`);
        grad.addColorStop(0.5, `rgba(99, 102, 241, ${0.12 * depthVal})`);
        grad.addColorStop(1, `rgba(255, 255, 255, ${0.3 * depthVal})`);
      } else {
        grad.addColorStop(0, `rgba(255, 255, 255, ${0.12 * depthVal})`);
        grad.addColorStop(0.5, `rgba(139, 92, 246, ${0.08 * depthVal})`);
        grad.addColorStop(1, `rgba(99, 102, 241, ${0.02 * depthVal})`);
      }

      ctx.fillStyle = grad;
      ctx.fill();

      ctx.strokeStyle = getWireframeColor(0.25 * depthVal);
      ctx.lineWidth = 1;
      ctx.stroke();
    };

    // Shape drawing functions
    const drawShape = (
      type: number,
      t: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number },
      opacity: number
    ) => {
      if (opacity <= 0.01) return;
      ctx.save();
      ctx.globalAlpha = opacity;

      // Base scale calculated responsively
      const baseScale = Math.min(width, height) * 0.28;

      switch (type) {
        case 0: // 01 AI Identity Profiling (Neural sphere)
          drawNeuralSphere(t, baseScale, rot, parallax);
          break;
        case 1: // 02 Personalized Growth Plan (Roadmap/Pathway)
          drawRoadmap(t, baseScale, rot, parallax);
          break;
        case 2: // 03 Smart Resource Curation (Crystal cards)
          drawResourceCuration(t, baseScale, rot, parallax);
          break;
        case 3: // 04 Opportunity Discovery (Compass)
          drawCompass(t, baseScale, rot, parallax);
          break;
        case 4: // 05 Identity Graph (Graph network)
          drawIdentityGraph(t, baseScale, rot, parallax);
          break;
        case 5: // 06 Explainable AI Recommendations (Decision Cube)
          drawDecisionCube(t, baseScale, rot, parallax);
          break;
        case 6: // 07 Growth Analytics Dashboard (Circular arcs)
          drawAnalyticsArcs(t, baseScale, rot, parallax);
          break;
        case 7: // 08 Reflection & Feedback Loop (Rippling orb)
          drawReflectionLoop(t, baseScale, rot, parallax);
          break;
        case 8: // 09 AI Mentor Companion (Holographic assistant orb)
          drawMentorOrb(t, baseScale, rot, parallax);
          break;
        case 9: // 10 Adaptive Learning Journey (Morphing crystal)
          drawAdaptiveCrystal(t, baseScale, rot, parallax);
          break;
        default:
          break;
      }

      ctx.restore();
    };

    // --- Shape 0: Neural Sphere ---
    const drawNeuralSphere = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const points: Point3D[] = [];
      const R = 90;
      const rings = 6;
      const ringPoints = 12;

      for (let i = 1; i < rings; i++) {
        const theta = (i * Math.PI) / rings;
        for (let j = 0; j < ringPoints; j++) {
          const phi = (j * 2 * Math.PI) / ringPoints;
          points.push({
            x: R * Math.sin(theta) * Math.cos(phi),
            y: R * Math.sin(theta) * Math.sin(phi),
            z: R * Math.cos(theta),
          });
        }
      }

      const projected = points.map((p) => project(p, scale, rot, parallax));

      ctx.lineWidth = 0.8;
      ctx.strokeStyle = getWireframeColor(0.18);
      ctx.beginPath();
      for (let i = 0; i < points.length; i++) {
        const p1 = projected[i];
        const nextInRing = i - (i % ringPoints) + ((i + 1) % ringPoints);
        const p2 = projected[nextInRing];
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);

        const nextRingIdx = i + ringPoints;
        if (nextRingIdx < points.length) {
          const p3 = projected[nextRingIdx];
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p3.x, p3.y);
        }
      }
      ctx.stroke();

      projected.forEach((p, idx) => {
        const pulse = Math.sin(t * 3 + idx) * 0.3 + 0.7;
        const isGlowing = idx % 9 === 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, isGlowing ? 4.5 * pulse * p.scaleProj : 2 * p.scaleProj, 0, Math.PI * 2);
        ctx.fillStyle = isGlowing ? getSecondaryAccentColor() : getPrimaryAccentColor();

        if (isGlowing) {
          ctx.shadowBlur = isLight ? 8 : 15;
          ctx.shadowColor = isLight ? 'rgba(219, 39, 119, 0.4)' : '#ec4899';
        } else {
          ctx.shadowBlur = 0;
        }
        ctx.fill();
      });
      ctx.shadowBlur = 0;
    };

    // --- Shape 1: Roadmap/Pathway ---
    const drawRoadmap = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const steps = 14;
      const widthHalf = 45;
      const points: Point3D[] = [];

      for (let i = 0; i < steps; i++) {
        const waveX = Math.sin(i * 0.4 + t) * 35;
        const waveY = (i - steps / 2) * 16;
        const waveZ = Math.cos(i * 0.4 + t) * 25;

        points.push({ x: waveX - widthHalf, y: waveY, z: waveZ });
        points.push({ x: waveX + widthHalf, y: waveY, z: waveZ });
      }

      const projected = points.map((p) => project(p, scale, rot, parallax));

      for (let i = 0; i < steps - 1; i++) {
        const idx = i * 2;
        const p1 = projected[idx];
        const p2 = projected[idx + 1];
        const p3 = projected[idx + 3];
        const p4 = projected[idx + 2];

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.lineTo(p3.x, p3.y);
        ctx.lineTo(p4.x, p4.y);
        ctx.closePath();

        const avgDepth = (p1.depthAlpha + p2.depthAlpha + p3.depthAlpha + p4.depthAlpha) / 4;

        if (isLight) {
          ctx.fillStyle = `rgba(99, 102, 241, ${0.12 * avgDepth})`;
        } else {
          ctx.fillStyle = `rgba(99, 102, 241, ${0.1 * avgDepth})`;
        }
        ctx.fill();

        ctx.strokeStyle = getWireframeColor(0.25 * avgDepth);
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.strokeStyle = isLight ? 'rgba(219, 39, 119, 0.7)' : 'rgba(236, 72, 153, 0.6)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for (let i = 0; i < steps - 1; i++) {
        const pLeft1 = points[i * 2];
        const pRight1 = points[i * 2 + 1];
        const pLeft2 = points[(i + 1) * 2];
        const pRight2 = points[(i + 1) * 2 + 1];

        const center1 = project(
          { x: (pLeft1.x + pRight1.x) / 2, y: (pLeft1.y + pRight1.y) / 2, z: (pLeft1.z + pRight1.z) / 2 },
          scale,
          rot,
          parallax
        );
        const center2 = project(
          { x: (pLeft2.x + pRight2.x) / 2, y: (pLeft2.y + pRight2.y) / 2, z: (pLeft2.z + pRight2.z) / 2 },
          scale,
          rot,
          parallax
        );

        if (i % 2 === 0) {
          ctx.moveTo(center1.x, center1.y);
          ctx.lineTo(center2.x, center2.y);
        }
      }
      ctx.stroke();

      for (let i = 2; i < steps; i += 4) {
        const pLeft = points[i * 2];
        const pRight = points[i * 2 + 1];
        const marker = project(
          {
            x: (pLeft.x + pRight.x) / 2,
            y: (pLeft.y + pRight.y) / 2 - 12,
            z: (pLeft.z + pRight.z) / 2,
          },
          scale,
          rot,
          parallax
        );

        ctx.beginPath();
        ctx.arc(marker.x, marker.y, 5 * marker.scaleProj, 0, Math.PI * 2);
        ctx.fillStyle = getCyanAccentColor();
        ctx.shadowBlur = isLight ? 8 : 12;
        ctx.shadowColor = isLight ? 'rgba(8, 145, 178, 0.4)' : '#38bdf8';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(marker.x, marker.y, 10 * marker.scaleProj, 0, Math.PI * 2);
        ctx.strokeStyle = isLight ? 'rgba(8, 145, 178, 0.25)' : 'rgba(56, 189, 248, 0.3)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      ctx.shadowBlur = 0;
    };

    // --- Shape 2: Resource Curation (Crystal orbiting cards) ---
    const drawResourceCuration = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const core = project({ x: 0, y: 0, z: 0 }, scale, rot, parallax);

      const cardCount = 3;
      const orbitRadius = 100;
      const cardWidth = 40;
      const cardHeight = 55;

      const cardsData: { center: Point3D; angle: number; yOff: number }[] = [];

      for (let i = 0; i < cardCount; i++) {
        const angle = t + (i * 2 * Math.PI) / cardCount;
        const yOff = Math.sin(t * 1.5 + i) * 15;
        cardsData.push({
          center: {
            x: Math.cos(angle) * orbitRadius,
            y: yOff,
            z: Math.sin(angle) * orbitRadius,
          },
          angle,
          yOff,
        });
      }

      const projectedCards = cardsData.map((c, i) => {
        const proj = project(c.center, scale, rot, parallax);
        return { ...c, proj, index: i };
      });

      projectedCards.sort((a, b) => b.proj.z - a.proj.z);

      projectedCards.forEach((card) => {
        const cx = card.center.x;
        const cy = card.center.y;
        const cz = card.center.z;

        const theta = card.angle + Math.PI / 2;
        const cosT = Math.cos(theta);
        const sinT = Math.sin(theta);

        const localVertices: Point3D[] = [
          { x: -cardWidth / 2 * cosT, y: -cardHeight / 2, z: -cardWidth / 2 * sinT },
          { x: cardWidth / 2 * cosT, y: -cardHeight / 2, z: cardWidth / 2 * sinT },
          { x: cardWidth / 2 * cosT, y: cardHeight / 2, z: cardWidth / 2 * sinT },
          { x: -cardWidth / 2 * cosT, y: cardHeight / 2, z: -cardWidth / 2 * sinT },
        ];

        const cardVertices = localVertices.map((v) => ({
          x: cx + v.x,
          y: cy + v.y,
          z: cz + v.z,
        }));

        const projV = cardVertices.map((v) => project(v, scale, rot, parallax));

        ctx.beginPath();
        ctx.moveTo(projV[0].x, projV[0].y);
        ctx.lineTo(projV[1].x, projV[1].y);
        ctx.lineTo(projV[2].x, projV[2].y);
        ctx.lineTo(projV[3].x, projV[3].y);
        ctx.closePath();

        const grad = ctx.createLinearGradient(projV[0].x, projV[0].y, projV[2].x, projV[2].y);
        if (isLight) {
          grad.addColorStop(0, 'rgba(255, 255, 255, 0.88)');
          grad.addColorStop(0.5, 'rgba(99, 102, 241, 0.15)');
          grad.addColorStop(1, 'rgba(255, 255, 255, 0.4)');
        } else {
          grad.addColorStop(0, 'rgba(255, 255, 255, 0.12)');
          grad.addColorStop(0.5, 'rgba(139, 92, 246, 0.08)');
          grad.addColorStop(1, 'rgba(99, 102, 241, 0.02)');
        }
        ctx.fillStyle = grad;
        ctx.fill();

        ctx.strokeStyle = getWireframeColor(0.28);
        ctx.lineWidth = 1;
        ctx.stroke();

        const tagPos = project(
          { x: cx, y: cy - cardHeight / 3, z: cz },
          scale,
          rot,
          parallax
        );
        ctx.beginPath();
        ctx.arc(tagPos.x, tagPos.y, 3 * tagPos.scaleProj, 0, Math.PI * 2);

        const cardColor = card.index === 0 ? getCyanAccentColor() : card.index === 1 ? getSecondaryAccentColor() : '#a855f7';
        ctx.fillStyle = cardColor;
        ctx.shadowBlur = isLight ? 6 : 10;
        ctx.shadowColor = cardColor;
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      ctx.beginPath();
      ctx.arc(core.x, core.y, 16 * core.scaleProj, 0, Math.PI * 2);
      const radGrad = ctx.createRadialGradient(
        core.x,
        core.y,
        0,
        core.x,
        core.y,
        16 * core.scaleProj
      );

      if (isLight) {
        radGrad.addColorStop(0, '#ffffff');
        radGrad.addColorStop(0.4, 'rgba(79, 70, 229, 0.8)');
        radGrad.addColorStop(1, 'rgba(99, 102, 241, 0)');
      } else {
        radGrad.addColorStop(0, '#ffffff');
        radGrad.addColorStop(0.3, 'rgba(139, 92, 246, 0.9)');
        radGrad.addColorStop(0.7, 'rgba(99, 102, 241, 0.4)');
        radGrad.addColorStop(1, 'rgba(99, 102, 241, 0)');
      }

      ctx.fillStyle = radGrad;
      ctx.shadowBlur = isLight ? 12 : 20;
      ctx.shadowColor = isLight ? 'rgba(79, 70, 229, 0.5)' : '#6366f1';
      ctx.fill();
      ctx.shadowBlur = 0;
    };

    // --- Shape 3: Opportunity Discovery (Compass) ---
    const drawCompass = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const pointsRingCount = 24;
      const radius = 90;
      const ringPoints: Point3D[] = [];

      for (let i = 0; i < pointsRingCount; i++) {
        const angle = (i * 2 * Math.PI) / pointsRingCount;
        ringPoints.push({
          x: Math.cos(angle) * radius,
          y: 0,
          z: Math.sin(angle) * radius,
        });
      }

      const projRing = ringPoints.map((p) => project(p, scale, rot, parallax));

      ctx.beginPath();
      projRing.forEach((p, idx) => {
        if (idx === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      ctx.closePath();
      ctx.strokeStyle = getWireframeColor(0.2);
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.strokeStyle = isLight ? 'rgba(79, 70, 229, 0.35)' : 'rgba(99, 102, 241, 0.4)';
      ctx.beginPath();
      for (let i = 0; i < pointsRingCount; i++) {
        const outer = ringPoints[i];
        const inner = {
          x: outer.x * 0.9,
          y: 0,
          z: outer.z * 0.9,
        };
        const pOuter = projRing[i];
        const pInner = project(inner, scale, rot, parallax);

        ctx.moveTo(pOuter.x, pOuter.y);
        ctx.lineTo(pInner.x, pInner.y);
      }
      ctx.stroke();

      const needleAngle = t * 0.8;
      const cosN = Math.cos(needleAngle);
      const sinN = Math.sin(needleAngle);
      const len = 70;
      const wide = 14;
      const thick = 8;

      const needlePoints: Point3D[] = [
        { x: cosN * len, y: 0, z: sinN * len },
        { x: -cosN * len, y: 0, z: -sinN * len },
        { x: sinN * wide, y: 0, z: -cosN * wide },
        { x: -sinN * wide, y: 0, z: cosN * wide },
        { x: 0, y: thick, z: 0 },
        { x: 0, y: -thick, z: 0 },
      ];

      const projNeedle = needlePoints.map((p) => project(p, scale, rot, parallax));

      const faces = [
        [0, 2, 4, isLight ? 'rgba(219, 39, 119, 0.7)' : 'rgba(236, 72, 153, 0.6)'],
        [0, 3, 4, isLight ? 'rgba(79, 70, 229, 0.7)' : 'rgba(139, 92, 246, 0.65)'],
        [1, 2, 4, isLight ? 'rgba(99, 102, 241, 0.5)' : 'rgba(99, 102, 241, 0.4)'],
        [1, 3, 4, isLight ? 'rgba(99, 102, 241, 0.55)' : 'rgba(99, 102, 241, 0.45)'],
        [0, 2, 5, isLight ? 'rgba(219, 39, 119, 0.5)' : 'rgba(236, 72, 153, 0.4)'],
        [0, 3, 5, isLight ? 'rgba(79, 70, 229, 0.5)' : 'rgba(139, 92, 246, 0.45)'],
        [1, 2, 5, isLight ? 'rgba(99, 102, 241, 0.4)' : 'rgba(99, 102, 241, 0.3)'],
        [1, 3, 5, isLight ? 'rgba(99, 102, 241, 0.45)' : 'rgba(99, 102, 241, 0.35)'],
      ];

      faces.forEach(([idxA, idxB, idxC, color]) => {
        const pA = projNeedle[idxA as number];
        const pB = projNeedle[idxB as number];
        const pC = projNeedle[idxC as number];

        ctx.beginPath();
        ctx.moveTo(pA.x, pA.y);
        ctx.lineTo(pB.x, pB.y);
        ctx.lineTo(pC.x, pC.y);
        ctx.closePath();
        ctx.fillStyle = color as string;
        ctx.fill();
        ctx.strokeStyle = getWireframeColor(0.2);
        ctx.lineWidth = 0.5;
        ctx.stroke();
      });

      const destinations = [
        { x: -110, y: -40, z: -30 },
        { x: 120, y: 30, z: -50 },
        { x: -50, y: 60, z: 100 },
      ];

      destinations.forEach((dest, idx) => {
        const wX = dest.x + Math.sin(t * 2 + idx) * 10;
        const wY = dest.y + Math.cos(t * 2 + idx) * 10;
        const projDest = project({ x: wX, y: wY, z: dest.z }, scale, rot, parallax);

        ctx.beginPath();
        ctx.arc(projDest.x, projDest.y, 4 * projDest.scaleProj, 0, Math.PI * 2);
        ctx.fillStyle = getCyanAccentColor();
        ctx.shadowBlur = isLight ? 8 : 12;
        ctx.shadowColor = isLight ? 'rgba(8, 145, 178, 0.4)' : '#38bdf8';
        ctx.fill();

        const ringPulse = ((t * 1.5 + idx) % 2) / 2;
        ctx.beginPath();
        ctx.arc(projDest.x, projDest.y, 14 * ringPulse * projDest.scaleProj, 0, Math.PI * 2);
        ctx.strokeStyle = isLight ? `rgba(8, 145, 178, ${0.5 * (1 - ringPulse)})` : `rgba(56, 189, 248, ${0.6 * (1 - ringPulse)})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      });
      ctx.shadowBlur = 0;
    };

    // --- Shape 4: Identity Graph ---
    const drawIdentityGraph = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const baseNodes: Point3D[] = [
        { x: 0, y: 0, z: 0 },
        { x: -70, y: -50, z: -30 },
        { x: 70, y: -60, z: 40 },
        { x: -40, y: 70, z: -20 },
        { x: 50, y: 55, z: -50 },
        { x: -90, y: 10, z: 30 },
        { x: 80, y: 15, z: -40 },
        { x: -10, y: -80, z: 20 },
        { x: 20, y: 85, z: 30 },
        { x: -60, y: -20, z: -80 },
        { x: 60, y: -10, z: -80 },
        { x: 0, y: -40, z: 90 },
      ];

      const edges = [
        [0, 1], [0, 2], [0, 3], [0, 4], [0, 11],
        [1, 5], [1, 7], [1, 9],
        [2, 6], [2, 7], [2, 10],
        [3, 5], [3, 8],
        [4, 6], [4, 8], [4, 10],
        [9, 10], [11, 7], [11, 8],
      ];

      const nodes = baseNodes.map((n, idx) => {
        if (idx === 0) return n;
        const angle = t * 1.2 + idx;
        return {
          x: n.x + Math.sin(angle) * 12,
          y: n.y + Math.cos(angle * 0.8) * 12,
          z: n.z + Math.sin(angle * 1.5) * 8,
        };
      });

      const projected = nodes.map((n) => project(n, scale, rot, parallax));

      ctx.beginPath();
      edges.forEach(([a, b]) => {
        const pA = projected[a];
        const pB = projected[b];
        ctx.moveTo(pA.x, pA.y);
        ctx.lineTo(pB.x, pB.y);
      });
      ctx.lineWidth = 0.8;
      ctx.strokeStyle = getWireframeColor(0.2);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(projected[0].x, projected[0].y);
      ctx.lineTo(projected[1].x, projected[1].y);
      ctx.moveTo(projected[0].x, projected[0].y);
      ctx.lineTo(projected[2].x, projected[2].y);
      ctx.moveTo(projected[0].x, projected[0].y);
      ctx.lineTo(projected[3].x, projected[3].y);
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = isLight ? 'rgba(79, 70, 229, 0.5)' : 'rgba(139, 92, 246, 0.4)';
      ctx.stroke();

      projected.forEach((p, idx) => {
        const size = idx === 0 ? 8 : idx % 3 === 0 ? 5 : 3.5;

        let color = getPrimaryAccentColor();
        if (idx === 0) color = getSecondaryAccentColor();
        else if (idx % 3 === 0) color = getCyanAccentColor();

        ctx.beginPath();
        ctx.arc(p.x, p.y, size * p.scaleProj, 0, Math.PI * 2);
        ctx.fillStyle = color;

        if (idx === 0 || idx === 1 || idx === 2) {
          ctx.shadowBlur = isLight ? 6 : 15;
          ctx.shadowColor = color;
        } else {
          ctx.shadowBlur = 0;
        }
        ctx.fill();
      });
      ctx.shadowBlur = 0;
    };

    // --- Shape 5: Explainable AI (Decision Cube) ---
    const drawDecisionCube = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const size = 60;
      const vertices: Point3D[] = [
        { x: -size, y: -size, z: -size },
        { x: size, y: -size, z: -size },
        { x: size, y: size, z: -size },
        { x: -size, y: size, z: -size },
        { x: -size, y: -size, z: size },
        { x: size, y: -size, z: size },
        { x: size, y: size, z: size },
        { x: -size, y: size, z: size },
      ];

      const projV = vertices.map((v) => project(v, scale, rot, parallax));

      const faces = [
        [0, 1, 2, 3], // Back
        [4, 5, 6, 7], // Front
        [0, 1, 5, 4], // Top
        [2, 3, 7, 6], // Bottom
        [0, 3, 7, 4], // Left
        [1, 2, 6, 5], // Right
      ];

      const facesWithDepth = faces.map((f, i) => {
        const avgDepth = (projV[f[0]].z + projV[f[1]].z + projV[f[2]].z + projV[f[3]].z) / 4;
        return { indices: f, avgDepth, index: i };
      });
      facesWithDepth.sort((a, b) => b.avgDepth - a.avgDepth);

      const treePoints: Point3D[] = [
        { x: 0, y: size, z: 0 },
        { x: 0, y: 15, z: 0 },
        { x: -30, y: -15, z: -20 },
        { x: 30, y: -15, z: 20 },
        { x: -45, y: -45, z: -35 },
        { x: -15, y: -45, z: -5 },
        { x: 15, y: -45, z: 5 },
        { x: 45, y: -45, z: 35 },
      ];

      const projTree = treePoints.map((tp) => project(tp, scale, rot, parallax));

      facesWithDepth.forEach((face) => {
        const isFrontFace = face.avgDepth > 0;
        if (!isFrontFace) {
          fillGlassFace(projV, face.indices);
        }
      });

      ctx.strokeStyle = isLight ? 'rgba(8, 145, 178, 0.8)' : 'rgba(56, 189, 248, 0.7)';
      ctx.lineWidth = 1.5;
      ctx.shadowBlur = isLight ? 6 : 12;
      ctx.shadowColor = isLight ? 'rgba(8, 145, 178, 0.4)' : '#38bdf8';
      ctx.beginPath();
      ctx.moveTo(projTree[0].x, projTree[0].y);
      ctx.lineTo(projTree[1].x, projTree[1].y);
      ctx.moveTo(projTree[1].x, projTree[1].y);
      ctx.lineTo(projTree[2].x, projTree[2].y);
      ctx.moveTo(projTree[1].x, projTree[1].y);
      ctx.lineTo(projTree[3].x, projTree[3].y);
      ctx.moveTo(projTree[2].x, projTree[2].y);
      ctx.lineTo(projTree[4].x, projTree[4].y);
      ctx.moveTo(projTree[2].x, projTree[2].y);
      ctx.lineTo(projTree[5].x, projTree[5].y);
      ctx.moveTo(projTree[3].x, projTree[3].y);
      ctx.lineTo(projTree[6].x, projTree[6].y);
      ctx.moveTo(projTree[3].x, projTree[3].y);
      ctx.lineTo(projTree[7].x, projTree[7].y);
      ctx.stroke();
      ctx.shadowBlur = 0;

      projTree.forEach((pt, idx) => {
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, (idx === 0 ? 5 : idx >= 4 ? 4 : 3) * pt.scaleProj, 0, Math.PI * 2);
        ctx.fillStyle = idx >= 4 ? getSecondaryAccentColor() : getCyanAccentColor();
        ctx.fill();
      });

      facesWithDepth.forEach((face) => {
        const isFrontFace = face.avgDepth > 0;
        if (isFrontFace) {
          fillGlassFace(projV, face.indices);
        }
      });
    };

    // --- Shape 6: Analytics Dashboard ---
    const drawAnalyticsArcs = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const drawArcRing = (radius: number, yOff: number, progressPct: number, color: string, speedMult: number) => {
        const stepsCount = 60;
        const startAng = t * speedMult;
        const endAng = startAng + 2 * Math.PI * progressPct;

        const points: Point3D[] = [];
        for (let i = 0; i <= stepsCount; i++) {
          const angle = startAng + (endAng - startAng) * (i / stepsCount);
          points.push({
            x: Math.cos(angle) * radius,
            y: yOff,
            z: Math.sin(angle) * radius,
          });
        }

        const proj = points.map((p) => project(p, scale, rot, parallax));

        ctx.beginPath();
        proj.forEach((p, idx) => {
          if (idx === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.stroke();

        const trackEndAng = startAng + 2 * Math.PI;
        const trackPoints: Point3D[] = [];
        const trackSteps = 30;
        for (let i = 0; i <= trackSteps; i++) {
          const angle = endAng + (trackEndAng - endAng) * (i / trackSteps);
          trackPoints.push({
            x: Math.cos(angle) * radius,
            y: yOff,
            z: Math.sin(angle) * radius,
          });
        }
        const projTrack = trackPoints.map((p) => project(p, scale, rot, parallax));

        ctx.beginPath();
        projTrack.forEach((p, idx) => {
          if (idx === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.strokeStyle = getWireframeColor(0.08);
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
      };

      drawArcRing(95, -35, 0.72, getSecondaryAccentColor(), 0.6);
      drawArcRing(75, 0, 0.88, getPrimaryAccentColor(), -0.4);
      drawArcRing(55, 35, 0.64, getCyanAccentColor(), 0.8);

      const coreTop = project({ x: 0, y: -45, z: 0 }, scale, rot, parallax);
      const coreBottom = project({ x: 0, y: 45, z: 0 }, scale, rot, parallax);

      ctx.beginPath();
      ctx.moveTo(coreTop.x, coreTop.y);
      ctx.lineTo(coreBottom.x, coreBottom.y);
      ctx.strokeStyle = getWireframeColor(0.1);
      ctx.lineWidth = 1;
      ctx.stroke();
    };

    // --- Shape 7: Reflection Loop (Memory Orb & Ripples) ---
    const drawReflectionLoop = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const centerOrb = project({ x: 0, y: 0, z: 0 }, scale, rot, parallax);

      const wavesCount = 3;
      for (let i = 0; i < wavesCount; i++) {
        const waveAge = ((t * 0.8 + i / wavesCount) % 1.0);
        const R = 35 + waveAge * 90;
        const waveOpacity = (1.0 - waveAge) * 0.6;

        const ringPoints: Point3D[] = [];
        const ringRes = 32;
        for (let j = 0; j < ringRes; j++) {
          const angle = (j * 2 * Math.PI) / ringRes;
          ringPoints.push({
            x: Math.cos(angle) * R,
            y: 0,
            z: Math.sin(angle) * R,
          });
        }

        const projWave = ringPoints.map((p) => project(p, scale, rot, parallax));

        ctx.beginPath();
        projWave.forEach((p, idx) => {
          if (idx === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.closePath();
        ctx.strokeStyle = isLight ? `rgba(99, 102, 241, ${waveOpacity * 0.85})` : `rgba(139, 92, 246, ${waveOpacity})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.arc(centerOrb.x, centerOrb.y, 18 * centerOrb.scaleProj, 0, Math.PI * 2);
      const radGrad = ctx.createRadialGradient(
        centerOrb.x,
        centerOrb.y,
        0,
        centerOrb.x,
        centerOrb.y,
        18 * centerOrb.scaleProj
      );

      if (isLight) {
        radGrad.addColorStop(0, '#ffffff');
        radGrad.addColorStop(0.4, 'rgba(219, 39, 119, 0.8)');
        radGrad.addColorStop(1, 'rgba(219, 39, 119, 0)');
      } else {
        radGrad.addColorStop(0, '#ffffff');
        radGrad.addColorStop(0.3, 'rgba(236, 72, 153, 0.9)');
        radGrad.addColorStop(0.7, 'rgba(139, 92, 246, 0.4)');
        radGrad.addColorStop(1, 'rgba(139, 92, 246, 0)');
      }

      ctx.fillStyle = radGrad;
      ctx.shadowBlur = isLight ? 12 : 20;
      ctx.shadowColor = isLight ? 'rgba(219, 39, 119, 0.45)' : '#ec4899';
      ctx.fill();
      ctx.shadowBlur = 0;
    };

    // --- Shape 8: AI Mentor Companion ---
    const drawMentorOrb = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const center = project({ x: 0, y: 0, z: 0 }, scale, rot, parallax);

      const drawGyroRing = (radius: number, color: string, rotAngle: number, axis: 'x' | 'y' | 'z') => {
        const ringPoints: Point3D[] = [];
        const res = 48;
        for (let i = 0; i < res; i++) {
          const angle = (i * 2 * Math.PI) / res;
          let point: Point3D;

          if (axis === 'x') {
            point = { x: 0, y: Math.cos(angle) * radius, z: Math.sin(angle) * radius };
          } else if (axis === 'y') {
            point = { x: Math.cos(angle) * radius, y: 0, z: Math.sin(angle) * radius };
          } else {
            point = { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius, z: 0 };
          }

          ringPoints.push(point);
        }

        const gyroRot = {
          x: rot.x + (axis === 'x' ? rotAngle : 0),
          y: rot.y + (axis === 'y' ? rotAngle : 0),
          z: rot.z + (axis === 'z' ? rotAngle : 0),
        };

        const proj = ringPoints.map((p) => project(p, scale, gyroRot, parallax));

        ctx.beginPath();
        proj.forEach((p, idx) => {
          if (idx === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.closePath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.2;
        ctx.stroke();

        const sliderIdx = Math.floor(((t * 0.4) % 1.0) * res);
        const sliderNode = proj[sliderIdx];
        if (sliderNode) {
          ctx.beginPath();
          ctx.arc(sliderNode.x, sliderNode.y, 3.5 * sliderNode.scaleProj, 0, Math.PI * 2);
          ctx.fillStyle = isLight ? '#000000' : '#ffffff';
          ctx.shadowBlur = isLight ? 4 : 10;
          ctx.shadowColor = color;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      };

      drawGyroRing(85, isLight ? 'rgba(8, 145, 178, 0.75)' : 'rgba(56, 189, 248, 0.7)', t * 1.2, 'y');
      drawGyroRing(70, isLight ? 'rgba(79, 70, 229, 0.75)' : 'rgba(139, 92, 246, 0.7)', -t * 0.9, 'x');
      drawGyroRing(100, isLight ? 'rgba(219, 39, 119, 0.55)' : 'rgba(236, 72, 153, 0.5)', t * 0.7, 'z');

      const pulseSize = 14 + Math.sin(t * 4) * 2;
      ctx.beginPath();
      ctx.arc(center.x, center.y, pulseSize * center.scaleProj, 0, Math.PI * 2);
      const radGrad = ctx.createRadialGradient(
        center.x,
        center.y,
        0,
        center.x,
        center.y,
        pulseSize * center.scaleProj
      );

      if (isLight) {
        radGrad.addColorStop(0, '#ffffff');
        radGrad.addColorStop(0.4, 'rgba(8, 145, 178, 0.85)');
        radGrad.addColorStop(1, 'rgba(8, 145, 178, 0)');
      } else {
        radGrad.addColorStop(0, '#ffffff');
        radGrad.addColorStop(0.4, 'rgba(56, 189, 248, 0.9)');
        radGrad.addColorStop(0.8, 'rgba(139, 92, 246, 0.3)');
        radGrad.addColorStop(1, 'rgba(139, 92, 246, 0)');
      }

      ctx.fillStyle = radGrad;
      ctx.shadowBlur = isLight ? 8 : 15;
      ctx.shadowColor = isLight ? 'rgba(8, 145, 178, 0.5)' : '#38bdf8';
      ctx.fill();
      ctx.shadowBlur = 0;
    };

    // --- Shape 9: Adaptive Learning Journey ---
    const drawAdaptiveCrystal = (
      t: number,
      scale: number,
      rot: { x: number; y: number; z: number },
      parallax: { x: number; y: number }
    ) => {
      const phi = (1 + Math.sqrt(5)) / 2;
      const baseVertices: Point3D[] = [
        { x: -1, y: phi, z: 0 },
        { x: 1, y: phi, z: 0 },
        { x: -1, y: -phi, z: 0 },
        { x: 1, y: -phi, z: 0 },
        { x: 0, y: -1, z: phi },
        { x: 0, y: 1, z: phi },
        { x: 0, y: -1, z: -phi },
        { x: 0, y: 1, z: -phi },
        { x: phi, y: 0, z: -1 },
        { x: phi, y: 0, z: 1 },
        { x: -phi, y: 0, z: -1 },
        { x: -phi, y: 0, z: 1 },
      ];

      const faceIndices = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
      ];

      const pulseFactor = 48 + Math.sin(t * 2.5) * 12;

      const vertices = baseVertices.map((v) => ({
        x: v.x * pulseFactor,
        y: v.y * pulseFactor,
        z: v.z * pulseFactor,
      }));

      const projV = vertices.map((v) => project(v, scale, rot, parallax));

      const facesWithDepth = faceIndices.map((f, i) => {
        const avgDepth = (projV[f[0]].z + projV[f[1]].z + projV[f[2]].z) / 3;
        return { indices: f, avgDepth, index: i };
      });
      facesWithDepth.sort((a, b) => b.avgDepth - a.avgDepth);

      facesWithDepth.forEach((face) => {
        const p1 = projV[face.indices[0]];
        const p2 = projV[face.indices[1]];
        const p3 = projV[face.indices[2]];

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.lineTo(p3.x, p3.y);
        ctx.closePath();

        const depthVal = (p1.depthAlpha + p2.depthAlpha + p3.depthAlpha) / 3;
        const grad = ctx.createLinearGradient(p1.x, p1.y, p3.x, p3.y);

        if (isLight) {
          grad.addColorStop(0, `rgba(255, 255, 255, ${0.75 * depthVal})`);
          grad.addColorStop(0.5, `rgba(99, 102, 241, ${0.12 * depthVal})`);
          grad.addColorStop(1, `rgba(255, 255, 255, ${0.3 * depthVal})`);
        } else {
          grad.addColorStop(0, `rgba(56, 189, 248, ${0.18 * depthVal})`);
          grad.addColorStop(0.5, `rgba(139, 92, 246, ${0.1 * depthVal})`);
          grad.addColorStop(1, `rgba(236, 72, 153, ${0.02 * depthVal})`);
        }

        ctx.fillStyle = grad;
        ctx.fill();

        ctx.strokeStyle = getWireframeColor(0.25 * depthVal);
        ctx.lineWidth = 0.8;
        ctx.stroke();
      });

      projV.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 4 * p.scaleProj, 0, Math.PI * 2);
        ctx.fillStyle = getCyanAccentColor();
        ctx.shadowBlur = isLight ? 6 : 10;
        ctx.shadowColor = getCyanAccentColor();
        ctx.fill();
      });
      ctx.shadowBlur = 0;
    };

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      smoothMouse.current.x += (mouseX - smoothMouse.current.x) * 0.08;
      smoothMouse.current.y += (mouseY - smoothMouse.current.y) * 0.08;

      const parallax = {
        x: smoothMouse.current.x * 25,
        y: smoothMouse.current.y * 20,
      };

      const t = timeRef.current;

      const baseRotation = {
        x: 0.3 + Math.sin(t * 0.15) * 0.1,
        y: t * 0.25 + smoothMouse.current.x * 0.3,
        z: Math.cos(t * 0.1) * 0.1 + smoothMouse.current.y * 0.2,
      };

      const nextIndex = Math.min(activeIndex + 1, 9);
      const isTransitioning = progress > 0;

      if (isTransitioning && activeIndex !== 9) {
        const transitionSpin = progress * Math.PI * 0.5;

        drawShape(
          activeIndex,
          t,
          { ...baseRotation, y: baseRotation.y + transitionSpin },
          parallax,
          1 - progress
        );

        drawShape(
          nextIndex,
          t,
          { ...baseRotation, y: baseRotation.y - (1 - progress) * Math.PI * 0.5 },
          parallax,
          progress
        );
      } else {
        drawShape(activeIndex, t, baseRotation, parallax, 1.0);
      }

      timeRef.current += 0.03;
      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [activeIndex, progress, mouseX, mouseY, isLight]);

  return <canvas ref={canvasRef} className="w-full h-full block" />;
};
