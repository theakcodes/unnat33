'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

export default function BusinessEcosystemBackground() {
  const prefersReduced = useReducedMotion();
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isDesktop, setIsDesktop] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkDesktop = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    checkDesktop();
    window.addEventListener('resize', checkDesktop);
    return () => window.removeEventListener('resize', checkDesktop);
  }, []);

  useEffect(() => {
    if (!isDesktop || prefersReduced) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [isDesktop, prefersReduced]);

  // Subtle parallax coefficients
  const p1 = isDesktop && !prefersReduced ? { x: mousePos.x * 6, y: mousePos.y * 4 } : { x: 0, y: 0 };
  const p2 = isDesktop && !prefersReduced ? { x: mousePos.x * 14, y: mousePos.y * 8 } : { x: 0, y: 0 };
  const p3 = isDesktop && !prefersReduced ? { x: mousePos.x * 20, y: mousePos.y * 12 } : { x: 0, y: 0 };

  return (
    <div
      ref={containerRef}
      className="absolute inset-x-0 top-0 h-[580px] sm:h-[620px] pointer-events-none overflow-hidden select-none"
      aria-hidden="true"
    >
      {/* ========================================================================= */}
      {/* LAYER 1: BASE AMBIENT GLOWS & READABILITY SHIELD */}
      {/* ========================================================================= */}
      {/* Soft Saffron Glow (Top Right) */}
      <motion.div
        animate={
          prefersReduced
            ? {}
            : {
                scale: [1, 1.06, 1],
                opacity: [0.35, 0.5, 0.35],
              }
        }
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -top-24 -right-20 w-[520px] h-[520px] rounded-full bg-gradient-to-br from-[#F4A340]/25 via-[#F8EEDC]/40 to-transparent blur-3xl pointer-events-none"
      />

      {/* Soft Forest Green Glow (Mid Left) */}
      <motion.div
        animate={
          prefersReduced
            ? {}
            : {
                scale: [1, 1.05, 1],
                opacity: [0.28, 0.42, 0.28],
              }
        }
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
        className="absolute top-16 -left-24 w-[480px] h-[480px] rounded-full bg-gradient-to-tr from-[#159A68]/22 via-[#EAF6F0]/35 to-transparent blur-3xl pointer-events-none"
      />

      {/* Center Readability Shield: Radial cream/white gradient ensures 100% headline legibility */}
      <div className="absolute inset-0 [background:radial-gradient(ellipse_at_center,_rgba(247,248,245,0.95)_0%,_rgba(255,255,255,0.8)_45%,_transparent_75%)] pointer-events-none" />

      {/* ========================================================================= */}
      {/* LAYER 2: UNDULATING LANDSCAPE RIBBONS (FLOWING CURVES AT BOTTOM OF HERO) */}
      {/* Weaves gently beneath the CTA buttons, meeting the top of the map card */}
      {/* ========================================================================= */}
      <div
        className="absolute inset-x-0 bottom-0 h-48 sm:h-56 pointer-events-none overflow-hidden"
        style={{ transform: `translate3d(${p1.x}px, ${p1.y}px, 0)` }}
      >
        {/* Rolling Background Hill Tone */}
        <div className="absolute inset-x-0 bottom-0 h-40 opacity-40">
          <svg className="w-full h-full" viewBox="0 0 1600 160" fill="none" preserveAspectRatio="none">
            <path
              d="M0,60 C 350,15 720,95 1100,40 C 1350,5 1500,50 1600,35 L 1600,160 L 0,160 Z"
              fill="#EBF3EE"
            />
          </svg>
        </div>

        {/* Ribbon 1: Warm Saffron Growth Ribbon */}
        <motion.div
          animate={prefersReduced ? {} : { x: ['0%', '-4%', '0%'] }}
          transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute inset-x-0 bottom-8 h-32 sm:h-40 w-[115%] -left-[7%]"
        >
          <svg
            className="w-full h-full opacity-65"
            viewBox="0 0 1600 160"
            fill="none"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="saffronWaveGradFinal" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#F4A340" stopOpacity="0.35" />
                <stop offset="30%" stopColor="#F8D39E" stopOpacity="0.8" />
                <stop offset="60%" stopColor="#F4A340" stopOpacity="0.85" />
                <stop offset="85%" stopColor="#F8D39E" stopOpacity="0.65" />
                <stop offset="100%" stopColor="#F4A340" stopOpacity="0.35" />
              </linearGradient>
            </defs>
            <path
              d="M-50,60 C 260,10 540,110 900,55 C 1180,15 1420,85 1650,50 L 1650,95 C 1420,130 1180,65 900,105 C 540,155 260,50 -50,105 Z"
              fill="url(#saffronWaveGradFinal)"
            />
          </svg>
        </motion.div>

        {/* Ribbon 2: Forest Green Regional Connectivity Ribbon */}
        <motion.div
          animate={prefersReduced ? {} : { x: ['0%', '3.5%', '0%'] }}
          transition={{ duration: 28, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
          className="absolute inset-x-0 bottom-2 h-36 sm:h-44 w-[115%] -left-[7%]"
        >
          <svg
            className="w-full h-full opacity-60"
            viewBox="0 0 1600 160"
            fill="none"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="greenWaveGradFinal" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#159A68" stopOpacity="0.25" />
                <stop offset="35%" stopColor="#96D9C1" stopOpacity="0.7" />
                <stop offset="70%" stopColor="#159A68" stopOpacity="0.65" />
                <stop offset="100%" stopColor="#EAF6F0" stopOpacity="0.25" />
              </linearGradient>
            </defs>
            <path
              d="M-50,95 C 290,135 620,70 980,110 C 1260,140 1450,80 1650,95 L 1650,130 C 1450,115 1260,175 980,145 C 620,105 290,170 -50,135 Z"
              fill="url(#greenWaveGradFinal)"
            />
          </svg>
        </motion.div>
      </div>

      {/* ========================================================================= */}
      {/* LAYER 3: CONSTELLATION NETWORK CONNECTING ARCH & NODES */}
      {/* Calibrated to arch high above the headline text (behind SIH badge) */}
      {/* ========================================================================= */}
      <div
        className="absolute inset-0 pointer-events-none hidden lg:block"
        style={{ transform: `translate3d(${p2.x}px, ${p2.y}px, 0)` }}
      >
        <svg className="w-full h-full" viewBox="0 0 1440 580" fill="none" preserveAspectRatio="none">
          {/* Constellation Arch: Peak y=50px (behind SIH badge), arches around headline text */}
          <path
            d="M 230,340 C 265,280 295,210 350,130 C 470,30 970,30 1090,130 C 1145,210 1175,280 1210,340"
            stroke="#F4A340"
            strokeWidth="1.8"
            strokeDasharray="6 6"
            opacity="0.6"
          />
        </svg>

        {/* Node 1: Left Growth Chart Icon Node (to left of paragraph) */}
        <motion.div
          animate={prefersReduced ? {} : { y: [-3, 3, -3], opacity: [0.85, 1, 0.85] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute left-[20%] top-[270px] -translate-x-1/2 -translate-y-1/2"
        >
          <div className="w-8 h-8 rounded-full bg-[#FEF8F0] shadow-xs border border-amber-300/90 flex items-center justify-center text-amber-600">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
              <polyline points="17 6 23 6 23 12" />
            </svg>
          </div>
        </motion.div>

        {/* Node 2: Sage Green Sprout Node (Above Left Shoulder of Headline) */}
        <motion.div
          animate={prefersReduced ? {} : { y: [3, -3, 3], opacity: [0.9, 1, 0.9] }}
          transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 0.8 }}
          className="absolute left-[24%] top-[115px] -translate-x-1/2 -translate-y-1/2"
        >
          <div className="w-12 h-12 rounded-full bg-[#F4F9F6] shadow-xs border border-emerald-300/90 flex items-center justify-center text-[#159A68]">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 20h10" />
              <path d="M10 20c0-4 2-7 2-11" />
              <path d="M12 9c2-2 5-3 8-3-1 3-2 6-5 8" />
              <path d="M12 12c-2-2-5-2-7-2 1 3 2 5 4 7" />
            </svg>
          </div>
        </motion.div>

        {/* Node 3: Government / Bank Statutory Pillar Node (Above Right Shoulder of Headline) */}
        <motion.div
          animate={prefersReduced ? {} : { y: [-4, 4, -4], opacity: [0.9, 1, 0.9] }}
          transition={{ duration: 7.5, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
          className="absolute right-[24%] top-[115px] translate-x-1/2 -translate-y-1/2"
        >
          <div className="w-12 h-12 rounded-full bg-[#F4F9F6] shadow-xs border border-emerald-300/90 flex items-center justify-center text-[#159A68]">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="21" x2="21" y2="21" />
              <line x1="6" y1="18" x2="6" y2="10" />
              <line x1="10" y1="18" x2="10" y2="10" />
              <line x1="14" y1="18" x2="14" y2="10" />
              <line x1="18" y1="18" x2="18" y2="10" />
              <polygon points="12 2 20 7 4 7" />
            </svg>
          </div>
        </motion.div>

        {/* Node 4: Saffron Rupee Currency Node (to right of paragraph) */}
        <motion.div
          animate={prefersReduced ? {} : { y: [4, -4, 4], opacity: [0.85, 1, 0.85] }}
          transition={{ duration: 6.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
          className="absolute right-[20%] top-[265px] translate-x-1/2 -translate-y-1/2"
        >
          <div className="w-10 h-10 rounded-full bg-[#FEF8F0] shadow-xs border border-amber-300/90 flex items-center justify-center text-[#F4A340] font-bold text-base">
            ₹
          </div>
        </motion.div>
      </div>

      {/* ========================================================================= */}
      {/* LAYER 4: LEFT SIDE — INDIAN MICRO-BUSINESS & LOCAL COMMERCE */}
      {/* Detailed Kirana stall, banyan foliage, shopkeeper & customer */}
      {/* ========================================================================= */}
      <div
        className="absolute top-2 left-0 w-64 sm:w-80 md:w-96 lg:w-[410px] h-[540px] pointer-events-none"
        style={{ transform: `translate3d(${p2.x}px, ${p2.y}px, 0)` }}
      >
        {/* Devanagari Micro-Typography */}
        <div className="absolute top-10 left-8 sm:left-12 text-left opacity-50">
          <span className="block text-[14px] font-medium tracking-wider text-[#0B1736] font-serif leading-tight">
            स्थानीय
          </span>
          <span className="block text-[14px] font-medium tracking-wider text-[#0B1736] font-serif leading-tight">
            व्यापार
          </span>
          <span className="block text-[10px] font-bold text-[#159A68] tracking-widest uppercase mt-0.5">
            उन्नत भारत
          </span>
        </div>

        {/* Editorial Vector Illustration */}
        <svg
          className="w-full h-full text-[#0B1736]"
          viewBox="0 0 380 500"
          fill="none"
          stroke="currentColor"
        >
          <defs>
            <radialGradient id="canopyFill" cx="30%" cy="30%" r="70%">
              <stop offset="0%" stopColor="#7EBA9B" stopOpacity="0.5" />
              <stop offset="50%" stopColor="#418361" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#1E5238" stopOpacity="0.15" />
            </radialGradient>
            <linearGradient id="roofFill" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#E9C18B" stopOpacity="0.55" />
              <stop offset="100%" stopColor="#C49156" stopOpacity="0.3" />
            </linearGradient>
            <linearGradient id="counterFill" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#F5E8D6" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#E6CFB0" stopOpacity="0.5" />
            </linearGradient>
          </defs>

          {/* Lush Tree Foliage Behind Kirana Stall */}
          <g opacity="0.7">
            {/* Canopy Lobes */}
            <path
              d="M -20 230 C -25 150 -5 70 50 40 C 100 10 160 30 155 85 C 195 95 210 160 175 210 C 145 250 65 255 -20 230 Z"
              fill="url(#canopyFill)"
              stroke="#159A68"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <path
              d="M 30 75 C 55 40 110 35 140 65 C 165 90 150 130 120 135 C 80 140 50 115 30 75 Z"
              fill="#98CEA9"
              fillOpacity="0.3"
              stroke="#159A68"
              strokeWidth="1"
            />
            {/* Branches */}
            <path d="M 25 190 Q 55 130 95 110" stroke="#5D4037" strokeWidth="1.6" opacity="0.55" />
            <path d="M 65 125 Q 85 95 120 90" stroke="#5D4037" strokeWidth="1.2" opacity="0.45" />
          </g>

          {/* Kirana Thatched Canopy / Slanted Awning */}
          <g opacity="0.75">
            <polygon
              points="10,190 150,160 182,200 20,230"
              fill="url(#roofFill)"
              stroke="#4E342E"
              strokeWidth="1.5"
            />
            {/* Thatch line ridges */}
            <line x1="42" y1="225" x2="32" y2="185" stroke="#4E342E" strokeWidth="1.1" opacity="0.6" />
            <line x1="72" y1="219" x2="62" y2="179" stroke="#4E342E" strokeWidth="1.1" opacity="0.6" />
            <line x1="102" y1="213" x2="92" y2="173" stroke="#4E342E" strokeWidth="1.1" opacity="0.6" />
            <line x1="132" y1="207" x2="122" y2="167" stroke="#4E342E" strokeWidth="1.1" opacity="0.6" />
            <line x1="162" y1="201" x2="152" y2="161" stroke="#4E342E" strokeWidth="1.1" opacity="0.6" />

            {/* Bamboo Support Poles */}
            <line x1="22" y1="230" x2="22" y2="405" stroke="#4E342E" strokeWidth="1.6" />
            <line x1="178" y1="200" x2="178" y2="395" stroke="#4E342E" strokeWidth="1.6" />
          </g>

          {/* Kirana Store Counter & Inventory */}
          <g opacity="0.7">
            {/* Wooden Counter Desk */}
            <rect
              x="20"
              y="295"
              width="164"
              height="105"
              rx="3"
              fill="url(#counterFill)"
              stroke="#0B1736"
              strokeWidth="1.4"
            />
            <line x1="20" y1="330" x2="184" y2="330" stroke="#0B1736" strokeWidth="1" opacity="0.35" />
            <line x1="20" y1="365" x2="184" y2="365" stroke="#0B1736" strokeWidth="1" opacity="0.35" />

            {/* Glass Jars & Spices on Counter */}
            <rect x="30" y="270" width="14" height="25" rx="2" fill="#F8EEDC" fillOpacity="0.9" stroke="#0B1736" strokeWidth="1.2" />
            <rect x="48" y="267" width="16" height="28" rx="2" fill="#FCE7C8" fillOpacity="0.9" stroke="#0B1736" strokeWidth="1.2" />
            <rect x="68" y="272" width="12" height="23" rx="2" fill="#EAF6F0" fillOpacity="0.9" stroke="#0B1736" strokeWidth="1.2" />

            {/* Clay Pots / Grains Baskets */}
            <ellipse cx="102" cy="286" rx="10" ry="7" fill="#E8B482" fillOpacity="0.85" stroke="#0B1736" strokeWidth="1.2" />
            <ellipse cx="125" cy="285" rx="9" ry="8" fill="#D98A53" fillOpacity="0.75" stroke="#0B1736" strokeWidth="1.2" />
          </g>

          {/* Shopkeeper Figure Silhouette (Behind Counter) */}
          <g opacity="0.6">
            {/* Head */}
            <circle cx="82" cy="222" r="8.5" fill="#D4A373" stroke="#0B1736" strokeWidth="1.3" />
            {/* Kurta Shirt */}
            <path
              d="M 66 295 L 70 242 Q 82 238 94 242 L 98 295 Z"
              fill="#F8FAFC"
              stroke="#0B1736"
              strokeWidth="1.3"
            />
            {/* Hand Gesturing / Weighing */}
            <path d="M 94 252 Q 115 262 130 278" stroke="#0B1736" strokeWidth="1.3" />
          </g>

          {/* Customer Woman Silhouette in Traditional Saree (Front Counter) */}
          <g opacity="0.65">
            {/* Head with Pallu Over Head */}
            <ellipse cx="198" cy="260" rx="7.5" ry="9" fill="#D4A373" stroke="#0B1736" strokeWidth="1.3" />
            {/* Saree Body Drape */}
            <path
              d="M 182 415 L 188 288 Q 198 280 208 288 L 218 415 Z"
              fill="#D97757"
              fillOpacity="0.5"
              stroke="#0B1736"
              strokeWidth="1.3"
            />
            {/* Saffron Pallu Accent Drapery */}
            <path
              d="M 190 284 Q 212 320 214 380"
              stroke="#F4A340"
              strokeWidth="1.8"
              opacity="0.85"
            />
          </g>
        </svg>
      </div>

      {/* ========================================================================= */}
      {/* LAYER 5: RIGHT SIDE — RURAL ENTERPRISE & ARTISAN CRAFT */}
      {/* Farmer in Pagri, Tractor silhouette, Woman potter shaping earthen Matkas */}
      {/* ========================================================================= */}
      <div
        className="absolute top-2 right-0 w-64 sm:w-80 md:w-96 lg:w-[410px] h-[540px] pointer-events-none"
        style={{ transform: `translate3d(${p3.x}px, ${p3.y}px, 0)` }}
      >
        {/* Devanagari Micro-Typography */}
        <div className="absolute top-10 right-8 sm:right-12 text-right opacity-50">
          <span className="block text-[14px] font-medium tracking-wider text-[#0B1736] font-serif leading-tight">
            छोटे
          </span>
          <span className="block text-[14px] font-medium tracking-wider text-[#0B1736] font-serif leading-tight">
            उद्यम
          </span>
          <span className="block text-[10px] font-bold text-[#F4A340] tracking-widest uppercase mt-0.5">
            बड़ी संभावनाएँ
          </span>
        </div>

        {/* Editorial Vector Illustration */}
        <svg
          className="w-full h-full text-[#0B1736]"
          viewBox="0 0 380 500"
          fill="none"
          stroke="currentColor"
        >
          <defs>
            <linearGradient id="potteryMatkaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#F8D39E" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#D97740" stopOpacity="0.65" />
            </linearGradient>
            <linearGradient id="tractorGradFinal" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3E7D5F" stopOpacity="0.45" />
              <stop offset="100%" stopColor="#7EBF9F" stopOpacity="0.3" />
            </linearGradient>
          </defs>

          {/* Distant Birds Gliding in Sky */}
          <g opacity="0.5">
            <path d="M 60 55 Q 72 47 84 55 Q 96 47 108 55" stroke="#0B1736" strokeWidth="1.2" />
            <path d="M 112 72 Q 122 66 132 72 Q 142 66 152 72" stroke="#0B1736" strokeWidth="1" />
            <path d="M 80 90 Q 89 85 98 90 Q 107 85 116 90" stroke="#0B1736" strokeWidth="0.9" />
          </g>

          {/* Farmer with Turban/Pagri in Agri Field */}
          <g opacity="0.6">
            {/* Pagri / Turban in Warm Saffron */}
            <path
              d="M 160 205 Q 168 193 176 205 Q 183 213 174 219 Q 162 219 160 205 Z"
              fill="#F4A340"
              fillOpacity="0.75"
              stroke="#F4A340"
              strokeWidth="1.2"
            />
            {/* Head */}
            <circle cx="168" cy="211" r="6" fill="#D4A373" stroke="#0B1736" strokeWidth="1.2" />
            {/* Farmer Kurta & Dhoti */}
            <path
              d="M 156 300 L 158 228 Q 168 224 178 228 L 180 300 Z"
              fill="#F8FAFC"
              stroke="#0B1736"
              strokeWidth="1.2"
            />
            {/* Staff / Walking Stick */}
            <line x1="184" y1="215" x2="184" y2="310" stroke="#5D4037" strokeWidth="1.3" opacity="0.75" />
          </g>

          {/* Rural Agricultural Tractor Silhouette */}
          <g opacity="0.65">
            {/* Rear Large Wheel */}
            <circle cx="120" cy="280" r="23" fill="#FFFFFF" fillOpacity="0.7" stroke="#0B1736" strokeWidth="1.5" />
            <circle cx="120" cy="280" r="10" stroke="#0B1736" strokeWidth="1.2" />
            {/* Front Small Wheel */}
            <circle cx="60" cy="289" r="14" fill="#FFFFFF" fillOpacity="0.7" stroke="#0B1736" strokeWidth="1.3" />
            <circle cx="60" cy="289" r="6" stroke="#0B1736" strokeWidth="1" />
            {/* Tractor Body & Hood */}
            <path
              d="M 120 256 L 75 256 L 54 278 L 42 278 L 42 264 L 80 246 L 105 246 L 120 228 L 142 228 L 142 270 Z"
              fill="url(#tractorGradFinal)"
              stroke="#159A68"
              strokeWidth="1.3"
            />
            {/* Exhaust Stack & Steering */}
            <line x1="68" y1="246" x2="68" y2="224" stroke="#0B1736" strokeWidth="1.3" />
            <line x1="112" y1="244" x2="118" y2="232" stroke="#0B1736" strokeWidth="1.2" />
          </g>

          {/* Rural Artisan Woman Sitting on Ground & Shaping Earthen Matkas */}
          <g opacity="0.68">
            {/* Head with Saree */}
            <circle cx="264" cy="275" r="7.5" fill="#D4A373" stroke="#0B1736" strokeWidth="1.3" />
            {/* Saree Dress */}
            <path
              d="M 246 415 L 252 294 Q 264 286 274 294 L 286 415 Z"
              fill="#D97757"
              fillOpacity="0.45"
              stroke="#0B1736"
              strokeWidth="1.3"
            />
            {/* Saree Drape Accent */}
            <path d="M 256 298 Q 278 335 274 385" stroke="#F4A340" strokeWidth="1.6" opacity="0.8" />

            {/* Potter's Turntable */}
            <ellipse cx="228" cy="390" rx="20" ry="7" fill="#F8EEDC" fillOpacity="0.85" stroke="#0B1736" strokeWidth="1.3" />
            {/* Wet Clay Pot being shaped */}
            <path
              d="M 218 382 Q 214 354 228 354 Q 242 354 238 382 Z"
              fill="url(#potteryMatkaGrad)"
              stroke="#8D4C28"
              strokeWidth="1.3"
            />
            {/* Artisan's Hands */}
            <path d="M 250 326 Q 238 348 232 364" stroke="#0B1736" strokeWidth="1.3" />

            {/* Completed Earthen Water Pots (Matkas) on Ground */}
            <circle cx="198" cy="382" r="12" fill="url(#potteryMatkaGrad)" stroke="#8D4C28" strokeWidth="1.3" />
            <path d="M 192 370 L 204 370" stroke="#8D4C28" strokeWidth="1.2" />

            <circle cx="176" cy="388" r="9" fill="url(#potteryMatkaGrad)" stroke="#8D4C28" strokeWidth="1.2" />
            <path d="M 172 378 L 180 378" stroke="#8D4C28" strokeWidth="1.1" />

            <circle cx="158" cy="392" r="7" fill="url(#potteryMatkaGrad)" stroke="#8D4C28" strokeWidth="1.1" />
          </g>
        </svg>
      </div>

      {/* ========================================================================= */}
      {/* LAYER 6: FLOATING BOTANICAL LEAF PARTICLES */}
      {/* ========================================================================= */}
      {!prefersReduced && (
        <>
          {/* Leaf 1 (Top Left Drift) */}
          <motion.div
            animate={{
              x: [0, 45, 90],
              y: [0, 35, 80],
              rotate: [0, 50, 100],
              opacity: [0, 0.45, 0],
            }}
            transition={{ duration: 18, repeat: Infinity, ease: 'linear' }}
            className="absolute top-12 left-[23%] text-[#159A68]"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.5 2 2 6.5 2 12c0 3 1.5 6 4 8 2.5-4 5.5-7 10-9 1-3 1-6-4-9z" opacity="0.4" />
            </svg>
          </motion.div>

          {/* Leaf 2 (Upper Right Gentle Drift) */}
          <motion.div
            animate={{
              x: [0, -35, -70],
              y: [0, 45, 95],
              rotate: [20, -25, 30],
              opacity: [0, 0.4, 0],
            }}
            transition={{ duration: 22, repeat: Infinity, ease: 'linear', delay: 4 }}
            className="absolute top-16 right-[23%] text-[#159A68]"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.5 2 2 6.5 2 12c0 3 1.5 6 4 8 2.5-4 5.5-7 10-9 1-3 1-6-4-9z" opacity="0.35" />
            </svg>
          </motion.div>

          {/* Leaf 3 (Center Bottom Soft Saffron Accent) */}
          <motion.div
            animate={{
              x: [0, 30, 60],
              y: [0, -20, -45],
              rotate: [0, 70, 140],
              opacity: [0, 0.35, 0],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear', delay: 8 }}
            className="absolute bottom-28 left-[36%] text-[#F4A340]"
          >
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.5 2 2 6.5 2 12c0 3 1.5 6 4 8 2.5-4 5.5-7 10-9 1-3 1-6-4-9z" opacity="0.4" />
            </svg>
          </motion.div>
        </>
      )}
    </div>
  );
}
