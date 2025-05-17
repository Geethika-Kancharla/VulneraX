'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import { ArrowRight, Shield, Zap } from 'lucide-react';

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');

    if (!canvas || !ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const letters = '01'.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;

    const drops: number[] = Array(Math.floor(columns)).fill(1);

    const draw = () => {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#3b82f6';
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const text = letters[Math.floor(Math.random() * letters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }

        drops[i]++;
      }
    };

    const interval = setInterval(draw, 50);

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div className="relative min-h-screen text-white overflow-hidden">
      <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full z-0" />

      <div className="relative z-10 flex items-center justify-center min-h-screen px-6">
        <div className="text-center space-y-8 max-w-2xl">
          <span className="inline-block bg-[#1e293b] text-[#3b82f6] px-4 py-1 rounded-full text-sm font-medium">
            Autonomous AI Red Teaming
          </span>
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight">
            Redefining Web App Security
          </h1>
          <p className="text-lg text-[#94a3b8]">
            Our AI-powered red team agent autonomously scans, attacks, and reports threats — mimicking real ethical hackers with intelligent, adaptive strategies.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/dashboard"
              className="px-6 py-3 bg-[#3b82f6] text-white rounded-lg shadow hover:bg-[#2563eb] transition duration-300 flex items-center justify-center gap-2"
            >
              Get Started <ArrowRight size={18} />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-6 justify-items-center">
            {[
              'Context-Aware Payloads',
              'AI Orchestrated Attacks',
              'Real-Time Scanning',
              'Autonomous Reporting',
              'Simulated Ethical Hacking',
              'LLM-Driven Strategy',
            ].map((text, idx) => (
              <div className="flex items-center gap-2" key={idx}>
                {idx % 2 === 0 ? (
                  <Shield size={20} className="text-[#3b82f6]" />
                ) : (
                  <Zap size={20} className="text-[#3b82f6]" />
                )}
                <span className="text-[#cbd5e1] text-sm">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}