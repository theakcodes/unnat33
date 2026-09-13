'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Landmark,
  BadgeIndianRupee,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  MapPin,
  Layers,
  ArrowUpRight,
  Database,
  Building2,
} from 'lucide-react';

export default function BusinessIntelligenceMap() {
  const [selectedCluster, setSelectedCluster] = useState('varanasi');

  const clusters = {
    varanasi: {
      name: 'Varanasi District Cluster',
      state: 'Uttar Pradesh',
      trade: 'Handloom, Zari & Apparel',
      demandScore: 92,
      demandLabel: 'Strong Regional Absorption',
      msmesInRadius: '1,240 Micro Units',
      financingOption: 'MUDRA Tarun (₹10L)',
      statutorySubsidies: 'PMEGP 35% Capital Margin',
      dprStatus: '13-Section DPR Ready',
      growthYoY: '+18.4%',
    },
    pune: {
      name: 'Pune Industrial Cluster',
      state: 'Maharashtra',
      trade: 'Light Engineering & Fabrication',
      demandScore: 89,
      demandLabel: 'High Supply Chain Demand',
      msmesInRadius: '3,850 Units',
      financingOption: 'CGTMSE Credit Guarantee',
      statutorySubsidies: 'State Industrial Incentive',
      dprStatus: '13-Section DPR Ready',
      growthYoY: '+16.2%',
    },
    jaipur: {
      name: 'Jaipur Craft Corridor',
      state: 'Rajasthan',
      trade: 'Textile Printing & Artisan Works',
      demandScore: 86,
      demandLabel: 'Export & Domestic Catchment',
      msmesInRadius: '2,110 Units',
      financingOption: 'PM Vishwakarma Scheme',
      statutorySubsidies: 'Artisan Concessionary Loan',
      dprStatus: '13-Section DPR Ready',
      growthYoY: '+14.8%',
    },
  };

  const active = clusters[selectedCluster as keyof typeof clusters] || clusters.varanasi;

  return (
    <div className="w-full bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden select-none">
      {/* 1. Interface Header Bar */}
      <div className="bg-slate-50/80 border-b border-slate-200 px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#159A68] animate-pulse" />
          <span className="text-xs font-bold text-[#0B1736] tracking-tight">
            Hyper-Local Market Intelligence Engine
          </span>
          <span className="hidden sm:inline text-xs text-slate-400">•</span>
          <span className="hidden sm:inline text-xs font-medium text-slate-500">
            785 Districts Synchronized
          </span>
        </div>

        {/* Cluster Tabs */}
        <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setSelectedCluster('varanasi')}
            className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              selectedCluster === 'varanasi'
                ? 'bg-[#0B1736] text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Varanasi
          </button>
          <button
            type="button"
            onClick={() => setSelectedCluster('pune')}
            className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              selectedCluster === 'pune'
                ? 'bg-[#0B1736] text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Pune
          </button>
          <button
            type="button"
            onClick={() => setSelectedCluster('jaipur')}
            className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              selectedCluster === 'jaipur'
                ? 'bg-[#0B1736] text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Jaipur
          </button>
        </div>
      </div>

      {/* 2. Visual Intelligence Map & Data Canvas */}
      <div className="p-4 sm:p-6 lg:p-7 relative bg-[#FBFBFA] min-h-[380px] sm:min-h-[420px] flex flex-col justify-between">
        
        {/* Subtle Geometric Node Matrix Lines (SVG Canvas) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-40" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="dotMatrix" width="24" height="24" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" fill="#CBD5E1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dotMatrix)" />
          {/* Subtle network lines connecting nodes */}
          <path d="M 120 180 Q 280 120 480 200 T 820 150" fill="none" stroke="#CBD5E1" strokeWidth="1.2" strokeDasharray="4 4" />
          <path d="M 180 320 Q 420 280 620 340 T 920 260" fill="none" stroke="#CBD5E1" strokeWidth="1.2" strokeDasharray="4 4" />
        </svg>

        {/* Top Node Markers Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 relative z-10 mb-4">
          
          {/* Signal Indicator 1: Demand Absorption */}
          <div className="bg-white/95 backdrop-blur-xs p-3.5 rounded-xl border border-slate-200/90 shadow-xs flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#EAF6F0] text-[#159A68] flex items-center justify-center shrink-0">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <span>Local Demand Index</span>
              </div>
              <div className="text-sm font-black text-[#0B1736] truncate">
                {active.demandScore}/100 • {active.demandLabel}
              </div>
            </div>
          </div>

          {/* Signal Indicator 2: Pre-Screened Capital Stack */}
          <div className="bg-white/95 backdrop-blur-xs p-3.5 rounded-xl border border-slate-200/90 shadow-xs flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center shrink-0">
              <BadgeIndianRupee className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <span>Recommended Credit</span>
              </div>
              <div className="text-sm font-black text-[#0B1736] truncate">
                {active.financingOption}
              </div>
            </div>
          </div>

          {/* Signal Indicator 3: Statutory Subsidy Gate */}
          <div className="bg-white/95 backdrop-blur-xs p-3.5 rounded-xl border border-slate-200/90 shadow-xs flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-50 text-[#F4A340] flex items-center justify-center shrink-0">
              <Landmark className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <span>Statutory Scheme</span>
              </div>
              <div className="text-sm font-black text-[#0B1736] truncate">
                {active.statutorySubsidies}
              </div>
            </div>
          </div>

        </div>

        {/* Central Elevated Business Intelligence Card */}
        <div className="relative z-10 bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6 my-auto max-w-2xl mx-auto w-full">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#159A68]" />
                <span className="text-xs font-bold text-[#159A68] uppercase tracking-wider">
                  Target Cluster Focus
                </span>
              </div>
              <h3 className="text-lg font-black text-[#0B1736] mt-0.5">
                {active.name}
              </h3>
              <p className="text-xs text-slate-500 font-medium">
                {active.trade} • {active.state}
              </p>
            </div>

            <div className="flex sm:flex-col items-center sm:items-end justify-between gap-1 shrink-0">
              <span className="text-xs font-semibold text-slate-500">Projected Growth</span>
              <span className="text-sm font-black text-[#159A68] bg-[#EAF6F0] px-2 py-0.5 rounded-md border border-[#159A68]/20">
                {active.growthYoY} YoY
              </span>
            </div>
          </div>

          {/* Cluster Analytical Breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Enterprise Density</span>
              <span className="text-xs font-extrabold text-[#0B1736] mt-0.5 block">{active.msmesInRadius}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Statutory Gate</span>
              <span className="text-xs font-extrabold text-[#159A68] mt-0.5 block">Eligible (Pre-Check)</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Bank Documentation</span>
              <span className="text-xs font-extrabold text-[#0B1736] mt-0.5 block">{active.dprStatus}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Advisory Level</span>
              <span className="text-xs font-extrabold text-[#0B1736] mt-0.5 block">Level 1 Complete</span>
            </div>
          </div>
        </div>

        {/* Bottom Trust & Data Provenance Bar */}
        <div className="relative z-10 pt-4 mt-4 border-t border-slate-200/70 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 font-medium gap-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-[#159A68]" />
            <span>Deterministic Rule Engine • Official Udyam & District Census Baseline</span>
          </div>
          <div className="flex items-center gap-3">
            <span>PMEGP • MUDRA • PM Vishwakarma • CGTMSE</span>
          </div>
        </div>

      </div>
    </div>
  );
}
