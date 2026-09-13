'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, TrendingUp, Landmark, CheckCircle2, Sprout, ShieldCheck, FileCheck2 } from 'lucide-react';
import { useLanguage } from '@/lib/i18n/useLanguage';

export default function FarmerHeroIllustration() {
  const { language } = useLanguage();
  const [activeCard, setActiveCard] = useState<string | null>(null);

  return (
    <div className="w-full max-w-5xl mx-auto my-6 space-y-5">
      {/* 1. REFINED HERO VISUAL STAGE */}
      <div className="relative w-full h-[340px] sm:h-[380px] md:h-[420px] rounded-3xl overflow-hidden shadow-xl border border-emerald-200/90 bg-gradient-to-b from-sky-200 via-sky-50 to-emerald-900/90 select-none">
        
        {/* Sky Ambient Lights & Sun Glow */}
        <div className="absolute inset-0 pointer-events-none">
          <motion.div
            animate={{ scale: [1, 1.05, 1], opacity: [0.8, 0.95, 0.8] }}
            transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute top-4 right-12 w-28 h-28 sm:w-36 sm:h-36 rounded-full bg-gradient-to-tr from-amber-400 via-yellow-200 to-amber-100 blur-lg opacity-85 shadow-[0_0_90px_rgba(245,158,11,0.5)]"
          />
          
          {/* Subtle Floating Cloud Layers */}
          <motion.div
            animate={{ x: [-15, 25, -15] }}
            transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute top-8 left-8 w-44 h-12 bg-white/60 backdrop-blur-xs rounded-full blur-[1px]"
          />
          <motion.div
            animate={{ x: [25, -15, 25] }}
            transition={{ duration: 28, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute top-14 right-1/4 w-56 h-14 bg-white/50 backdrop-blur-xs rounded-full blur-[1px]"
          />
        </div>

        {/* Dynamic Growth Data Contours (Subtle Tech & Financial Grid Lines) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-25" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="heroGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#047857" strokeWidth="0.75" strokeDasharray="3 3" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#heroGrid)" />
        </svg>

        {/* Refined Tricolor Ribbon Contour Accent */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-10" preserveAspectRatio="none" viewBox="0 0 1000 500">
          <defs>
            <linearGradient id="tricolorOrange" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FF9933" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#EA580C" stopOpacity="0.9" />
            </linearGradient>
            <linearGradient id="tricolorWhite" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#F1F5F9" stopOpacity="0.95" />
            </linearGradient>
            <linearGradient id="tricolorGreen" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#138808" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#047857" stopOpacity="0.95" />
            </linearGradient>
          </defs>
          <path d="M-30,340 C 260,210 480,430 1030,220" stroke="url(#tricolorOrange)" strokeWidth="18" fill="none" className="filter drop-shadow-sm opacity-90" />
          <path d="M-30,354 C 260,224 480,444 1030,234" stroke="url(#tricolorWhite)" strokeWidth="16" fill="none" className="filter drop-shadow-xs opacity-95" />
          <path d="M-30,368 C 260,238 480,458 1030,248" stroke="url(#tricolorGreen)" strokeWidth="18" fill="none" className="filter drop-shadow-sm opacity-90" />
        </svg>

        {/* Indian Enterprise Landscape: Terrace Fields & Architecture Silhouette (Right Side) */}
        <div className="absolute bottom-6 right-4 sm:right-10 md:right-16 z-20 pointer-events-none opacity-80">
          <svg className="w-56 sm:w-72 md:w-88 h-36 sm:h-48 text-emerald-950/40" viewBox="0 0 340 220" fill="currentColor">
            {/* Monument / Parliament & Growth Pillars Silhouette */}
            <path d="M 70 210 L 70 95 L 60 95 L 60 80 L 80 80 L 80 50 L 70 50 L 70 40 L 150 40 L 150 50 L 140 50 L 140 80 L 160 80 L 160 95 L 150 95 L 150 210 L 125 210 L 125 125 Q 110 105 95 125 L 95 210 Z" />
            <path d="M 180 210 L 180 115 Q 235 65 290 115 L 290 210 Z" opacity="0.65" />
            <rect x="230" y="55" width="10" height="25" opacity="0.65" />
            {/* Solar Panel & Agri-Tech clean modern shapes */}
            <polygon points="260,180 320,165 315,195 255,210" opacity="0.5" />
            <line x1="285" y1="172" x2="285" y2="205" stroke="currentColor" strokeWidth="2" />
          </svg>
        </div>

        {/* Dignified Indian Farmer & Artisan Entrepreneur Silhouette (Left Side) */}
        <div className="absolute bottom-0 left-6 sm:left-12 z-30 flex items-end">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="relative"
          >
            <div className="relative w-40 sm:w-52 md:w-60 h-56 sm:h-72 md:h-80">
              <svg viewBox="0 0 200 260" className="w-full h-full drop-shadow-xl">
                {/* Kurta Body */}
                <path d="M 32 260 L 46 160 Q 100 145 154 160 L 168 260 Z" fill="#F8FAFC" stroke="#CBD5E1" strokeWidth="2.5" />
                {/* Nehru Jacket in deep forest green */}
                <path d="M 55 170 Q 100 160 145 170 L 140 260 L 110 260 L 110 192 L 90 192 L 90 260 L 60 260 Z" fill="#064E3B" />
                {/* Gamcha / Saffron & Green Shoulder Accents */}
                <path d="M 40 170 Q 68 220 58 260 L 45 260 Q 54 210 36 175 Z" fill="#FF9933" />
                <path d="M 160 170 Q 132 220 142 260 L 155 260 Q 146 210 164 175 Z" fill="#138808" />

                {/* Neck & Face Tone */}
                <path d="M 85 140 L 85 165 Q 100 172 115 165 L 115 140 Z" fill="#D97706" />
                <ellipse cx="100" cy="110" rx="32" ry="38" fill="#D97706" />

                {/* Ears */}
                <circle cx="67" cy="110" r="7" fill="#D97706" />
                <circle cx="133" cy="110" r="7" fill="#D97706" />

                {/* Pagri (Turban) */}
                <path d="M 62 95 Q 100 50 138 95 Q 148 75 130 60 Q 100 45 70 60 Q 52 75 62 95 Z" fill="#DC2626" />
                <path d="M 68 85 Q 100 55 132 85 Q 140 72 125 58 Q 100 48 75 58 Q 60 72 68 85 Z" fill="#F97316" />
                <path d="M 74 75 Q 100 58 126 75 Z" fill="#FBBF24" />

                {/* Facial Features */}
                <path d="M 80 122 Q 100 132 120 122 Q 115 116 100 120 Q 85 116 80 122 Z" fill="#1E293B" />
                <ellipse cx="86" cy="104" rx="4.5" ry="3.5" fill="#0F172A" />
                <ellipse cx="114" cy="104" rx="4.5" ry="3.5" fill="#0F172A" />
                <circle cx="87.5" cy="103" r="1.5" fill="#FFFFFF" />
                <circle cx="115.5" cy="103" r="1.5" fill="#FFFFFF" />
                <circle cx="100" cy="94" r="3" fill="#DC2626" />
              </svg>
            </div>
          </motion.div>
        </div>

        {/* Subtle Live Badge on Landscape */}
        <div className="absolute top-4 left-4 sm:left-6 z-30">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 backdrop-blur-md text-emerald-300 border border-emerald-500/30 text-xs font-semibold shadow-md">
            <Sprout className="w-3.5 h-3.5 text-emerald-400" />
            <span>{language === 'hi' ? 'ग्रामीण एवं सूक्ष्म उद्यम' : 'Micro & Rural Enterprise'}</span>
          </div>
        </div>

        {/* Bottom Horizon Gradient */}
        <div className="absolute bottom-0 inset-x-0 h-16 bg-gradient-to-t from-emerald-950 via-emerald-950/60 to-transparent pointer-events-none z-15" />
      </div>

      {/* 2. DEDICATED METRICS & RECOGNITION SHOWCASE ROW (NO OVERLAPPING / CLEAN SPACING) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 z-30 relative">
        
        {/* Showcase Card 1: MUDRA Tarun Scheme */}
        <motion.div
          whileHover={{ y: -3, scale: 1.01 }}
          transition={{ duration: 0.2 }}
          onClick={() => setActiveCard(activeCard === 'mudra' ? null : 'mudra')}
          className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all cursor-pointer flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-100 flex items-center justify-center font-extrabold text-sm shrink-0 shadow-xs">
            ₹10L
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span className="truncate">{language === 'hi' ? 'मुद्रा तरुण ऋण' : 'MUDRA Tarun Loan'}</span>
            </div>
            <div className="text-[11px] font-medium text-slate-500 mt-0.5 truncate">
              {language === 'hi' ? '0% गारंटी शुल्क • तुरंत मंजूरी' : '0% Collateral • Fast Disbursal'}
            </div>
          </div>
        </motion.div>

        {/* Showcase Card 2: High Market Demand */}
        <motion.div
          whileHover={{ y: -3, scale: 1.01 }}
          transition={{ duration: 0.2 }}
          onClick={() => setActiveCard(activeCard === 'demand' ? null : 'demand')}
          className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300 transition-all cursor-pointer flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-700 border border-blue-100 flex items-center justify-center shrink-0 shadow-xs">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
              <span className="truncate">{language === 'hi' ? 'उच्च स्थानीय मांग' : 'Strong Local Demand'}</span>
              <span className="bg-blue-100 text-blue-800 text-[10px] px-1.5 py-0.5 rounded-full font-extrabold shrink-0">92%</span>
            </div>
            <div className="text-[11px] font-medium text-slate-500 mt-0.5 truncate">
              {language === 'hi' ? 'उत्तर प्रदेश व बिहार क्लस्टर' : 'Top Tier District Cluster'}
            </div>
          </div>
        </motion.div>

        {/* Showcase Card 3: Instant DPR Generator */}
        <motion.div
          whileHover={{ y: -3, scale: 1.01 }}
          transition={{ duration: 0.2 }}
          onClick={() => setActiveCard(activeCard === 'dpr' ? null : 'dpr')}
          className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-purple-300 transition-all cursor-pointer flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-xl bg-purple-50 text-purple-700 border border-purple-100 flex items-center justify-center shrink-0 shadow-xs">
            <FileCheck2 className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
              <Sparkles className="w-3.5 h-3.5 text-purple-600 shrink-0" />
              <span className="truncate">{language === 'hi' ? '60-सेकंड बैंक DPR' : '60-Sec Bank DPR'}</span>
            </div>
            <div className="text-[11px] font-medium text-slate-500 mt-0.5 truncate">
              {language === 'hi' ? '13-अनुभाग विस्तृत परियोजना रिपोर्ट' : '13-Section Canonical PDF'}
            </div>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
