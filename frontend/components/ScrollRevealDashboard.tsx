'use client';

import React, { useRef, useState } from 'react';
import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  TrendingUp,
  Landmark,
  BadgeIndianRupee,
  ShieldCheck,
  Plus,
  MapPin,
  ArrowRight,
  Sun,
  LayoutDashboard,
  User,
  PieChart,
  FileSpreadsheet,
  FileText,
  Bot,
  HelpCircle,
  ChevronDown,
  Sparkles,
  BarChart3,
  CheckCircle2,
  Zap,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart as RePieChart,
  Pie,
  Cell,
  CartesianGrid,
} from 'recharts';

export default function ScrollRevealDashboard() {
  const { t, language } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedState, setSelectedState] = useState('Uttar Pradesh');
  const [activeTab, setActiveTab] = useState('market');

  // Scroll driven 3D perspective animation matching Framer app mockup
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'start start'],
  });

  const rotateX = useTransform(scrollYProgress, [0, 1], [18, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [0.88, 1]);
  const opacity = useTransform(scrollYProgress, [0, 0.4], [0.4, 1]);
  const translateY = useTransform(scrollYProgress, [0, 1], [60, 0]);

  // Chart Data for Business Growth Projection
  const growthData = [
    { year: t('dashboardMock.year1'), revenue: 10.2 },
    { year: t('dashboardMock.year2'), revenue: 18.4 },
    { year: t('dashboardMock.year3'), revenue: 35.0 },
  ];

  // Chart Data for Funding Sources Donut Chart
  const fundingSourcesData = [
    { name: language === 'hi' ? 'सरकारी योजनाएं' : 'Government Schemes', value: 45, color: '#059669' },
    { name: language === 'hi' ? 'बैंक ऋण' : 'Bank Loans', value: 30, color: '#2563eb' },
    { name: language === 'hi' ? 'सब्सिडी' : 'Subsidies', value: 15, color: '#eab308' },
    { name: language === 'hi' ? 'स्व-निवेश' : 'Self Investment', value: 10, color: '#9333ea' },
  ];

  return (
    <div ref={containerRef} className="py-12 md:py-24 relative overflow-hidden bg-slate-900/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-extrabold mb-4 shadow-sm border border-emerald-200">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
            <span>Interactive Advisory Dashboard Reveal</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-black text-slate-900 tracking-tight">
            {language === 'hi' ? 'स्मार्ट बिज़नेस डैशबोर्ड का अनुभव करें' : 'Experience the Smart Advisory Dashboard'}
          </h2>
          <p className="text-sm md:text-base text-slate-600 mt-3 leading-relaxed font-normal">
            {language === 'hi'
              ? 'स्थान, योजना पात्रता, ऋण संरचना और बाजार संभावना का एक एकीकृत दृश्य।'
              : 'Unified real-time visibility into local market demand, scheme matching, EMI structuring, and instant DPR creation.'}
          </p>
        </div>

        {/* 3D Perspective Card Reveal Container */}
        <div style={{ perspective: 1200 }} className="w-full">
          <motion.div
            style={{
              rotateX,
              scale,
              opacity,
              y: translateY,
            }}
            className="w-full bg-white rounded-3xl border border-slate-200/90 shadow-2xl shadow-slate-900/10 overflow-hidden transform-gpu"
          >
            {/* Mockup Top Window Bar */}
            <div className="bg-slate-100/90 px-6 py-3 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-rose-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="ml-2 text-xs font-semibold text-slate-500 hidden sm:inline">
                  https://unnate.gov.in/dashboard
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs font-bold text-slate-600">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span>Live AI Advisory Stream</span>
              </div>
            </div>

            {/* Dashboard Inner App Layout */}
            <div className="flex min-h-[640px]">
              
              {/* Left Sidebar Mockup matching Image 2 */}
              <div className="hidden lg:flex w-64 bg-slate-50/80 border-r border-slate-200/80 p-5 flex-col justify-between shrink-0">
                <div className="space-y-6">
                  {/* Brand Logo in Mockup */}
                  <div className="flex items-center gap-2.5 px-2">
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-700 to-green-500 flex items-center justify-center text-white shadow-md">
                      <TrendingUp className="w-4 h-4" />
                    </div>
                    <span className="text-base font-extrabold text-slate-900">Unnat<span className="text-emerald-600">E</span></span>
                  </div>

                  {/* Sidebar Navigation Items */}
                  <nav className="space-y-1">
                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-emerald-100/80 text-emerald-800 font-bold text-xs shadow-sm">
                      <LayoutDashboard className="w-4 h-4 text-emerald-700" />
                      <span>{t('nav.dashboard')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <User className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.businessProfile')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <BarChart3 className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.marketAnalysis')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <Landmark className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.governmentSchemes')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <BadgeIndianRupee className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.financialOptions')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <FileSpreadsheet className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.dprBuilder')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <FileText className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.insightsReports')}</span>
                    </div>

                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors">
                      <Bot className="w-4 h-4 text-slate-400" />
                      <span>{t('nav.aiAdvisor')}</span>
                    </div>
                  </nav>
                </div>

                {/* Need Guidance Box */}
                <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-50 to-emerald-50 border border-amber-200/60 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-900">
                    <HelpCircle className="w-4 h-4 text-amber-600" />
                    <span>{t('dashboard.needGuidance')}</span>
                  </div>
                  <p className="text-[11px] text-amber-800 leading-snug">
                    {t('dashboard.askAdvisor')}
                  </p>
                </div>
              </div>

              {/* Main Content View matching Image 2 */}
              <div className="flex-1 p-6 md:p-8 space-y-6 bg-slate-50/40">
                
                {/* Greeting & Header Bar */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
                      <span>{t('dashboard.greeting')}</span>
                      <Sun className="w-6 h-6 text-amber-500 fill-amber-400" />
                    </h1>
                    <p className="text-xs font-medium text-slate-500 mt-0.5">
                      {t('dashboard.snapshot')}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    {/* Location Dropdown */}
                    <div className="relative">
                      <button className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 shadow-sm hover:border-emerald-300">
                        <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                        <span>{selectedState}</span>
                        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                      </button>
                    </div>

                    {/* Start New Analysis Button */}
                    <Link
                      href="/dashboard"
                      className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md transition-all shrink-0"
                    >
                      <span>{t('dashboard.startNewAnalysis')}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>

                {/* 4 Metric Cards matching Image 2 */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  
                  {/* Card 1: Market Demand */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-sm space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                        <TrendingUp className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">
                        {t('dashboardMock.high')}
                      </span>
                    </div>
                    <div>
                      <span className="text-xs font-medium text-slate-500">{t('dashboard.marketDemand')}</span>
                      <div className="text-xl font-black text-slate-900 mt-0.5">{t('dashboardMock.strong')}</div>
                    </div>
                    <p className="text-[11px] text-slate-400">{t('dashboardMock.growingDemand')}</p>
                  </div>

                  {/* Card 2: Relevant Schemes */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-sm space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="w-9 h-9 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center">
                        <Landmark className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-extrabold">
                        5+
                      </span>
                    </div>
                    <div>
                      <span className="text-xs font-medium text-slate-500">{t('dashboard.relevantSchemes')}</span>
                      <div className="text-xl font-black text-slate-900 mt-0.5">{t('dashboardMock.available')}</div>
                    </div>
                    <p className="text-[11px] text-slate-400">{t('dashboardMock.centralState')}</p>
                  </div>

                  {/* Card 3: Estimated Funding */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-sm space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
                        <BadgeIndianRupee className="w-5 h-5" />
                      </div>
                    </div>
                    <div>
                      <span className="text-xs font-medium text-slate-500">{t('dashboard.estimatedFunding')}</span>
                      <div className="text-xl font-black text-slate-900 mt-0.5">₹12.5 Lakh+</div>
                    </div>
                    <p className="text-[11px] text-slate-400">{t('dashboardMock.financialSupport')}</p>
                  </div>

                  {/* Card 4: Business Readiness with Circular Progress Ring */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-sm flex items-center justify-between gap-3">
                    <div className="space-y-2 flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center shrink-0">
                          <ShieldCheck className="w-4 h-4" />
                        </div>
                        <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 text-[10px] font-extrabold">
                          78%
                        </span>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-slate-500 truncate block">{t('dashboard.businessReadiness')}</span>
                        <div className="text-xl font-black text-slate-900 mt-0.5">78 / 100</div>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate">{t('dashboardMock.goodPotential')}</p>
                    </div>

                    {/* Circular Progress Ring */}
                    <div className="relative w-16 h-16 shrink-0 flex items-center justify-center">
                      <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 48 48">
                        <circle
                          cx="24"
                          cy="24"
                          r="19"
                          className="text-slate-100"
                          strokeWidth="4"
                          stroke="currentColor"
                          fill="transparent"
                        />
                        <circle
                          cx="24"
                          cy="24"
                          r="19"
                          className="text-purple-600"
                          strokeWidth="4"
                          strokeDasharray={119.38}
                          strokeDashoffset={119.38 * (1 - 0.78)}
                          strokeLinecap="round"
                          stroke="currentColor"
                          fill="transparent"
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        <span className="text-xs font-black text-slate-900 leading-none">78%</span>
                        <span className="text-[8px] font-bold text-slate-400 uppercase mt-0.5">Score</span>
                      </div>
                    </div>
                  </div>

                </div>

                {/* 2 Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Chart 1: Business Growth Projection (Area Chart with Gradient) */}
                  <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-sm font-bold text-slate-900">{t('dashboard.growthProjection')}</h3>
                          <p className="text-[11px] text-slate-400">{t('dashboardMock.estimatedRevenue')}</p>
                        </div>
                        <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-extrabold">
                          {t('dashboardMock.years')}
                        </span>
                      </div>

                      <div className="h-56 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={growthData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                            <defs>
                              <linearGradient id="growthAreaFill" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#059669" stopOpacity={0.25} />
                                <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="year" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={{ stroke: '#e2e8f0' }} />
                            <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${v}L`} tickLine={false} axisLine={false} />
                            <Tooltip
                              formatter={(v: any) => [`₹${v} Lakh`, 'Projected Revenue']}
                              contentStyle={{ backgroundColor: '#ffffff', borderRadius: '0.75rem', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)', fontSize: '12px', fontWeight: 'bold' }}
                            />
                            <Area
                              type="monotone"
                              dataKey="revenue"
                              stroke="#059669"
                              strokeWidth={3}
                              fillOpacity={1}
                              fill="url(#growthAreaFill)"
                              dot={{ r: 4, fill: '#059669', stroke: '#ffffff', strokeWidth: 2 }}
                              activeDot={{ r: 6, fill: '#059669', stroke: '#ffffff', strokeWidth: 2 }}
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* Chart 2: Funding Sources (Donut Chart with Structured Legend) */}
                  <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold text-slate-900">{t('dashboard.fundingSources')}</h3>
                        <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-100">
                          Recommended
                        </span>
                      </div>

                      <div className="h-44 w-full relative flex items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                          <RePieChart>
                            <Pie
                              data={fundingSourcesData}
                              cx="50%"
                              cy="50%"
                              innerRadius={50}
                              outerRadius={70}
                              paddingAngle={4}
                              dataKey="value"
                            >
                              {fundingSourcesData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} stroke="#ffffff" strokeWidth={2} />
                              ))}
                            </Pie>
                            <Tooltip formatter={(v: any) => [`${v}%`, 'Share']} />
                          </RePieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                          <span className="text-xs font-black text-slate-900">₹58.4L</span>
                          <span className="text-[10px] text-slate-400 font-semibold">{t('dashboardMock.potential')}</span>
                        </div>
                      </div>

                      {/* Donut Legend */}
                      <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-100">
                        {fundingSourcesData.map((item, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-[11px]">
                            <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                            <span className="text-slate-600 font-medium truncate">{item.name}</span>
                            <span className="font-extrabold text-slate-900 ml-auto bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200 text-[10px]">{item.value}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                </div>

              </div>
            </div>

          </motion.div>
        </div>

        {/* Animated Tabs Section revealing features as user scrolls */}
        <div id="analysis" className="mt-20 space-y-8">
          <div className="text-center max-w-2xl mx-auto">
            <h3 className="text-2xl font-extrabold text-slate-900">
              {language === 'hi' ? 'विस्तृत सलाहकार मॉड्यूल' : 'Explore Advisory Modules'}
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              {language === 'hi' ? 'अपनी व्यावसायिक आवश्यकता के अनुसार टैब पर क्लिक करें' : 'Click through modules to see hyper-local insights in action'}
            </p>
          </div>

          {/* Interactive Tab Switcher */}
          <div className="flex items-center justify-center gap-2 flex-wrap">
            <button
              onClick={() => setActiveTab('market')}
              className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-sm ${
                activeTab === 'market'
                  ? 'bg-slate-900 text-white shadow-emerald-950/20'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              ⭐ {t('badges.market')}
            </button>

            <button
              onClick={() => setActiveTab('schemes')}
              className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-sm ${
                activeTab === 'schemes'
                  ? 'bg-slate-900 text-white shadow-emerald-950/20'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              ⚡ {t('badges.governmentSchemes')}
            </button>

            <button
              onClick={() => setActiveTab('finance')}
              className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-sm ${
                activeTab === 'finance'
                  ? 'bg-slate-900 text-white shadow-emerald-950/20'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              🛡️ {t('badges.finance')}
            </button>

            <button
              onClick={() => setActiveTab('dpr')}
              className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-sm ${
                activeTab === 'dpr'
                  ? 'bg-slate-900 text-white shadow-emerald-950/20'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              📊 {t('badges.dprBuilder')}
            </button>
          </div>

          {/* Tab Content Display */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200/90 shadow-xl max-w-4xl mx-auto">
            {activeTab === 'market' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                    <TrendingUp className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      {language === 'hi' ? 'हाइपर-लोकल बाजार विश्लेषण' : 'Hyper-Local Market & Enterprise Clustering'}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {language === 'hi' ? '785 भारतीय जिलों से वास्तविक उद्योग घनत्व डाटा' : 'Real-time MSME cluster classification & demand estimation'}
                    </p>
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-3 pt-2">
                  <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-900 font-medium">
                    ✔ {language === 'hi' ? 'उद्योगों का वास्तविक प्रतिशत वर्गीकरण' : 'Empirical enterprise scale distribution (Micro/Small/Medium)'}
                  </div>
                  <div className="p-3.5 rounded-xl bg-blue-50/60 border border-blue-100 text-xs text-blue-900 font-medium">
                    ✔ {language === 'hi' ? 'खुले मौसम API द्वारा जलवायु जोखिम संकेत' : 'Open-Meteo microclimate footfall & logistics disruption signals'}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'schemes' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
                    <Landmark className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      {language === 'hi' ? '60+ सरकारी योजनाओं का मिलान' : 'Deterministic Statutory Eligibility Matcher'}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {language === 'hi' ? 'मुद्रा, पीएमईजीपी, स्टैंड-अप इंडिया और राज्य योजनाएं' : 'Matches age, gender, category, and investment with statutory rules'}
                    </p>
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-3 pt-2">
                  <div className="p-3.5 rounded-xl bg-amber-50/60 border border-amber-100 text-xs text-amber-900 font-medium">
                    ✔ {language === 'hi' ? 'पात्रता की गारंटीकृत गणना' : 'Exact statutory eligibility confidence scoring & disqualification reasons'}
                  </div>
                  <div className="p-3.5 rounded-xl bg-purple-50/60 border border-purple-100 text-xs text-purple-900 font-medium">
                    ✔ {language === 'hi' ? 'सब्सिडी और मार्जिन मनी ऑटो-कैलकुलेशन' : 'Instant subsidy & margin money statutory calculations'}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'finance' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                    <BadgeIndianRupee className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      {language === 'hi' ? 'ऋण संरचना और किफायती EMI सलाहकार' : 'Financial Structuring & EMI Affordability'}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {language === 'hi' ? 'ऋण-से-आय (DTI) और पुनर्भुगतान परिदृश्य' : 'Calculates safe repayment limits based on monthly surplus'}
                    </p>
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-3 pt-2">
                  <div className="p-3.5 rounded-xl bg-blue-50/60 border border-blue-100 text-xs text-blue-900 font-medium">
                    ✔ {language === 'hi' ? 'रूढ़िवादी, अनुशंसित और विस्तारित ऋण परिदृश्य' : 'Conservative, Recommended & Extended tenure EMI scenarios'}
                  </div>
                  <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-900 font-medium">
                    ✔ {language === 'hi' ? 'सीजीटीएमएसई क्रेडिट गारंटी कवरेज' : 'CGTMSE credit guarantee coverage analysis'}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'dpr' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
                    <FileSpreadsheet className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      {language === 'hi' ? 'कैनोनिकल 13-अनुभाग डीपीआर और पीडीएफ रिपोर्ट' : '13-Section Canonical DPR Generator'}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {language === 'hi' ? 'बैंक जमा करने के लिए तैयार विस्तृत रिपोर्ट' : 'Bank-ready PDF detailed project reports synthesized in under 60s'}
                    </p>
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-3 pt-2">
                  <div className="p-3.5 rounded-xl bg-purple-50/60 border border-purple-100 text-xs text-purple-900 font-medium">
                    ✔ {language === 'hi' ? 'क्लोद 3.5 सॉनेट द्वारा AI विश्लेषण' : 'Anthropic Claude 3.5 Sonnet qualitative market synthesis'}
                  </div>
                  <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-900 font-medium">
                    ✔ {language === 'hi' ? 'डाउनलोड करने योग्य PDF और 7-दिवसीय साझा लिंक' : 'Downloadable PDF & 7-day shareable report URL'}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
