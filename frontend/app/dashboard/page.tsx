'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { useLanguage } from '@/lib/i18n/useLanguage';
import { useAppStore } from '@/lib/store';
import {
  TrendingUp,
  Landmark,
  BadgeIndianRupee,
  ShieldCheck,
  Plus,
  MapPin,
  Search,
  ArrowUpRight,
  Sun,
  FileSpreadsheet,
  ChevronRight,
  CloudSun,
  CloudRain,
  Compass,
  CheckCircle2,
  AlertTriangle,
  BrainCircuit,
  Sparkles,
  BarChart3,
  Layers,
  Info,
  Building2,
  Scale,
  ShieldAlert,
  Lightbulb,
  Thermometer,
  Wind,
  Truck,
  Activity,
  Store,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from 'recharts';
import { MarketIntelligenceResponse } from '@/lib/api-client';

export default function DashboardPage() {
  const { t } = useLanguage();
  const { user, setUser } = useAppStore();
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [marketIntelligence, setMarketIntelligence] = useState<MarketIntelligenceResponse | null>(null);
  const [researchLoading, setResearchLoading] = useState(false);
  const [researchError, setResearchError] = useState<string | null>(null);
  const [programCount, setProgramCount] = useState<number>(60);

  useEffect(() => {
    // Fetch profile and user businesses
    fetch('/api/user/profile')
      .then((res) => res.json())
      .then((data) => {
        if (data.user) {
          setUser(data.user);
        }
      })
      .catch(() => {});

    fetch('/api/businesses')
      .then((res) => res.json())
      .then((data) => {
        if (data.businesses) setBusinesses(data.businesses);
      })
      .finally(() => setLoading(false));

    // Fetch authoritative programme count from FastAPI
    fetch('/api/schemes?limit=1')
      .then((res) => res.json())
      .then((data) => {
        if (data.count) setProgramCount(data.count);
      })
      .catch(() => {});
  }, [setUser]);

  // Fetch unified market intelligence (ML clustering + LLM analysis + real MSME & weather data)
  useEffect(() => {
    if (!user?.district || !user?.state) {
      setMarketIntelligence(null);
      setResearchLoading(false);
      setResearchError(null);
      return;
    }

    setResearchLoading(true);
    setResearchError(null);

    const primaryBusiness = businesses && businesses.length > 0 ? businesses[0] : null;
    const businessContext = primaryBusiness ? {
      business_type: primaryBusiness.type,
      sub_type: primaryBusiness.subType,
      experience_level: primaryBusiness.experienceLevel,
      target_market: primaryBusiness.targetMarket,
      current_income: primaryBusiness.currentIncome,
      estimated_capital: primaryBusiness.estimatedCapital,
      existing_debt: primaryBusiness.existingDebt,
    } : undefined;

    fetch('/api/research/market-intelligence', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state_name: user.state,
        district_name: user.district,
        business_profile: businessContext,
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (data && !data.error) {
          setMarketIntelligence(data);
        } else {
          setMarketIntelligence(null);
          setResearchError(data?.error || 'Failed to load market intelligence');
        }
      })
      .catch((err) => {
        console.warn('Could not fetch market intelligence:', err);
        setMarketIntelligence(null);
        setResearchError(err.message || 'Network error');
      })
      .finally(() => {
        setResearchLoading(false);
      });
  }, [user?.state, user?.district, businesses]);

  const market = marketIntelligence?.market_context;
  const weather = marketIntelligence?.weather_context;
  const ml = marketIntelligence?.ml_analysis;
  const llm = marketIntelligence?.llm_analysis;
  const weatherImpact = marketIntelligence?.weather_activity_impact;
  const observations = marketIntelligence?.research_observations || [];
  const cautions = marketIntelligence?.operational_cautions || [];
  const activeDistrictName = marketIntelligence?.district_name || user?.district;
  const primaryBusiness = businesses && businesses.length > 0 ? businesses[0] : null;

  // Helper styling for Indicative Weather Activity Impact badges
  const getActivityBadgeStyle = (label?: string | null) => {
    switch (label) {
      case 'Very Favourable':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'Favourable':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'Neutral':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'Potentially Disruptive':
        return 'bg-amber-100 text-amber-900 border-amber-300';
      case 'Highly Disruptive':
        return 'bg-rose-100 text-rose-900 border-rose-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getRiskSignalStyle = (level?: string | null) => {
    switch (level?.toLowerCase()) {
      case 'severe':
      case 'high':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      case 'moderate':
      case 'moderate disruption':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'lower':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      case 'favourable':
      case 'normal':
      case 'none':
      case 'low':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  // Weather Activity Outlook Line Chart Data (Strictly 3-Day Forecast)
  const weatherOutlookChartData = (weatherImpact?.weather_outlook_3days || []).map((item) => ({
    day: item.day_name,
    score: item.impact_score,
    label: item.impact_label,
    temp: item.temp_range,
    rain: `${item.precipitation_sum_mm}mm`,
    condition: item.weather_description,
  }));

  // Real Enterprise Scale Distribution Data for Chart (Micro, Small, Medium)
  const enterpriseScaleChartData = market ? [
    {
      tier: 'Micro',
      fullName: 'Micro Enterprises',
      count: market.micro_enterprises,
      share: Number(market.micro_share?.toFixed(1) || 0),
      color: '#059669',
    },
    {
      tier: 'Small',
      fullName: 'Small Enterprises',
      count: market.small_enterprises,
      share: Number(market.small_share?.toFixed(1) || 0),
      color: '#2563eb',
    },
    {
      tier: 'Medium',
      fullName: 'Medium Enterprises',
      count: market.medium_enterprises,
      share: Number(market.medium_share?.toFixed(1) || 0),
      color: '#7c3aed',
    },
  ] : [];

  return (
    <div className="min-h-screen bg-[#F7F8F5] text-[#0B1736] flex flex-col font-sans">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6">
          
          {/* Top Bar with Search & Location */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
            <div className="relative w-full md:w-96">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search schemes, markets, or ask anything... (Ctrl K)"
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#F7F8F5] border border-slate-200 text-xs text-[#0B1736] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#159A68] focus:border-transparent transition"
              />
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#EAF7F0] text-[#159A68] text-xs font-bold border border-[#159A68]/20">
                <MapPin className="w-3.5 h-3.5 text-[#159A68]" />
                {user?.district && user?.state ? (
                  <span>{user.district}, {user.state}</span>
                ) : (
                  <span className="text-amber-800 flex items-center gap-1">
                    Location Not Configured
                    <Link href="/dashboard/profile" className="underline font-bold text-[#159A68] ml-1">
                      Set District
                    </Link>
                  </span>
                )}
              </div>

              <Link
                href="/advisory/business-plan"
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0B1736] hover:bg-[#159A68] text-white text-xs font-bold shadow-xs transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>{t('dashboard.startNewAnalysis')}</span>
              </Link>
            </div>
          </div>

          {/* Missing Location Alert Banner */}
          {(!user?.district || !user?.state) && (
            <div className="p-4 rounded-2xl bg-[#FFF5DF] border border-amber-200/80 text-amber-950 text-xs flex items-center justify-between shadow-xs">
              <div className="flex items-center gap-2.5">
                <MapPin className="w-5 h-5 text-[#F4A340] shrink-0" />
                <div>
                  <p className="font-bold text-[#0B1736]">District location not configured</p>
                  <p className="text-slate-600">Complete your location in your profile to view district-specific MSME market intelligence, ML classification, and microclimate signals.</p>
                </div>
              </div>
              <Link
                href="/dashboard/profile"
                className="px-3.5 py-1.5 rounded-xl bg-[#F4A340] hover:bg-[#E2922F] text-white font-bold text-xs shrink-0 shadow-xs transition-colors"
              >
                Complete Profile
              </Link>
            </div>
          )}

          {/* Greeting Banner */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-black text-[#0B1736] tracking-tight flex items-center gap-2">
                <span>{t('dashboard.greeting')}</span>
                <Sun className="w-6 h-6 text-[#F4A340] fill-amber-400" />
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                {user?.district && user?.state
                  ? `Empirical MSME intelligence & statutory assistance overview for ${activeDistrictName}, ${user.state}.`
                  : 'Complete your business profile to view location-specific MSME market intelligence and weather signals.'}
              </p>
            </div>
          </div>

          {/* 4 Quick Stats Cards (Differentiated Editorial Information Blocks) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* 1. Market Demand / Density Card */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-[#EAF7F0] text-[#159A68] flex items-center justify-center">
                    <TrendingUp className="w-4 h-4" />
                  </div>
                  <span className="px-2.5 py-0.5 rounded-md bg-[#EAF7F0] text-[#159A68] border border-[#159A68]/20 text-[11px] font-bold">
                    {market?.state_rank 
                      ? `Rank #${market.state_rank}${market.total_districts_in_state ? `/${market.total_districts_in_state}` : ''}` 
                      : (researchLoading ? 'Loading...' : (user?.district ? 'Pending' : 'No District'))}
                  </span>
                </div>
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{t('dashboard.marketDemand')}</div>
                <div className="text-2xl font-black text-[#0B1736] tracking-tight mt-1">
                  {market?.total_msmes 
                    ? `${(market.total_msmes / 1000).toFixed(1)}k MSMEs` 
                    : (researchLoading ? 'Loading...' : (user?.district ? 'Pending' : 'Set Location'))}
                </div>
              </div>
              <p className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 font-medium">
                {market?.micro_share !== undefined 
                  ? `${market.micro_share.toFixed(1)}% Micro Enterprises` 
                  : (user?.district ? 'Official Udyam records' : 'District profile required')}
              </p>
            </div>

            {/* 2. Relevant Schemes Card */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-[#FFF5DF] text-[#F4A340] flex items-center justify-center">
                    <Landmark className="w-4 h-4" />
                  </div>
                  <span className="px-2.5 py-0.5 rounded-md bg-[#FFF5DF] text-[#D97706] border border-amber-200/70 text-[11px] font-bold">
                    {programCount > 0 ? `${programCount}` : '60+'}
                  </span>
                </div>
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{t('dashboard.relevantSchemes')}</div>
                <div className="text-2xl font-black text-[#0B1736] tracking-tight mt-1">
                  {programCount > 0 ? `${programCount} Programmes` : '60 Available'}
                </div>
              </div>
              <p className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 font-medium">
                Central Sector & Centrally Sponsored
              </p>
            </div>

            {/* 3. Capital Advisory & Structuring Card */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-[#EEF4FA] text-blue-700 flex items-center justify-center">
                    <BadgeIndianRupee className="w-4 h-4" />
                  </div>
                  <span className="px-2.5 py-0.5 rounded-md bg-[#EEF4FA] text-blue-800 border border-blue-200/60 text-[11px] font-bold">
                    Statutory Bounds
                  </span>
                </div>
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Capital Advisory</div>
                <div className="text-2xl font-black text-[#0B1736] tracking-tight mt-1">
                  {primaryBusiness?.estimatedCapital
                    ? `₹${(primaryBusiness.estimatedCapital / 100000).toFixed(1)}L Target`
                    : 'Up to ₹50 Lakhs'}
                </div>
              </div>
              <div className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
                <span>PMEGP, MUDRA & CGTMSE</span>
                <Link href="/advisory/financial" className="text-[#159A68] hover:underline font-bold flex items-center gap-0.5">
                  Structuring <ChevronRight className="w-3 h-3" />
                </Link>
              </div>
            </div>

            {/* 4. Climate & Environmental Context Card */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-[#EAF7F0] text-[#159A68] flex items-center justify-center">
                    {weather?.current ? (
                      (weather.current.precipitation_mm > 0 || weather.current.weather_code >= 50) ? (
                        <CloudRain className="w-4 h-4 text-[#159A68]" />
                      ) : (
                        <CloudSun className="w-4 h-4 text-[#159A68]" />
                      )
                    ) : (
                      <ShieldCheck className="w-4 h-4 text-[#159A68]" />
                    )}
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-md text-[11px] font-bold ${
                    weather?.current
                      ? (weather.is_stale ? 'bg-amber-100 text-amber-800' : 'bg-[#EAF7F0] text-[#159A68] border border-[#159A68]/20')
                      : 'bg-slate-100 text-slate-600'
                  }`}>
                    {researchLoading
                      ? 'Fetching...'
                      : weather?.current
                      ? (weather.is_stale ? 'Cached Snapshot' : 'Open-Meteo Live')
                      : (user?.district ? (researchError ? 'Offline' : 'Unavailable') : 'Location Needed')}
                  </span>
                </div>
                
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  {weather?.current ? `Local Weather • ${activeDistrictName}` : 'District Climate Context'}
                </div>
                
                <div className="text-xl sm:text-2xl font-black text-[#0B1736] tracking-tight mt-1">
                  {researchLoading ? (
                    <span className="text-slate-400 text-base font-semibold animate-pulse">Loading Climate...</span>
                  ) : weather?.current ? (
                    `${Math.round(weather.current.temperature_c)}°C • ${weather.current.weather_description}`
                  ) : user?.district ? (
                    <span className="text-slate-500 text-base font-semibold">Weather Unavailable</span>
                  ) : (
                    'Set Location'
                  )}
                </div>
              </div>

              <div className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100">
                {weather?.current ? (
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>Feels {Math.round(weather.current.apparent_temperature_c)}°C</span>
                    <span>•</span>
                    <span>Rain {weather.current.precipitation_mm}mm</span>
                    <span>•</span>
                    <span>Hum {weather.current.relative_humidity_pct}%</span>
                    <span>•</span>
                    <span>Wind {Math.round(weather.current.wind_speed_kmh)}km/h</span>
                  </div>
                ) : (
                  <p className="text-slate-400">
                    {user?.district
                      ? (researchError || 'Live signal offline; external service unreachable')
                      : 'Configure district in profile'}
                  </p>
                )}
              </div>
            </div>

          </div>

          {/* Empirical District Research Intelligence Banner */}
          {(observations.length > 0 || cautions.length > 0 || (weather?.forecast_3days && weather.forecast_3days.length > 0)) && (
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
                  <Compass className="w-4 h-4 text-emerald-600" />
                  <span>Empirical District Research Intelligence ({activeDistrictName}, {user?.state || ''})</span>
                </div>
                {weather?.fetched_at && (
                  <span className="text-[10px] text-slate-400">
                    Updated: {new Date(weather.fetched_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} ({weather.source})
                  </span>
                )}
              </div>

              {/* Operational Cautions / Climate Alerts (Deterministic Backend Warnings) */}
              {cautions.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Statutory & Operational Climate/Market Advisories</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {cautions.map((caution: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-amber-900 bg-amber-50/80 p-2.5 rounded-xl border border-amber-200">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                        <span>{caution}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 3-Day Weather Forecast Strip */}
              {weather?.forecast_3days && weather.forecast_3days.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-[11px] font-bold text-slate-500 flex items-center gap-1.5">
                    <CloudSun className="w-3.5 h-3.5 text-purple-600" />
                    <span>3-Day Microclimate Forecast (Open-Meteo Centroid Model)</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    {weather.forecast_3days.map((day, idx) => (
                      <div key={idx} className="bg-purple-50/50 p-3 rounded-xl border border-purple-100 flex flex-col justify-between">
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                          <span>{idx === 0 ? 'Today' : (idx === 1 ? 'Tomorrow' : day.date)}</span>
                          <span className="text-purple-700 font-bold">{Math.round(day.temp_max_c)}° / {Math.round(day.temp_min_c)}°C</span>
                        </div>
                        <div className="text-[11px] text-slate-600 mt-1 font-medium">
                          {day.weather_description}
                        </div>
                        <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2 pt-1.5 border-t border-purple-100/60">
                          <span>Rain: {day.precipitation_sum_mm}mm ({day.precipitation_probability_pct ?? 0}%)</span>
                          <span>Wind: {Math.round(day.wind_speed_max_kmh)}km/h</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empirical Research Observations */}
              {observations.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-[11px] font-bold text-slate-500">Empirical Baseline Observations</div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {observations.map((obs: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{obs}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Parallel Market Research Intelligence: Real Scale Distribution + ML Classification */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Enterprise Scale Distribution Chart (2 Cols) - Replaces fake growth projections */}
            <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-emerald-600" />
                      <h3 className="text-sm font-bold text-slate-900">District MSME Enterprise Scale Breakdown</h3>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      Empirical distribution from official Udyam records for {activeDistrictName}, {user?.state || ''}
                    </p>
                  </div>
                  {market && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-lg border border-emerald-200">
                        State Rank #{market.state_rank} / {market.total_districts_in_state}
                      </span>
                      <span className="text-xs font-bold text-slate-700 bg-slate-100 px-3 py-1 rounded-lg">
                        National Rank #{market.national_rank} / {market.total_districts_nationally || 785}
                      </span>
                    </div>
                  )}
                </div>

                {/* Real Scale Bar Chart */}
                {market ? (
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={enterpriseScaleChartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="tier" stroke="#94a3b8" fontSize={12} />
                        <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                        <Tooltip
                          formatter={(value: any, name: any, item: any) => [
                            `${Number(value).toLocaleString()} units (${item.payload.share}%)`,
                            item.payload.fullName
                          ]}
                          contentStyle={{ backgroundColor: '#fff', borderRadius: '0.75rem', border: '1px solid #e2e8f0', fontSize: '12px' }}
                        />
                        <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                          {enterpriseScaleChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 w-full flex items-center justify-center text-slate-400 text-xs">
                    {researchLoading ? 'Loading empirical enterprise data...' : 'Configure district profile to view enterprise scale breakdown.'}
                  </div>
                )}
              </div>

              {/* Numerical Breakdown Indicators */}
              {market && (
                <div className="grid grid-cols-3 gap-3 pt-4 border-t border-slate-100 mt-4">
                  <div className="bg-emerald-50/60 p-3 rounded-xl border border-emerald-100">
                    <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider">Micro Enterprises</span>
                    <div className="text-base font-black text-emerald-950 mt-0.5">
                      {market.micro_enterprises.toLocaleString()}
                    </div>
                    <span className="text-[10px] text-emerald-700 font-semibold">{market.micro_share.toFixed(1)}% of total</span>
                  </div>

                  <div className="bg-blue-50/60 p-3 rounded-xl border border-blue-100">
                    <span className="text-[10px] font-bold text-blue-800 uppercase tracking-wider">Small Enterprises</span>
                    <div className="text-base font-black text-blue-950 mt-0.5">
                      {market.small_enterprises.toLocaleString()}
                    </div>
                    <span className="text-[10px] text-blue-700 font-semibold">{market.small_share.toFixed(1)}% of total</span>
                  </div>

                  <div className="bg-purple-50/60 p-3 rounded-xl border border-purple-100">
                    <span className="text-[10px] font-bold text-purple-800 uppercase tracking-wider">Medium Enterprises</span>
                    <div className="text-base font-black text-purple-950 mt-0.5">
                      {market.medium_enterprises.toLocaleString()}
                    </div>
                    <span className="text-[10px] text-purple-700 font-semibold">{market.medium_share.toFixed(1)}% of total</span>
                  </div>
                </div>
              )}
            </div>

            {/* ML Market Profile Card (1 Col) - Replaces fake funding sources donut */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <BrainCircuit className="w-4 h-4 text-emerald-600" />
                    <h3 className="text-sm font-bold text-slate-900">ML Market Classification</h3>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    scikit-learn k-means
                  </span>
                </div>

                <p className="text-[11px] text-slate-500 mb-4">
                  Unsupervised district archetype classification based on 785 national district datasets
                </p>

                {ml && ml.is_available ? (
                  <div className="space-y-4">
                    
                    {/* Cluster Badge & Description */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Archetype Cluster</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          Cluster #{ml.cluster_id}
                        </span>
                      </div>
                      <div className="text-xs font-black text-slate-900 leading-snug">
                        {ml.cluster_label}
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        {ml.cluster_description}
                      </p>
                    </div>

                    {/* Market Research Indicator Composite Score */}
                    <div className="p-3.5 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold text-emerald-950">Market Research Indicator</span>
                        <span className="text-sm font-black text-emerald-800">
                          {ml.quantitative_indicators.market_research_indicator.toFixed(1)} <span className="text-[10px] font-normal text-emerald-600">/ 100</span>
                        </span>
                      </div>
                      <div className="w-full bg-emerald-200/50 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-emerald-600 h-2 rounded-full transition-all"
                          style={{ width: `${Math.min(100, Math.max(0, ml.quantitative_indicators.market_research_indicator))}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-emerald-800 flex items-center justify-between">
                        <span>40% Nat Density</span>
                        <span>30% State Density</span>
                        <span>30% Formal SME Depth</span>
                      </div>
                    </div>

                    {/* Quantitative Percentiles */}
                    <div className="space-y-2 text-xs">
                      <div className="flex items-center justify-between py-1 border-b border-slate-100">
                        <span className="text-slate-500 text-[11px]">National Density Percentile</span>
                        <span className="font-bold text-slate-900">{ml.quantitative_indicators.national_density_percentile.toFixed(1)}%</span>
                      </div>
                      <div className="flex items-center justify-between py-1 border-b border-slate-100">
                        <span className="text-slate-500 text-[11px]">State Density Percentile</span>
                        <span className="font-bold text-slate-900">{ml.quantitative_indicators.state_density_percentile.toFixed(1)}%</span>
                      </div>
                      <div className="flex items-center justify-between py-1 border-b border-slate-100">
                        <span className="text-slate-500 text-[11px]">Formal SME Depth Score</span>
                        <span className="font-bold text-slate-900">{ml.quantitative_indicators.sme_depth_score.toFixed(1)} / 100</span>
                      </div>
                      <div className="flex items-center justify-between py-1">
                        <span className="text-slate-500 text-[11px]">Cluster Mean Micro Share</span>
                        <span className="font-bold text-slate-700">{ml.quantitative_indicators.cluster_mean_micro_share.toFixed(1)}%</span>
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="py-12 text-center text-slate-400 text-xs">
                    {researchLoading ? 'Computing ML cluster indicators...' : 'ML analysis pending location configuration.'}
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 text-[10px] text-slate-400">
                Methodology: Deterministic k-means (k=4) fitted on official 785 Udyam district MSME profiles.
              </div>
            </div>

          </div>

          {/* Weather & Business Activity Intelligence Section (Modelled Heuristic Layer) */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
            {/* Header with Title & Provenance Badges */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center">
                  <Activity className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <span>Weather & Business Activity Intelligence</span>
                    <span className="text-xs font-normal text-slate-400">({activeDistrictName}, {user?.state || ''})</span>
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    District atmospheric conditions mapped to indicative enterprise activity and customer footfall signals
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                  Modelled Heuristic
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-800 border border-purple-200">
                  Open-Meteo
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                  Zero Footfall Fabrication
                </span>
              </div>
            </div>

            {weatherImpact && weatherImpact.is_available ? (
              <div className="space-y-5">
                {/* 3 Main Functional Columns */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                  
                  {/* Column 1: Current Weather & Activity Impact Badge */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Current Atmospheric Context</span>
                        {weather?.current && (
                          <span className="text-xs font-bold text-slate-800">
                            {Math.round(weather.current.temperature_c)}°C • {weather.current.weather_description}
                          </span>
                        )}
                      </div>

                      <div className="mt-3 p-3.5 rounded-xl bg-white border border-slate-200 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-700">Indicative Activity Impact</span>
                          <span className={`px-2.5 py-1 rounded-full text-xs font-black border ${getActivityBadgeStyle(weatherImpact.activity_impact_label)}`}>
                            {weatherImpact.activity_impact_label}
                          </span>
                        </div>
                        {weatherImpact.activity_impact_score !== null && weatherImpact.activity_impact_score !== undefined && (
                          <div className="flex items-baseline justify-between pt-1">
                            <span className="text-[11px] text-slate-500">Heuristic Score:</span>
                            <span className="text-base font-black text-slate-900">
                              {weatherImpact.activity_impact_score.toFixed(1)} <span className="text-[10px] font-normal text-slate-500">/ 100</span>
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Potential Footfall / Walk-in Effect */}
                    <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-100">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950 mb-1">
                        <Store className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Potential Footfall / Walk-in Effect</span>
                      </div>
                      <p className="text-[11px] text-emerald-900 leading-relaxed font-medium">
                        {weatherImpact.potential_footfall_effect}
                      </p>
                    </div>
                  </div>

                  {/* Column 2: Business-Specific Operational Implication */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Sector Operational Implication</span>
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 capitalize">
                          {primaryBusiness?.type || 'General Enterprise'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed mt-2 p-3 bg-white rounded-xl border border-slate-200">
                        {weatherImpact.business_type_implication || 'Weather conditions currently present standard operational considerations for this enterprise category.'}
                      </p>
                    </div>

                    <div className="p-2.5 rounded-lg bg-blue-50/60 border border-blue-100 text-[11px] text-blue-900 flex items-center gap-2">
                      <Info className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span>Guidance dynamically adapts to your registered business domain and prevailing humidity/rain/temperature.</span>
                    </div>
                  </div>

                  {/* Column 3: Weather Risk Signals Grid */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Weather Risk Signals</div>
                      <div className="grid grid-cols-2 gap-2 mt-1">
                        
                        {/* Heat Stress */}
                        <div className="p-2.5 rounded-lg bg-white border border-slate-200 flex flex-col justify-between">
                          <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                            <span className="flex items-center gap-1">
                              <Thermometer className="w-3 h-3 text-amber-500" /> Heat Stress
                            </span>
                          </div>
                          <span className={`mt-1.5 px-2 py-0.5 rounded text-[10px] font-bold border text-center ${getRiskSignalStyle(weatherImpact.risk_signals?.heat_stress)}`}>
                            {weatherImpact.risk_signals?.heat_stress || 'Normal'}
                          </span>
                        </div>

                        {/* Rain Disruption */}
                        <div className="p-2.5 rounded-lg bg-white border border-slate-200 flex flex-col justify-between">
                          <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                            <span className="flex items-center gap-1">
                              <CloudRain className="w-3 h-3 text-blue-500" /> Rain Disruption
                            </span>
                          </div>
                          <span className={`mt-1.5 px-2 py-0.5 rounded text-[10px] font-bold border text-center ${getRiskSignalStyle(weatherImpact.risk_signals?.rain_disruption)}`}>
                            {weatherImpact.risk_signals?.rain_disruption || 'None'}
                          </span>
                        </div>

                        {/* Outdoor Activity */}
                        <div className="p-2.5 rounded-lg bg-white border border-slate-200 flex flex-col justify-between">
                          <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                            <span className="flex items-center gap-1">
                              <Compass className="w-3 h-3 text-emerald-500" /> Outdoor Activity
                            </span>
                          </div>
                          <span className={`mt-1.5 px-2 py-0.5 rounded text-[10px] font-bold border text-center ${getRiskSignalStyle(weatherImpact.risk_signals?.outdoor_activity)}`}>
                            {weatherImpact.risk_signals?.outdoor_activity || 'Normal'}
                          </span>
                        </div>

                        {/* Logistics Disruption */}
                        <div className="p-2.5 rounded-lg bg-white border border-slate-200 flex flex-col justify-between">
                          <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                            <span className="flex items-center gap-1">
                              <Truck className="w-3 h-3 text-purple-500" /> Logistics
                            </span>
                          </div>
                          <span className={`mt-1.5 px-2 py-0.5 rounded text-[10px] font-bold border text-center ${getRiskSignalStyle(weatherImpact.risk_signals?.logistics_disruption)}`}>
                            {weatherImpact.risk_signals?.logistics_disruption || 'Low'}
                          </span>
                        </div>

                      </div>
                    </div>

                    <div className="text-[10px] text-slate-400">
                      Heuristic thresholds: Heat (&gt;38°C), Rain (&gt;2.5mm), Wind (&gt;35km/h).
                    </div>
                  </div>

                </div>

                {/* 3-Day Weather Activity Outlook Chart & Strips */}
                {weatherImpact.weather_outlook_3days && weatherImpact.weather_outlook_3days.length > 0 && (
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div>
                        <div className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                          <BarChart3 className="w-3.5 h-3.5 text-teal-600" />
                          <span>Weather Activity Outlook (3-Day Heuristic Projection)</span>
                        </div>
                        <p className="text-[10px] text-slate-500">
                          Ordered projection derived strictly from available Open-Meteo 3-day daily forecasts
                        </p>
                      </div>
                      <span className="text-[10px] text-slate-400">
                        Indicative weather impact (0-100) • No 12-month data fabricated
                      </span>
                    </div>

                    {/* Mini Line Chart for 3-Day Trend */}
                    {weatherOutlookChartData.length > 0 && (
                      <div className="h-28 w-full bg-white p-2 rounded-lg border border-slate-100">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={weatherOutlookChartData} margin={{ top: 10, right: 20, left: -25, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="day" stroke="#94a3b8" fontSize={10} tickLine={false} />
                            <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={9} ticks={[0, 50, 100]} />
                            <Tooltip
                              formatter={(val: any, name: any, item: any) => [
                                `${val}/100 • ${item.payload.label}`,
                                'Activity Impact Score'
                              ]}
                              labelFormatter={(lbl) => `Forecast: ${lbl}`}
                              contentStyle={{ backgroundColor: '#fff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', fontSize: '11px' }}
                            />
                            <Line
                              type="monotone"
                              dataKey="score"
                              stroke="#0d9488"
                              strokeWidth={2}
                              dot={{ r: 4, fill: '#0d9488', stroke: '#fff', strokeWidth: 1.5 }}
                              activeDot={{ r: 6 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* 3 Day Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
                      {weatherImpact.weather_outlook_3days.map((item, idx) => (
                        <div key={idx} className="bg-white p-3 rounded-lg border border-slate-200 flex flex-col justify-between">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-800">{item.day_name}</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getActivityBadgeStyle(item.impact_label)}`}>
                              {item.impact_label}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-600 mt-1 font-medium">
                            {item.temp_range} • {item.weather_description}
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2 pt-1 border-t border-slate-100">
                            <span>Rain: {item.precipitation_sum_mm}mm ({item.precipitation_probability_pct ?? 0}%)</span>
                            <span className="font-semibold text-slate-600">{item.impact_score}/100</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            ) : (
              <div className="py-8 text-center text-slate-400 text-xs bg-slate-50 rounded-xl border border-slate-200">
                {researchLoading
                  ? 'Computing weather activity impact heuristics...'
                  : (user?.district ? 'Weather activity impact currently unavailable for this district.' : 'Configure district profile to view weather activity intelligence.')}
              </div>
            )}

            {/* Mandatory Statutory & Provenance Disclaimer */}
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-[11px] text-slate-500 flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-teal-600 shrink-0" />
                <span>
                  {weatherImpact?.methodology_disclaimer || 'Indicative weather impact on business activity — not observed footfall or a sales forecast.'}
                  {' '}Environmental thresholds are transparent product heuristics chosen to illustrate weather sensitivity. Zero customer counts or revenue projections.
                </span>
              </div>
            </div>
          </div>

          {/* LLM Qualitative Analysis Panel (Server-Side Anthropic Claude Engine) */}
          {llm && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
              
              {/* Header with Grounding Indicator */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">
                      Qualitative Market Intelligence & Strategic Guidance
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Grounded interpretation synthesized from real MSME density and local climate signals
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                    llm.source === 'anthropic-claude-3-5-sonnet'
                      ? 'bg-purple-50 text-purple-800 border border-purple-200'
                      : 'bg-amber-50 text-amber-800 border border-amber-200'
                  }`}>
                    {llm.source === 'anthropic-claude-3-5-sonnet' ? 'Claude 3.5 Sonnet' : 'Empirical Synthesis'}
                  </span>
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    Zero Data Fabrication
                  </span>
                </div>
              </div>

              {/* Market Interpretation Lead Paragraph */}
              {llm.market_interpretation && (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs leading-relaxed text-slate-800">
                  <span className="font-bold text-slate-900 block mb-1">Executive Market Summary:</span>
                  {llm.market_interpretation}
                </div>
              )}

              {/* 4 Qualitative Dimension Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                
                {/* Opportunities */}
                {llm.opportunities && llm.opportunities.length > 0 && (
                  <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-100 space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950">
                      <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Key Opportunities</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-emerald-900">
                      {llm.opportunities.map((item: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-emerald-500 font-bold">•</span>
                          <span className="leading-snug">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Operational Considerations */}
                {llm.operational_considerations && llm.operational_considerations.length > 0 && (
                  <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-100 space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-blue-950">
                      <Compass className="w-3.5 h-3.5 text-blue-600" />
                      <span>Operations & Climate</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-blue-900">
                      {llm.operational_considerations.map((item: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-blue-500 font-bold">•</span>
                          <span className="leading-snug">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Risks */}
                {llm.risks && llm.risks.length > 0 && (
                  <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-100 space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-amber-950">
                      <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                      <span>Market Risk Factors</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-amber-900">
                      {llm.risks.map((item: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-amber-500 font-bold">•</span>
                          <span className="leading-snug">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Practical Recommendations */}
                {llm.practical_recommendations && llm.practical_recommendations.length > 0 && (
                  <div className="p-4 rounded-xl bg-purple-50/50 border border-purple-100 space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-purple-950">
                      <Lightbulb className="w-3.5 h-3.5 text-purple-600" />
                      <span>Strategic Next Steps</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-purple-900">
                      {llm.practical_recommendations.map((item: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-purple-500 font-bold">•</span>
                          <span className="leading-snug">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              </div>

              {/* Grounding & Integrity Assurance Footnote */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-[11px] text-slate-500 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>
                    Deterministic Grounding: Analysis is generated server-side strictly from official Udyam MSME figures and Open-Meteo atmospheric readings. Zero arbitrary growth projections or fabricated statistics.
                  </span>
                </div>
              </div>

            </div>
          )}

          {/* User Businesses & Recent Advisories Table */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-[#0B1736]">{t('dashboard.recentAdvisories')}</h3>
              <Link href="/advisory/business-plan" className="text-xs font-bold text-[#159A68] hover:underline flex items-center gap-1">
                New Plan <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {businesses.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                <FileSpreadsheet className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                <p>No business plans generated yet.</p>
                <Link href="/advisory/business-plan" className="mt-3 inline-block px-4 py-2 rounded-xl bg-[#0B1736] hover:bg-[#159A68] text-white font-bold text-xs shadow-xs transition-colors">
                  Create First Plan
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                      <th className="pb-3">Business Type</th>
                      <th className="pb-3">Capital Target</th>
                      <th className="pb-3">Created Date</th>
                      <th className="pb-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {businesses.map((b, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 font-bold text-[#0B1736] capitalize">{b.type}</td>
                        <td className="py-3 text-slate-700">₹{b.estimatedCapital?.toLocaleString('en-IN')}</td>
                        <td className="py-3 text-slate-500">{new Date(b.createdAt).toLocaleDateString()}</td>
                        <td className="py-3 text-right space-x-2">
                          <Link
                            href={`/dashboard/businesses/${b.id}`}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#EAF7F0] text-[#159A68] font-bold hover:bg-[#d9efe3] transition-colors"
                          >
                            <span>View Details</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </main>
      </div>
    </div>
  );
}
