'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import Navbar from '@/components/Navbar';
import BusinessIntelligenceMap from '@/components/BusinessIntelligenceMap';
import ScrollRevealDashboard from '@/components/ScrollRevealDashboard';
import BusinessEcosystemBackground from '@/components/BusinessEcosystemBackground';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  ArrowRight,
  Sparkles,
  TrendingUp,
  Landmark,
  BadgeIndianRupee,
  FileSpreadsheet,
  ShieldCheck,
  Building2,
  Store,
  Utensils,
  Wheat,
  Wrench,
  CheckCircle2,
  ChevronRight,
  Compass,
  FileText,
  MapPin,
  ExternalLink,
} from 'lucide-react';

export default function LandingPage() {
  const { t, language } = useLanguage();

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F8F5] text-[#0B1736] font-sans selection:bg-[#159A68] selection:text-white">
      <Navbar />

      {/* ========================================================================= */}
      {/* 1. HERO SECTION */}
      {/* ========================================================================= */}
      <section className="relative overflow-hidden pt-10 pb-16 md:pt-16 md:pb-24 border-b border-slate-200/80 bg-gradient-to-b from-[#F7F8F5] via-white to-[#F7F8F5]">
        <BusinessEcosystemBackground />
        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Hero Typography & CTA Block */}
          <div className="max-w-3xl mx-auto text-center mb-10 sm:mb-12">
            
            {/* Eyebrow */}
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-[#EAF6F0] border border-[#159A68]/20 text-[#159A68] text-xs font-bold tracking-wider uppercase mb-5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>SIH26091 • AI HYPER-LOCAL ADVISORY</span>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-3xl sm:text-5xl md:text-6xl font-black text-[#0B1736] tracking-tight leading-[1.15] mb-5"
            >
              Turn Local Insight<br className="hidden sm:inline" /> Into Better Business.
            </motion.h1>

            {/* Supporting Copy */}
            <motion.p
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal mb-8"
            >
              UnnatE helps micro and rural entrepreneurs understand their market, plan investments, discover financing opportunities and navigate government schemes — all in one place.
            </motion.p>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-3.5"
            >
              <Link
                href="/dashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-lg bg-[#0B1736] hover:bg-[#159A68] text-white font-bold text-sm shadow-xs transition-colors group"
              >
                <span>Explore Your Business</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </Link>

              <Link
                href="#how-it-works"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm border border-slate-200 shadow-xs transition-colors"
              >
                <span>See How It Works</span>
              </Link>
            </motion.div>
          </div>

          {/* Business Intelligence Map Visual (Product-Oriented Canvas) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <BusinessIntelligenceMap />
          </motion.div>

        </div>
      </section>

      {/* ========================================================================= */}
      {/* 2. TRUST / VALUE STRIP */}
      {/* ========================================================================= */}
      <section className="bg-white border-b border-slate-200/80 py-8 sm:py-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Value 1 */}
            <div className="p-4 rounded-xl bg-[#F7F8F5] border border-slate-200/70 flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-lg bg-[#EAF6F0] text-[#159A68] flex items-center justify-center shrink-0 mt-0.5">
                <TrendingUp className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Local Market</span>
                <span className="text-xs font-bold text-[#0B1736] block mt-0.5">Understand demand around you</span>
              </div>
            </div>

            {/* Value 2 */}
            <div className="p-4 rounded-xl bg-[#F7F8F5] border border-slate-200/70 flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center shrink-0 mt-0.5">
                <BadgeIndianRupee className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Financing</span>
                <span className="text-xs font-bold text-[#0B1736] block mt-0.5">Find relevant funding opportunities</span>
              </div>
            </div>

            {/* Value 3 */}
            <div className="p-4 rounded-xl bg-[#F7F8F5] border border-slate-200/70 flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-lg bg-amber-50 text-[#F4A340] flex items-center justify-center shrink-0 mt-0.5">
                <Landmark className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Government Schemes</span>
                <span className="text-xs font-bold text-[#0B1736] block mt-0.5">Discover schemes you may qualify for</span>
              </div>
            </div>

            {/* Value 4 */}
            <div className="p-4 rounded-xl bg-[#F7F8F5] border border-slate-200/70 flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center shrink-0 mt-0.5">
                <FileSpreadsheet className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">DPR Builder</span>
                <span className="text-xs font-bold text-[#0B1736] block mt-0.5">Generate structured business reports</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. HOW UNNATE WORKS (4-Step Editorial Section) */}
      {/* ========================================================================= */}
      <section id="how-it-works" className="py-20 sm:py-24 bg-[#F7F8F5] border-b border-slate-200/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#159A68] uppercase tracking-wider block mb-2">
              Four-Step Consulting Workflow
            </span>
            <h2 className="text-2xl sm:text-4xl font-black text-[#0B1736] tracking-tight mb-4">
              How UnnatE Works in 4 Simple Steps
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed font-normal">
              Empowering micro and rural entrepreneurs with deterministic scheme matching, empirical demand analytics, and bank-ready DPR documentation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Step 01 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="text-2xl font-black text-[#159A68] mb-3">01</div>
                <h3 className="text-sm font-bold text-[#0B1736] mb-2">
                  Tell us about your business
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Enter your trade, location (state and district), and capital scale in Hindi or English.
                </p>
              </div>
              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center gap-1.5 text-[11px] font-semibold text-slate-500">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#159A68]" />
                <span>1-minute profile setup</span>
              </div>
            </motion.div>

            {/* Step 02 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="text-2xl font-black text-[#159A68] mb-3">02</div>
                <h3 className="text-sm font-bold text-[#0B1736] mb-2">
                  Understand your local market
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Access empirical MSME density, nearby cluster benchmarks, and local demand indicators.
                </p>
              </div>
              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center gap-1.5 text-[11px] font-semibold text-slate-500">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#159A68]" />
                <span>785 districts analyzed</span>
              </div>
            </motion.div>

            {/* Step 03 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.3 }}
              className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="text-2xl font-black text-[#159A68] mb-3">03</div>
                <h3 className="text-sm font-bold text-[#0B1736] mb-2">
                  Discover finance & schemes
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Deterministic statutory rule engine matches your profile across central and state schemes.
                </p>
              </div>
              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center gap-1.5 text-[11px] font-semibold text-slate-500">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#159A68]" />
                <span>Statutory 100-pt gate</span>
              </div>
            </motion.div>

            {/* Step 04 */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.4 }}
              className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="text-2xl font-black text-[#159A68] mb-3">04</div>
                <h3 className="text-sm font-bold text-[#0B1736] mb-2">
                  Build your growth plan
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Download bank-ready 13-section Detailed Project Reports with structured repayment scenarios.
                </p>
              </div>
              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center gap-1.5 text-[11px] font-semibold text-slate-500">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#159A68]" />
                <span>Bank-ready PDF export</span>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 4. PRODUCT PREVIEW SECTION */}
      {/* ========================================================================= */}
      <section id="analysis" className="py-16 sm:py-20 bg-white border-b border-slate-200/80">
        <ScrollRevealDashboard />
      </section>

      {/* ========================================================================= */}
      {/* 5. BUILT FOR MICRO & RURAL ENTREPRENEURS */}
      {/* ========================================================================= */}
      <section id="entrepreneurs" className="py-20 sm:py-24 bg-[#F7F8F5] border-b border-slate-200/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#159A68] uppercase tracking-wider block mb-2">
              Foundational Trade Categories
            </span>
            <h2 className="text-2xl sm:text-4xl font-black text-[#0B1736] tracking-tight mb-4">
              Built for Real-World Micro & Rural Enterprises
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed font-normal">
              Practical advisory structured specifically for local entrepreneurs across India's primary commercial sectors.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            
            {/* Category 1 */}
            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs hover:border-[#159A68]/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-[#EAF6F0] text-[#159A68] flex items-center justify-center mb-4">
                <Store className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-[#0B1736] mb-1.5">
                Retail & Micro-Commerce
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Kirana stores, rural distributors, apparel shops, and daily necessities retail.
              </p>
              <div className="text-[11px] font-semibold text-[#159A68]">
                PM SVANidhi & MUDRA Shishu
              </div>
            </div>

            {/* Category 2 */}
            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs hover:border-[#159A68]/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center mb-4">
                <Utensils className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-[#0B1736] mb-1.5">
                Food & Agro-Processing
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Dairy collection units, grain and flour milling, bakery, and cold chain logistics.
              </p>
              <div className="text-[11px] font-semibold text-blue-700">
                PMEGP & PMFME Subsidies
              </div>
            </div>

            {/* Category 3 */}
            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs hover:border-[#159A68]/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-amber-50 text-[#F4A340] flex items-center justify-center mb-4">
                <Wheat className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-[#0B1736] mb-1.5">
                Agriculture & Allied
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Protected polyhouses, poultry units, solar water pumping, and seed production.
              </p>
              <div className="text-[11px] font-semibold text-[#F4A340]">
                AIF & Nabard Refinance
              </div>
            </div>

            {/* Category 4 */}
            <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs hover:border-[#159A68]/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center mb-4">
                <Wrench className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-[#0B1736] mb-1.5">
                Local Services & Artisans
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Handloom weaving, light fabrication, automotive repair, and electrical workshops.
              </p>
              <div className="text-[11px] font-semibold text-purple-700">
                PM Vishwakarma & CGTMSE
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 6. LOCAL INTELLIGENCE SECTION */}
      {/* ========================================================================= */}
      <section className="py-20 sm:py-24 bg-white border-b border-slate-200/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="max-w-3xl mb-12">
            <span className="text-xs font-bold text-[#159A68] uppercase tracking-wider block mb-2">
              Empirical District Insights
            </span>
            <h2 className="text-2xl sm:text-4xl font-black text-[#0B1736] tracking-tight mb-4">
              Your district has a story.<br />UnnatE helps you read it.
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              Every Indian district exhibits distinct supply chain gaps and consumer absorption rates. We map official census data and enterprise registers into clear, actionable business guidance.
            </p>
          </div>

          {/* Analytical District Metrics Dashboard Card */}
          <div className="bg-[#F7F8F5] rounded-2xl border border-slate-200/90 p-6 sm:p-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              
              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Demand Absorption</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0B1736]">88 / 100</div>
                <p className="text-xs text-slate-500">
                  High local consumption with regional supply deficit.
                </p>
              </div>

              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Enterprise Density</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0B1736]">14,200+</div>
                <p className="text-xs text-slate-500">
                  Active registered micro units in current district cluster.
                </p>
              </div>

              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Customer Catchment</span>
                <div className="text-2xl sm:text-3xl font-black text-[#0B1736]">Tier 2 / 3 Hub</div>
                <p className="text-xs text-slate-500">
                  High household density within a 20km commercial radius.
                </p>
              </div>

              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Growth Velocity</span>
                <div className="text-2xl sm:text-3xl font-black text-[#159A68]">+18.4% YoY</div>
                <p className="text-xs text-slate-500">
                  Expanding trade volume across primary commercial categories.
                </p>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* ========================================================================= */}
      {/* 7. FINANCE + GOVERNMENT SCHEMES (Split Section) */}
      {/* ========================================================================= */}
      <section className="py-20 sm:py-24 bg-[#F7F8F5] border-b border-slate-200/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#159A68] uppercase tracking-wider block mb-2">
              Statutory Support Navigation
            </span>
            <h2 className="text-2xl sm:text-4xl font-black text-[#0B1736] tracking-tight mb-4">
              Know what you can access.
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed font-normal">
              Deterministic statutory rules evaluate eligibility in real-time without middlemen or guesswork.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* Split Card 1: Financing Stack */}
            <div className="bg-white p-7 rounded-2xl border border-slate-200/90 shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-lg font-black text-[#0B1736]">Financing Stack</h3>
                    <p className="text-xs text-slate-500">Commercial & priority sector credit lines</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
                    <BadgeIndianRupee className="w-5 h-5" />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0B1736]">PMMY MUDRA Loans</span>
                      <span className="text-xs font-extrabold text-[#159A68]">Up to ₹10L</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      Collateral-free credit across Shishu, Kishore, and Tarun categories.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0B1736]">CGTMSE Guarantee</span>
                      <span className="text-xs font-extrabold text-blue-700">Up to ₹5 Cr</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      Credit guarantee support for collateral-free MSME bank term loans.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0B1736]">Stand-Up India</span>
                      <span className="text-xs font-extrabold text-purple-700">₹10L – ₹1 Cr</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      Greenfield business loans for women and SC/ST promoters.
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-6 mt-6 border-t border-slate-100">
                <Link
                  href="/advisory/financial"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-[#159A68] hover:text-[#0E754E] transition-colors"
                >
                  <span>Explore Financing Structures</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Split Card 2: Government Subsidies */}
            <div className="bg-white p-7 rounded-2xl border border-slate-200/90 shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-lg font-black text-[#0B1736]">Government Schemes</h3>
                    <p className="text-xs text-slate-500">Central & state statutory subsidies</p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-[#EAF6F0] text-[#159A68] flex items-center justify-center">
                    <Landmark className="w-5 h-5" />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0B1736]">PMEGP Capital Subsidy</span>
                      <span className="text-xs font-extrabold text-[#159A68]">15% – 35%</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      Margin money capital subsidy on total project cost for manufacturing and services.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0B1736]">PM Vishwakarma</span>
                      <span className="text-xs font-extrabold text-amber-600">5% Concession</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      End-to-end artisan recognition, skill verification, and credit support.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0B1736]">PM SVANidhi</span>
                      <span className="text-xs font-extrabold text-blue-700">₹10k – ₹50k</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">
                      Micro-working capital with prompt repayment 7% interest subsidy.
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-6 mt-6 border-t border-slate-100">
                <Link
                  href="/advisory/schemes"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-[#159A68] hover:text-[#0E754E] transition-colors"
                >
                  <span>Check Scheme Eligibility</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 8. STRONG FINAL CTA */}
      {/* ========================================================================= */}
      <section className="py-20 bg-[#0B1736] text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <span className="text-xs font-bold text-[#F4A340] uppercase tracking-wider block">
            Get Started Today
          </span>
          <h2 className="text-3xl sm:text-5xl font-black tracking-tight leading-[1.15]">
            Your next business decision<br />starts with better information.
          </h2>
          <p className="text-sm sm:text-base text-slate-300 max-w-xl mx-auto leading-relaxed font-normal">
            Understand your market. Find the right support. Build with confidence.
          </p>
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg bg-[#159A68] hover:bg-[#0E754E] text-white font-bold text-sm shadow-sm transition-colors group"
            >
              <span>Start Your Business Analysis</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <Link
              href="/advisory/schemes"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-white/10 hover:bg-white/15 text-white font-bold text-sm border border-white/20 transition-colors"
            >
              <span>Review Government Schemes</span>
            </Link>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 9. PROFESSIONAL CIVIC-TECH FOOTER */}
      {/* ========================================================================= */}
      <footer id="about" className="bg-white text-slate-600 border-t border-slate-200 py-12 sm:py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-12 border-b border-slate-200">
            
            {/* Column 1: Brand */}
            <div className="space-y-3 md:col-span-1">
              <div className="flex items-center gap-2.5">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/logo.png"
                  alt="UnnatE Logo"
                  className="h-9 w-auto object-contain"
                />
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                PLAN • GROW • SUCCEED<br />
                AI-Driven Hyper-Local Business Advisory and Financial Structuring Platform for Micro-Entrepreneurs.
              </p>
              <div className="text-[11px] font-bold text-slate-400">
                Official Submission • SIH26091
              </div>
            </div>

            {/* Column 2: Platform */}
            <div className="space-y-2.5 text-xs">
              <span className="font-bold text-[#0B1736] uppercase tracking-wider block mb-3">
                Platform
              </span>
              <Link href="#how-it-works" className="block hover:text-[#159A68] transition-colors">
                How It Works
              </Link>
              <Link href="#analysis" className="block hover:text-[#159A68] transition-colors">
                Market Analysis
              </Link>
              <Link href="#entrepreneurs" className="block hover:text-[#159A68] transition-colors">
                For Entrepreneurs
              </Link>
              <Link href="/dashboard" className="block hover:text-[#159A68] transition-colors">
                Advisory Dashboard
              </Link>
            </div>

            {/* Column 3: Resources */}
            <div className="space-y-2.5 text-xs">
              <span className="font-bold text-[#0B1736] uppercase tracking-wider block mb-3">
                Resources
              </span>
              <Link href="/advisory/schemes" className="block hover:text-[#159A68] transition-colors">
                Government Schemes
              </Link>
              <Link href="/advisory/financial" className="block hover:text-[#159A68] transition-colors">
                Financing Options
              </Link>
              <Link href="/advisory/business-plan" className="block hover:text-[#159A68] transition-colors">
                DPR Builder
              </Link>
              <Link href="/chat" className="block hover:text-[#159A68] transition-colors">
                AI Advisory Assistant
              </Link>
            </div>

            {/* Column 4: About */}
            <div className="space-y-2.5 text-xs">
              <span className="font-bold text-[#0B1736] uppercase tracking-wider block mb-3">
                About
              </span>
              <Link href="#about" className="block hover:text-[#159A68] transition-colors">
                About UnnatE
              </Link>
              <div className="text-slate-500">
                Smart India Hackathon 2024
              </div>
              <div className="text-slate-500">
                Deterministic Rule Engine Active
              </div>
              <div className="text-slate-500">
                Census 2011 & Udyam 2024-25
              </div>
            </div>

          </div>

          <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
            <p>© 2026 UnnatE. Built for Indian Micro and Rural Entrepreneurs.</p>
            <p>Smart India Hackathon (SIH26091) Official Presentation.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
