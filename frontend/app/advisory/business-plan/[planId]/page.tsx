'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import ShareModal from '@/components/ShareModal';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  TrendingUp,
  Calendar,
  CheckCircle,
  AlertTriangle,
  FileCheck,
  Share2,
  ArrowRight,
  Loader2,
  BadgeIndianRupee,
  ShieldCheck,
  Info,
  Building2,
  CheckCircle2,
  ExternalLink,
  RefreshCw,
  Download,
  Landmark,
  Compass,
  Cpu,
  Database,
  BarChart3,
  PieChart as PieChartIcon,
  CloudSun,
  Thermometer,
  CloudRain,
  Truck,
  Activity,
  Printer,
  Edit3,
  Layers,
  HelpCircle,
  ShieldAlert,
  ArrowUpRight,
  ListOrdered,
  Briefcase,
  Users,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { DPRResponse, ComparableDistrictItem, CustomerSegmentItem } from '@/lib/api-client';

// ============================================================================
// Data Provenance Badging & Typography
// ============================================================================

const PROVENANCE_STYLES: Record<string, string> = {
  'USER PROVIDED': 'bg-blue-50 text-blue-700 border-blue-200',
  'GOVERNMENT / DATASET DERIVED': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'BACKEND DETERMINISTIC CALCULATION': 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'MODELLED INDICATOR': 'bg-purple-50 text-purple-700 border-purple-200',
  'AI INTERPRETATION': 'bg-amber-50 text-amber-700 border-amber-200',
  'ILLUSTRATIVE ASSUMPTION': 'bg-orange-50 text-orange-700 border-orange-200',
  'USER EDITED': 'bg-cyan-50 text-cyan-700 border-cyan-200',
};

function ProvenanceBadge({ tag }: { tag: string }) {
  const style = PROVENANCE_STYLES[tag] || 'bg-slate-100 text-slate-700 border-slate-200';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold border ${style} shrink-0`}>
      {tag}
    </span>
  );
}

// Section navigation links
const NAV_SECTIONS = [
  { id: 'sec-exec', label: '1. Executive' },
  { id: 'sec-model', label: '2. Business Model' },
  { id: 'sec-market', label: '3. Market' },
  { id: 'sec-customers', label: '4. Customers' },
  { id: 'sec-competition', label: '5. Competition' },
  { id: 'sec-location', label: '6. Location' },
  { id: 'sec-operations', label: '7. Operations' },
  { id: 'sec-marketing', label: '8. Marketing' },
  { id: 'sec-govt', label: '9. Government Support' },
  { id: 'sec-capital', label: '10. Capital Donut' },
  { id: 'sec-financials', label: '11. Financials' },
  { id: 'sec-risks', label: '12. Risks & Climate' },
  { id: 'sec-implementation', label: '13. Implementation' },
  { id: 'sec-assumptions', label: '14. Assumptions' },
  { id: 'sec-gaps', label: '15. Research Gaps' },
  { id: 'sec-provenance', label: '16. Provenance' },
];

export default function BusinessPlanResultsPage({ params }: { params: { planId: string } }) {
  const { t } = useLanguage();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [dpr, setDpr] = useState<DPRResponse | null>(null);
  const [advisoryMeta, setAdvisoryMeta] = useState<any>(null);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shareOpen, setShareOpen] = useState(false);

  // 1. Fetch Advisory Plan and Profile
  const loadDPRData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [advRes, profRes] = await Promise.all([
        fetch(`/api/advisory/${params.planId}`).then((r) => r.json()).catch(() => ({ advisory: null })),
        fetch('/api/user/profile').then((r) => r.json()).catch(() => ({ user: null, business: null })),
      ]);

      if (profRes) setUserProfile(profRes);

      let canonicalDPR: DPRResponse | null = null;

      // Case A: advisory already contains the canonical 13-section DPRResponse
      if (advRes?.advisory?.planJson?.executive_summary && advRes?.advisory?.planJson?.capital_structure) {
        canonicalDPR = advRes.advisory.planJson as DPRResponse;
        setAdvisoryMeta(advRes.advisory);
      }

      // Case B: If missing or directly requesting a DPR- prefix, call /api/advisory/dpr to synthesize
      if (!canonicalDPR) {
        const u = profRes?.user || {};
        const b = profRes?.business || {};
        const targetProgram = searchParams.get('programCode') || advRes?.advisory?.selectedProgramCode || 'PMEGP_NEW';

        const dprRes = await fetch('/api/advisory/dpr', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            district_name: b.district || u.district || 'Varanasi',
            state_name: b.state || u.state || 'Uttar Pradesh',
            business_type: b.sector || b.type || 'Handloom & Textiles',
            sub_type: b.description || 'Artisanal Manufacturing',
            estimated_capital: b.projectCost || b.estimatedCapital || 1200000,
            current_income: b.monthlyIncome ? b.monthlyIncome * 12 : 360000,
            selected_program_code: targetProgram,
            category: u.category || 'GENERAL',
            gender: u.gender || 'MALE',
          }),
        });

        if (dprRes.ok) {
          const dprData = await dprRes.json();
          canonicalDPR = dprData;
          setAdvisoryMeta({
            id: params.planId,
            planJson: dprData,
            business: b,
          });
        } else {
          throw new Error('Could not synthesize canonical Detailed Project Report.');
        }
      }

      setDpr(canonicalDPR);
    } catch (err: any) {
      console.error('Failed to load DPR:', err);
      setError(err.message || 'Error loading report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDPRData();
  }, [params.planId]);

  // Handle Regenerate DPR
  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const u = userProfile?.user || {};
      const b = userProfile?.business || {};
      const targetProgram = dpr?.government_support?.program_code || searchParams.get('programCode') || 'PMEGP_NEW';

      const dprRes = await fetch('/api/advisory/dpr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          district_name: dpr?.district_name || b.district || u.district || 'Varanasi',
          state_name: dpr?.state_name || b.state || u.state || 'Uttar Pradesh',
          business_type: dpr?.business_type || b.sector || b.type || 'Handloom & Textiles',
          sub_type: dpr?.sub_type || b.description,
          estimated_capital: dpr?.capital_structure?.total_project_cost || b.projectCost || 1200000,
          current_income: b.monthlyIncome ? b.monthlyIncome * 12 : 360000,
          selected_program_code: targetProgram,
          category: u.category || 'GENERAL',
          gender: u.gender || 'MALE',
        }),
      });

      if (dprRes.ok) {
        const freshDPR = await dprRes.json();
        setDpr(freshDPR);
      }
    } catch (err) {
      console.warn('Regeneration failed:', err);
    } finally {
      setRegenerating(false);
    }
  };

  // Handle Official DPR PDF Download
  const handleDownloadPDF = async () => {
    if (!dpr) return;
    setDownloadingPdf(true);
    try {
      const res = await fetch('/api/advisory/dpr/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dpr),
      });
      if (!res.ok) {
        throw new Error(`Failed to export PDF: ${res.statusText}`);
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `DPR_${dpr.report_id || 'REPORT'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      console.error('PDF download error:', err);
      alert('Could not download official PDF. Please try again or use Print / Save PDF.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  // --------------------------------------------------------------------------
  // Data Visualizations preparation
  // --------------------------------------------------------------------------

  // 1. Enterprise Scale Breakdown (MSME Census)
  const enterpriseScaleData = useMemo(() => {
    if (!dpr?.market_analysis) return [];
    const ma = dpr.market_analysis;
    const total = ma.total_msmes_in_district || 1;
    const microCount = Math.round(total * (ma.micro_enterprise_share / 100));
    const smallMediumCount = total - microCount;
    return [
      {
        tier: 'Micro Scale',
        count: microCount,
        share: ma.micro_enterprise_share,
        color: '#159A68',
      },
      {
        tier: 'Small & Medium',
        count: smallMediumCount,
        share: ma.small_medium_share,
        color: '#0B1736',
      },
    ];
  }, [dpr?.market_analysis]);

  // 2. NearestNeighbors Proximity Metric (Standardized Euclidean distance)
  const comparableDistrictsData = useMemo(() => {
    if (!dpr?.market_analysis?.comparable_districts) return [];
    return dpr.market_analysis.comparable_districts.map((cd: ComparableDistrictItem) => ({
      name: `${cd.district_name} (${cd.state_name.substring(0, 8)})`,
      distance: Number(cd.similarity_distance.toFixed(2)),
      rank: cd.similarity_rank,
      archetype: cd.cluster_label || 'Comparable',
      note: cd.qualitative_observation,
    }));
  }, [dpr?.market_analysis?.comparable_districts]);

  // 3. Capital Structure Donut Chart (Authoritative Only)
  const capitalDonutData = useMemo(() => {
    if (!dpr?.capital_structure) return { slices: [], isPartial: false };
    const cs = dpr.capital_structure;
    const slices: Array<{ name: string; value: number; color: string; note: string }> = [];

    // Promoter Equity (preserve null if None)
    if (cs.promoter_equity_amount != null && cs.promoter_equity_amount > 0) {
      slices.push({
        name: 'Promoter Equity',
        value: cs.promoter_equity_amount,
        color: '#0B1736',
        note: cs.promoter_equity_pct != null ? `${cs.promoter_equity_pct}% contribution` : 'Self-Financed',
      });
    }

    // Government Subsidy
    if (cs.government_subsidy_amount != null && cs.government_subsidy_amount > 0) {
      slices.push({
        name: 'Govt Subsidy / Support',
        value: cs.government_subsidy_amount,
        color: '#159A68',
        note: cs.government_subsidy_pct != null ? `${cs.government_subsidy_pct}% Margin Grant` : 'Statutory Grant',
      });
    }

    // Net Bank Loan Exposure
    const netDebt = cs.net_bank_loan_exposure ?? cs.initial_bank_loan;
    if (netDebt != null && netDebt > 0) {
      slices.push({
        name: 'Net Bank Loan',
        value: netDebt,
        color: '#F4A340',
        note: 'Credit facility exposure',
      });
    }

    // If total slices don't equal total project cost, it's a partial authoritative allocation
    const allocatedSum = slices.reduce((acc, s) => acc + s.value, 0);
    const isPartial = cs.promoter_equity_amount == null || Math.abs(allocatedSum - cs.total_project_cost) > 10;

    return { slices, isPartial };
  }, [dpr?.capital_structure]);

  // 4. Amortization Schedule Chart (Annual Debt Service)
  const amortizationChartData = useMemo(() => {
    if (!dpr?.financial_assumptions?.amortization_schedule) return [];
    return dpr.financial_assumptions.amortization_schedule.map((entry) => ({
      year: `Yr ${entry.year}`,
      openingBalance: entry.opening_balance,
      principal: entry.annual_principal,
      interest: entry.annual_interest,
      totalPayment: entry.total_annual_payment,
      closingBalance: entry.closing_balance,
    }));
  }, [dpr?.financial_assumptions?.amortization_schedule]);

  // Scroll to section helper
  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-[#64748B] gap-3">
          <Loader2 className="w-9 h-9 text-[#159A68] animate-spin" />
          <span className="text-sm font-semibold text-[#0B1736]">Synthesizing Official Detailed Project Report (DPR)...</span>
          <span className="text-xs text-[#64748B]">Grounded in 785-district census, scikit-learn ML & statutory rules</span>
        </div>
      </div>
    );
  }

  if (error || !dpr) {
    return (
      <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center p-8">
          <div className="bg-white p-8 rounded-2xl border border-red-200 text-center max-w-md shadow-xs space-y-3">
            <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
            <h2 className="text-base font-bold text-[#0B1736]">Failed to Load Detailed Project Report</h2>
            <p className="text-xs text-[#64748B]">{error || 'Unable to retrieve canonical DPR data.'}</p>
            <button
              onClick={loadDPRData}
              className="px-4 py-2 bg-[#159A68] hover:bg-[#128357] text-white font-bold text-xs rounded-xl transition"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const cs = dpr.capital_structure;
  const fa = dpr.financial_assumptions;
  const ma = dpr.market_analysis;
  const gs = dpr.government_support;
  const ra = dpr.risk_analysis;
  const ia = dpr.illustrative_assumptions;

  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col font-sans text-[#0B1736] antialiased">
      {/* Navbar (Hidden during printing) */}
      <div className="print:hidden">
        <Navbar />
      </div>

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        {/* Sidebar (Hidden during printing) */}
        <div className="print:hidden">
          <Sidebar />
        </div>

        <main className="flex-1 p-4 md:p-6 lg:p-8 space-y-6 w-full max-w-5xl mx-auto">
          
          {/* ------------------------------------------------------------- */}
          {/* Action Header & Breadcrumb (Screen Only) */}
          {/* ------------------------------------------------------------- */}
          <div className="print:hidden flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-[#E2E8F0] shadow-xs">
            <div className="text-xs text-[#64748B]">
              <span className="text-slate-400">Advisory / Business Plan / </span>
              <span className="font-mono font-bold text-[#0B1736]">{dpr.report_id}</span>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <Link
                href={`/advisory/business-plan?edit=true&planId=${params.planId}`}
                className="px-3.5 py-1.5 rounded-xl border border-[#E2E8F0] hover:bg-[#F8FAFC] text-[#0B1736] text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <Edit3 className="w-3.5 h-3.5 text-[#64748B]" />
                <span>Edit Profile / Narrative</span>
              </Link>

              <button
                type="button"
                onClick={handleRegenerate}
                disabled={regenerating}
                className="px-3.5 py-1.5 rounded-xl border border-[#E2E8F0] hover:bg-[#F8FAFC] text-[#0B1736] text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 text-[#64748B] ${regenerating ? 'animate-spin' : ''}`} />
                <span>{regenerating ? 'Regenerating...' : 'Regenerate'}</span>
              </button>

              <button
                type="button"
                onClick={() => window.print()}
                className="px-3.5 py-1.5 rounded-xl bg-[#0B1736] hover:bg-[#132247] text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-xs"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print / Save PDF</span>
              </button>

              <button
                type="button"
                onClick={handleDownloadPDF}
                disabled={downloadingPdf}
                className="px-3.5 py-1.5 rounded-xl bg-[#159A68] hover:bg-[#128357] text-white text-xs font-bold flex items-center gap-1.5 transition shadow-xs disabled:opacity-50"
              >
                <Download className={`w-3.5 h-3.5 ${downloadingPdf ? 'animate-bounce' : ''}`} />
                <span>{downloadingPdf ? 'Generating PDF...' : 'Download PDF'}</span>
              </button>

              <button
                type="button"
                onClick={() => setShareOpen(true)}
                className="px-3.5 py-1.5 rounded-xl border border-[#159A68]/30 bg-[#EAF7F0] hover:bg-[#ddf3e7] text-[#159A68] text-xs font-bold flex items-center gap-1.5 transition shadow-xs"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Share Report</span>
              </button>
            </div>
          </div>

          {/* ------------------------------------------------------------- */}
          {/* Executive Header Banner */}
          {/* ------------------------------------------------------------- */}
          <div className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-6">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-[#E2E8F0] pb-6">
              <div className="flex items-start gap-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/logo.png" alt="UnnatE" className="h-12 w-auto object-contain shrink-0 hidden sm:block mt-1" />
                <div className="space-y-1.5">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#EAF7F0] text-[#159A68] rounded-full text-[10px] font-bold uppercase tracking-wider border border-[#159A68]/20">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#159A68]" />
                    <span>Official Detailed Project Report (DPR) • Bank & Ministry Ready</span>
                  </div>
                  <h1 className="text-2xl md:text-3xl font-black text-[#0B1736] tracking-tight capitalize">
                    {dpr.project_name}
                  </h1>
                <p className="text-xs text-[#64748B]">
                  Promoter: <span className="font-semibold text-[#0B1736]">{dpr.promoter_name}</span> • Sector:{' '}
                  <span className="font-semibold text-[#0B1736]">{dpr.business_type}</span>{' '}
                  {dpr.sub_type && <span className="text-[#64748B]/70">({dpr.sub_type})</span>} • Location:{' '}
                  <span className="font-semibold text-[#0B1736]">
                    {dpr.district_name}, {dpr.state_name}
                  </span>{' '}
                  • Stage: <span className="font-semibold text-[#159A68]">Greenfield Formulation</span>
                </p>
              </div>
            </div>

            <div className="bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0] text-right shrink-0">
                <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider">Report Authority</span>
                <div className="text-xs font-extrabold text-[#0B1736] mt-0.5">UnnatE Advisory System</div>
                <div className="text-[10px] font-mono text-[#64748B]">{dpr.report_id}</div>
              </div>
            </div>

            {/* 5 Executive KPI Highlights with Clear Provenance */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {/* KPI 1: MRI */}
              <div className="p-3.5 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-[#64748B] uppercase">MRI Score</span>
                    <ProvenanceBadge tag="MODELLED INDICATOR" />
                  </div>
                  <div className="text-xl font-black text-[#0B1736]">
                    {ma.market_research_indicator.toFixed(1)} <span className="text-xs text-[#64748B] font-normal">/ 100</span>
                  </div>
                </div>
                <div className="text-[10px] text-[#64748B] mt-2">40% Nat • 30% State • 30% SME</div>
              </div>

              {/* KPI 2: Market Archetype */}
              <div className="p-3.5 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-[#64748B] uppercase">ML Archetype</span>
                    <ProvenanceBadge tag="MODELLED INDICATOR" />
                  </div>
                  <div className="text-xs font-black text-[#0B1736] leading-tight">
                    {ma.cluster_archetype_label}
                  </div>
                </div>
                <div className="text-[10px] text-[#64748B] mt-2">KMeans (k=4) fitted</div>
              </div>

              {/* KPI 3: Recommended Scheme */}
              <div className="p-3.5 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-[#64748B] uppercase">Scheme</span>
                    <ProvenanceBadge tag="GOVERNMENT / DATASET DERIVED" />
                  </div>
                  <div className="text-xs font-black text-[#0B1736] truncate" title={gs.program_name}>
                    {gs.program_code}
                  </div>
                </div>
                <div className="text-[10px] text-[#64748B] mt-2 truncate">{gs.program_name}</div>
              </div>

              {/* KPI 4: Project Cost */}
              <div className="p-3.5 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-[#64748B] uppercase">Project Cost</span>
                    <ProvenanceBadge tag="USER PROVIDED" />
                  </div>
                  <div className="text-lg font-black text-[#0B1736]">
                    ₹{cs.total_project_cost.toLocaleString('en-IN')}
                  </div>
                </div>
                <div className="text-[10px] text-[#64748B] mt-2">Formulation Budget</div>
              </div>

              {/* KPI 5: Net Effective Debt */}
              <div className="p-3.5 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex flex-col justify-between col-span-2 md:col-span-1">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-[#64748B] uppercase">Net Debt</span>
                    <ProvenanceBadge tag="BACKEND DETERMINISTIC CALCULATION" />
                  </div>
                  <div className="text-lg font-black text-[#D97706]">
                    {gs.is_credit_linked
                      ? cs.net_bank_loan_exposure != null
                        ? `₹${cs.net_bank_loan_exposure.toLocaleString('en-IN')}`
                        : 'Not Specified'
                      : 'N/A — Non-Credit'}
                  </div>
                </div>
                <div className="text-[10px] text-[#64748B] mt-2">
                  After ₹{cs.government_subsidy_amount.toLocaleString('en-IN')} Subsidy
                </div>
              </div>
            </div>
          </div>

          {/* ------------------------------------------------------------- */}
          {/* Section Navigation Strip (Sticky Screen Bar) */}
          {/* ------------------------------------------------------------- */}
          <div className="print:hidden sticky top-2 z-30 bg-white/95 backdrop-blur-md p-2 rounded-2xl border border-[#E2E8F0] shadow-xs overflow-x-auto">
            <div className="flex items-center gap-1.5 min-w-max text-xs font-semibold">
              <span className="text-[10px] uppercase font-bold text-[#64748B] px-2">Jump to:</span>
              {NAV_SECTIONS.map((sec) => (
                <button
                  key={sec.id}
                  onClick={() => scrollTo(sec.id)}
                  className="px-2.5 py-1 rounded-lg text-[#64748B] hover:text-[#159A68] hover:bg-[#EAF7F0] transition-colors text-[11px]"
                >
                  {sec.label}
                </button>
              ))}
            </div>
          </div>

          {/* ============================================================= */}
          {/* SECTION 1: Executive Summary */}
          {/* ============================================================= */}
          <section id="sec-exec" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  1
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Executive Summary</h2>
              </div>
              <ProvenanceBadge tag={dpr.executive_summary.provenance} />
            </div>

            {/* Quick Metrics Table */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border">
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Total Project Cost</span>
                <strong className="text-slate-900 text-sm">₹{cs.total_project_cost.toLocaleString('en-IN')}</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border">
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Statutory Scheme</span>
                <strong className="text-slate-900 text-sm truncate block" title={gs.program_name}>{gs.program_name}</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border">
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Capital Subsidy</span>
                <strong className="text-emerald-700 text-sm">
                  {cs.government_subsidy_amount > 0 ? `₹${cs.government_subsidy_amount.toLocaleString('en-IN')} (${cs.government_subsidy_pct}%)` : 'Not Applicable'}
                </strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border">
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Indicative Monthly EMI</span>
                <strong className="text-purple-700 text-sm">
                  {fa.monthly_emi > 0 ? `₹${fa.monthly_emi.toLocaleString('en-IN')}` : 'None (Non-Credit)'}
                </strong>
              </div>
            </div>

            <div className="pt-2">
              <h3 className="text-xs font-bold text-slate-900 uppercase mb-1.5">Executive Strategic Narrative</h3>
              <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line bg-slate-50/70 p-4 rounded-xl border border-slate-200">
                {dpr.executive_summary.executive_narrative}
              </p>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 2: Business Model & Value Proposition */}
          {/* ============================================================= */}
          <section id="sec-model" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  2
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Business Model & Value Proposition</h2>
              </div>
              <ProvenanceBadge tag={dpr.business_model.provenance} />
            </div>

            {/* Value Proposition Callout */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/80">
              <span className="text-[10px] font-bold text-blue-900 uppercase tracking-wider block mb-1">
                Core Value Proposition
              </span>
              <p className="text-xs text-blue-950 font-medium leading-relaxed">
                {dpr.business_model.value_proposition}
              </p>
            </div>

            {/* 4 Dimension Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-slate-900">
                  <Users className="w-4 h-4 text-blue-600" />
                  <span>Target Customer Segments</span>
                </div>
                <p className="text-slate-600 leading-relaxed">{dpr.business_model.target_segments_summary}</p>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-slate-900">
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                  <span>Primary Revenue Streams</span>
                </div>
                <ul className="space-y-1 text-slate-600">
                  {dpr.business_model.revenue_streams.map((rev, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{rev}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-slate-900">
                  <Briefcase className="w-4 h-4 text-indigo-600" />
                  <span>Key Operational Activities</span>
                </div>
                <ul className="space-y-1 text-slate-600">
                  {dpr.business_model.key_activities.map((act, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-indigo-500 font-bold">•</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold text-slate-900">
                  <BadgeIndianRupee className="w-4 h-4 text-amber-600" />
                  <span>Cost Drivers & Overheads</span>
                </div>
                <ul className="space-y-1 text-slate-600">
                  {dpr.business_model.cost_structure_summary.map((cost, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-amber-500 font-bold">•</span>
                      <span>{cost}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 3: Market Analysis & MSME Census */}
          {/* ============================================================= */}
          <section id="sec-market" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-6">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  3
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Market Analysis & District MSME Structure</h2>
              </div>
              <ProvenanceBadge tag={dpr.market_analysis.provenance} />
            </div>

            {/* A. District MSME Census Cards */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold text-slate-900 uppercase">A. Official District MSME Census (PostgreSQL)</h3>
                <span className="text-[10px] text-slate-400">785-District Official Udyam Records</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mb-4">
                <div className="p-3.5 bg-slate-50 rounded-2xl border">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Total Formal MSMEs</span>
                  <div className="text-lg font-black text-slate-900 mt-1">
                    {ma.total_msmes_in_district.toLocaleString('en-IN')}
                  </div>
                  <span className="text-[10px] text-slate-400">{dpr.district_name}, {dpr.state_name}</span>
                </div>

                <div className="p-3.5 bg-emerald-50/60 rounded-2xl border border-emerald-200">
                  <span className="text-[10px] font-bold text-emerald-800 uppercase">Micro Enterprises</span>
                  <div className="text-lg font-black text-emerald-900 mt-1">
                    {ma.micro_enterprise_share.toFixed(1)}%
                  </div>
                  <span className="text-[10px] text-emerald-700">Dominant artisanal tier</span>
                </div>

                <div className="p-3.5 bg-blue-50/60 rounded-2xl border border-blue-200">
                  <span className="text-[10px] font-bold text-blue-800 uppercase">Small & Medium MSMEs</span>
                  <div className="text-lg font-black text-blue-900 mt-1">
                    {ma.small_medium_share.toFixed(1)}%
                  </div>
                  <span className="text-[10px] text-blue-700">Formal SME depth</span>
                </div>

                <div className="p-3.5 bg-slate-50 rounded-2xl border">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">District Density Ranking</span>
                  <div className="text-base font-black text-slate-900 mt-1">
                    State #{ma.state_rank ?? '—'} • Nat #{ma.national_rank ?? '—'}
                  </div>
                  <span className="text-[10px] text-slate-400">of 785 Indian districts</span>
                </div>
              </div>

              {/* Composition Bar Chart */}
              <div className="bg-slate-50 p-4 rounded-2xl border space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-800">Enterprise Scale Composition</span>
                  <span className="text-[10px] text-slate-500">Udyam Distribution</span>
                </div>
                <div className="h-20 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart layout="vertical" data={enterpriseScaleData} margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                      <XAxis type="number" domain={[0, 100]} unit="%" fontSize={10} stroke="#94a3b8" />
                      <YAxis dataKey="tier" type="category" fontSize={10} stroke="#94a3b8" width={85} />
                      <Tooltip formatter={(val: any) => [`${val}% of district MSMEs`, 'Share']} />
                      <Bar dataKey="share" radius={[0, 6, 6, 0]}>
                        {enterpriseScaleData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* B & C. ML Market Classification & MRI */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* ML Classification */}
              <div className="p-4 rounded-2xl bg-slate-50 border space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-900 uppercase">B. ML Market Classification</h3>
                  <ProvenanceBadge tag="MODELLED INDICATOR" />
                </div>
                <div className="space-y-1">
                  <div className="inline-block px-2.5 py-0.5 rounded bg-purple-100 text-purple-900 font-bold text-xs">
                    Archetype: {ma.cluster_archetype_label}
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed pt-1">
                    {ma.cluster_archetype_description}
                  </p>
                </div>
                <div className="text-[10px] text-slate-400 pt-1 border-t">
                  Methodology: ML-derived market classification using unsupervised scikit-learn KMeans (k=4) fitted on 785 district profiles.
                </div>
              </div>

              {/* MRI Composite Score */}
              <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-emerald-950 uppercase">C. Market Research Indicator (MRI)</h3>
                  <span className="text-sm font-black text-emerald-900">
                    {ma.market_research_indicator.toFixed(1)} <span className="text-xs font-normal">/ 100</span>
                  </span>
                </div>
                <div className="w-full bg-emerald-200/60 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-emerald-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(100, Math.max(0, ma.market_research_indicator))}%` }}
                  />
                </div>
                <div className="grid grid-cols-3 gap-2 text-[10px] text-emerald-900 pt-1 text-center font-medium">
                  <div className="bg-white/80 p-1.5 rounded-lg border border-emerald-200">
                    <span className="block font-bold">40%</span> National Density
                  </div>
                  <div className="bg-white/80 p-1.5 rounded-lg border border-emerald-200">
                    <span className="block font-bold">30%</span> Intra-State
                  </div>
                  <div className="bg-white/80 p-1.5 rounded-lg border border-emerald-200">
                    <span className="block font-bold">30%</span> Formal SME Depth
                  </div>
                </div>
              </div>
            </div>

            {/* D. Comparable Markets (NearestNeighbors) */}
            <div className="p-5 rounded-2xl bg-slate-50 border space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 uppercase">
                    D. Comparable Markets (NearestNeighbors Distance)
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Comparable districts identified from MSME structural similarity across standardized feature space.
                  </p>
                </div>
                <ProvenanceBadge tag="MODELLED INDICATOR" />
              </div>

              {comparableDistrictsData.length > 0 ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {comparableDistrictsData.map((cd, i) => (
                      <div key={i} className="bg-white p-3.5 rounded-xl border text-xs space-y-1">
                        <div className="flex items-center justify-between font-bold">
                          <span className="text-slate-900">{cd.name}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-mono">
                            Rank #{cd.rank}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-500">
                          Euclidean Proximity Distance: <span className="font-mono font-semibold text-slate-800">{cd.distance}</span>
                        </div>
                        <div className="text-[10px] text-slate-600 bg-slate-50 p-2 rounded border mt-1">
                          {cd.note}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="text-[10px] text-slate-400 italic">
                    Note: Metrics reflect standardized Euclidean distances from the target district; zero percentage similarity claims are fabricated.
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-400 py-4 text-center">No comparable districts found.</div>
              )}
            </div>

            {/* E. Market Strategic Drivers & Barriers */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-2xl bg-emerald-50/50 border border-emerald-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-950 uppercase text-[11px]">Primary Demand Drivers</span>
                  <ProvenanceBadge tag="AI INTERPRETATION" />
                </div>
                <ul className="space-y-1.5 text-emerald-900">
                  {ma.demand_drivers.map((d, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-emerald-600 font-bold">•</span>
                      <span>{d}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-2xl bg-amber-50/50 border border-amber-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-950 uppercase text-[11px]">Market Barriers & Friction</span>
                  <ProvenanceBadge tag="AI INTERPRETATION" />
                </div>
                <ul className="space-y-1.5 text-amber-900">
                  {ma.market_barriers.map((b, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-amber-600 font-bold">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 4: Customer Segments */}
          {/* ============================================================= */}
          <section id="sec-customers" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  4
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Customer Segments & Demand Channels</h2>
              </div>
              <ProvenanceBadge tag={dpr.customer_segments.provenance} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {dpr.customer_segments.customer_segments.map((seg, i) => (
                <div key={i} className="p-4 bg-slate-50 rounded-2xl border text-xs space-y-2 flex flex-col justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between font-bold text-slate-900">
                      <span>{seg.segment}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-blue-100 text-blue-800 uppercase font-semibold">
                        Target Segment
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600"><span className="font-semibold text-slate-700">Need:</span> {seg.need}</p>
                  </div>
                  <div className="pt-2 border-t space-y-1 text-[11px]">
                    <div className="text-slate-600">
                      <span className="font-semibold text-slate-700">Buying Factor:</span> {seg.buying_consideration}
                    </div>
                    <div className="text-indigo-700 font-semibold flex items-center gap-1">
                      <ArrowRight className="w-3 h-3" />
                      <span>{seg.recommended_channel}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border text-xs">
              <span className="font-bold text-slate-900 block mb-1">Purchasing Behaviour & Demand Rhythms</span>
              <p className="text-slate-600 leading-relaxed">{dpr.customer_segments.buying_behaviour_summary}</p>
              <div className="text-[10px] text-slate-400 mt-2">
                Note: Segments describe functional commercial targets; zero customer counts or market share percentages fabricated.
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 5: Indicative Competition Assessment */}
          {/* ============================================================= */}
          <section id="sec-competition" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  5
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Indicative Competition Assessment</h2>
              </div>
              <ProvenanceBadge tag={dpr.competition.provenance} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Competitive Intensity</span>
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold text-xs">
                    {dpr.competition.competition_intensity}
                  </span>
                </div>
                <p className="text-slate-700 font-semibold">{dpr.competition.market_structure_type}</p>
                <p className="text-slate-600 leading-relaxed">{dpr.competition.competition_rationale}</p>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Differentiation Opportunities</span>
                <ul className="space-y-1.5 text-slate-700">
                  {dpr.competition.differentiation_vectors.map((diff, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{diff}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Field Validation Alert */}
            <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 text-xs text-amber-950 space-y-1">
              <div className="flex items-center gap-2 font-bold text-amber-900">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Field Validation Directives (Zero Competitor Counts Fabricated)</span>
              </div>
              <p className="text-amber-900 leading-relaxed pl-6">
                District MSME census numbers measure overall enterprise density, not direct competitors. The entrepreneur must conduct on-ground checks across local clusters:
              </p>
              <ul className="list-disc pl-10 space-y-0.5 text-amber-900">
                {dpr.competition.field_survey_gaps.map((gap, i) => (
                  <li key={i}>{gap}</li>
                ))}
              </ul>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 6: Location Analysis */}
          {/* ============================================================= */}
          <section id="sec-location" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  6
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Location Analysis & Infrastructure Suitability</h2>
              </div>
              <ProvenanceBadge tag={dpr.location_analysis.provenance} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Raw Material Proximity</span>
                <p className="font-semibold text-slate-900">{dpr.location_analysis.raw_material_proximity}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Labor Availability & Skills</span>
                <p className="font-semibold text-slate-900">{dpr.location_analysis.labor_availability}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Target District</span>
                <p className="font-semibold text-slate-900">{dpr.location_analysis.district_name}, {dpr.location_analysis.state_name}</p>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border text-xs space-y-2">
              <span className="font-bold text-slate-900 uppercase text-[11px] block">Transport & Logistics Connectivity Advantages</span>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-600">
                {dpr.location_analysis.connectivity_advantages.map((adv, i) => (
                  <li key={i} className="flex items-start gap-2 bg-white p-2.5 rounded-xl border">
                    <Truck className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                    <span>{adv}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 7: Operations & Production Plan */}
          {/* ============================================================= */}
          <section id="sec-operations" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  7
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Operations & Production Plan</h2>
              </div>
              <ProvenanceBadge tag={dpr.operations_plan.provenance} />
            </div>

            {/* Workflow sequence */}
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                Core Production & Commercial Workflow
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                {dpr.operations_plan.workflow_steps.map((step, i) => (
                  <div key={i} className="p-3 bg-slate-50 rounded-xl border text-xs flex items-center gap-2">
                    <div className="w-5 h-5 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-[10px] shrink-0">
                      {i + 1}
                    </div>
                    <span className="font-semibold text-slate-800">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Machinery, Utilities, Roles */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Key Machinery & Equipment</span>
                <ul className="space-y-1 text-slate-600">
                  {dpr.operations_plan.key_machinery_equipment.map((m, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-indigo-500 font-bold">•</span>
                      <span>{m}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Utilities & Power</span>
                <ul className="space-y-1 text-slate-600">
                  {dpr.operations_plan.utilities_and_power.map((u, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-amber-500 font-bold">•</span>
                      <span>{u}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Workforce & Roles</span>
                <ul className="space-y-1 text-slate-600">
                  {dpr.operations_plan.workforce_roles.map((w, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-blue-500 font-bold">•</span>
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Quality control */}
            <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 text-xs">
              <span className="font-bold text-emerald-950 uppercase text-[10px] block mb-1">Quality Assurance & Compliance</span>
              <p className="text-emerald-900">{dpr.operations_plan.quality_assurance}</p>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 8: Marketing & Distribution Strategy */}
          {/* ============================================================= */}
          <section id="sec-marketing" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  8
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Marketing & Distribution Strategy</h2>
              </div>
              <ProvenanceBadge tag={dpr.marketing_strategy.provenance} />
            </div>

            <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-200 text-xs">
              <span className="font-bold text-indigo-950 uppercase text-[10px] block mb-1">Positioning Statement</span>
              <p className="text-indigo-900 font-medium">{dpr.marketing_strategy.positioning_statement}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Sales & Distribution Channels</span>
                <ul className="space-y-1 text-slate-600">
                  {dpr.marketing_strategy.sales_channels.map((ch, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{ch}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Customer Acquisition</span>
                <ul className="space-y-1 text-slate-600">
                  {dpr.marketing_strategy.customer_acquisition_methods.map((ca, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-blue-500 font-bold">•</span>
                      <span>{ca}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Pricing Framework</span>
                <p className="text-slate-700">{dpr.marketing_strategy.pricing_framework}</p>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 9: Government Support */}
          {/* ============================================================= */}
          <section id="sec-govt" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  9
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Government Scheme Support & Statutory Eligibility</h2>
              </div>
              <ProvenanceBadge tag={gs.provenance} />
            </div>

            {/* Scheme banner */}
            <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                  {gs.program_code}
                </span>
                <h3 className="text-lg font-bold text-emerald-950 mt-1">{gs.program_name}</h3>
                <p className="text-xs text-emerald-800 mt-0.5">{gs.ministry} • Nodal: {gs.nodal_agency}</p>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="px-3 py-1.5 rounded-xl bg-white text-emerald-900 border border-emerald-200 text-xs font-bold shadow-sm">
                  {gs.is_credit_linked ? 'Credit-Linked' : 'Non-Credit Programme'}
                </span>
              </div>
            </div>

            {/* Subsidy details */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Eligible Subsidy Rate</span>
                <div className="text-base font-black text-emerald-700">
                  {gs.eligible_subsidy_rate_pct != null ? `${gs.eligible_subsidy_rate_pct}%` : 'N/A (Non-Subsidy)'}
                </div>
                <span className="text-[10px] text-slate-400">Statutory Margin Money Grant</span>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Eligible Subsidy Amount</span>
                <div className="text-base font-black text-emerald-700">
                  ₹{gs.eligible_subsidy_amount.toLocaleString('en-IN')}
                </div>
                <span className="text-[10px] text-slate-400">Deterministic allocation</span>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Maximum Subsidy Cap</span>
                <div className="text-base font-black text-slate-900">
                  {gs.max_subsidy_allowed != null ? `₹${gs.max_subsidy_allowed.toLocaleString('en-IN')}` : 'Statutory Ceiling'}
                </div>
                <span className="text-[10px] text-slate-400">Per programme gazette</span>
              </div>
            </div>

            {/* Criteria met & mandatory conditions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
                <span className="font-bold text-slate-900 uppercase text-[11px] block">Statutory Eligibility Criteria Met</span>
                <ul className="space-y-1.5 text-slate-600">
                  {gs.eligible_criteria_met.map((crit, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{crit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
                <span className="font-bold text-slate-900 uppercase text-[11px] block">Mandatory Programme Conditions</span>
                <ul className="space-y-1.5 text-slate-600">
                  {gs.mandatory_statutory_conditions.map((cond, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <Info className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                      <span>{cond}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 10: Capital Structure & Ring Donut Chart */}
          {/* ============================================================= */}
          <section id="sec-capital" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-6">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  10
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Authoritative Capital Structure & Debt Service</h2>
              </div>
              <ProvenanceBadge tag={cs.provenance} />
            </div>

            {/* Donut Chart + Slices Table */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
              {/* Donut Chart (5 cols) */}
              <div className="lg:col-span-5 bg-slate-50 p-4 rounded-2xl border flex flex-col items-center justify-center relative">
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Capital Allocation Donut</span>
                  {capitalDonutData.isPartial && (
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                      Partial authoritative allocation
                    </span>
                  )}
                </div>

                <div className="h-56 w-full relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={capitalDonutData.slices}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={3}
                      >
                        {capitalDonutData.slices.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: any) => [`₹${Number(value).toLocaleString('en-IN')}`, 'Amount']} />
                    </PieChart>
                  </ResponsiveContainer>
                  {/* Center of Donut text */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center">
                    <span className="text-[9px] font-bold text-slate-400 uppercase">Project Cost</span>
                    <span className="text-sm font-black text-slate-900">
                      ₹{cs.total_project_cost.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-[10px] text-slate-600 flex-wrap justify-center mt-2">
                  {capitalDonutData.slices.map((s, idx) => (
                    <div key={idx} className="flex items-center gap-1">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                      <span>{s.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Authoritative Financial Breakdown Table (7 cols) */}
              <div className="lg:col-span-7 space-y-3">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 bg-slate-50 rounded-xl border">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Total Project Cost</span>
                    <strong className="text-slate-900 text-base font-black">
                      ₹{cs.total_project_cost.toLocaleString('en-IN')}
                    </strong>
                    <div className="text-[10px] text-slate-400 mt-0.5">Authoritative base</div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Promoter Contribution</span>
                    {cs.promoter_equity_amount != null ? (
                      <>
                        <strong className="text-blue-700 text-base font-black">
                          ₹{cs.promoter_equity_amount.toLocaleString('en-IN')}
                        </strong>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          {cs.promoter_equity_pct != null ? `${cs.promoter_equity_pct}% margin` : 'Self-equity'}
                        </div>
                      </>
                    ) : (
                      <div className="text-[11px] text-amber-700 font-medium mt-1 leading-snug">
                        Not specified by authoritative programme data
                      </div>
                    )}
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Govt Subsidy</span>
                    <strong className="text-emerald-700 text-base font-black">
                      {cs.government_subsidy_amount > 0 ? `₹${cs.government_subsidy_amount.toLocaleString('en-IN')}` : 'None'}
                    </strong>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {cs.government_subsidy_pct ? `${cs.government_subsidy_pct}% Margin grant` : 'No subsidy'}
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Net Bank Loan</span>
                    <strong className="text-purple-700 text-base font-black">
                      {cs.net_bank_loan_exposure != null ? `₹${cs.net_bank_loan_exposure.toLocaleString('en-IN')}` : 'None'}
                    </strong>
                    <div className="text-[10px] text-slate-400 mt-0.5">Net effective debt</div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Initial Bank Loan</span>
                    <strong className="text-slate-700 text-base font-black">
                      {cs.initial_bank_loan != null ? `₹${cs.initial_bank_loan.toLocaleString('en-IN')}` : 'None'}
                    </strong>
                    <div className="text-[10px] text-slate-400 mt-0.5">Sanctioned facility</div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border">
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Term Loan / Working Capital</span>
                    <div className="text-[11px] text-slate-500 font-medium mt-1 leading-snug">
                      {cs.term_loan_amount != null
                        ? `TL: ₹${cs.term_loan_amount.toLocaleString('en-IN')} | WC: ₹${(cs.working_capital_amount || 0).toLocaleString('en-IN')}`
                        : 'Lender appraisal dependent'}
                    </div>
                  </div>
                </div>

                {/* Notice regarding Null promoter contribution */}
                {cs.promoter_equity_amount == null && (
                  <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-[11px] text-amber-900 flex items-start gap-2">
                    <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <span>
                      <strong>Promoter Contribution Notice:</strong> Authoritative scheme records for {gs.program_code} do not mandate a fixed statutory promoter margin. This value is preserved as null rather than fabricating a default 5% or 10% margin.
                    </span>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 11: Financial Assumptions & Amortization */}
          {/* ============================================================= */}
          <section id="sec-financials" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  11
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Financial Assumptions & Debt Service Schedule</h2>
              </div>
              <ProvenanceBadge tag={fa.provenance} />
            </div>

            {/* Benchmark interest rate card */}
            <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Applicable Interest Rate Benchmark
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800">
                  Indicative benchmark
                </span>
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="text-sm font-bold text-slate-900">
                  {fa.annual_interest_rate_pct != null
                    ? `${fa.annual_interest_rate_pct}% Market Benchmark`
                    : 'Not applicable — programme is not credit-linked.'}
                </div>
                <div className="text-xs text-slate-500 italic">
                  Market-linked / lender-dependent. Actual rate determined by lending institution.
                </div>
              </div>
            </div>

            {/* Loan Terms Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3.5 bg-slate-50 rounded-2xl border">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Monthly Equated EMI</span>
                <div className="text-lg font-black text-indigo-950 mt-1">
                  {fa.monthly_emi > 0 ? `₹${fa.monthly_emi.toLocaleString('en-IN')}` : 'None'}
                </div>
                <span className="text-[10px] text-slate-400">Monthly Debt Service</span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-2xl border">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Annual Debt Service</span>
                <div className="text-lg font-black text-indigo-950 mt-1">
                  {fa.annual_debt_service > 0 ? `₹${fa.annual_debt_service.toLocaleString('en-IN')}` : 'None'}
                </div>
                <span className="text-[10px] text-slate-400">12-Month Outflow</span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-2xl border">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Repayment Tenure</span>
                <div className="text-lg font-black text-slate-900 mt-1">
                  {fa.loan_tenure_months ? `${fa.loan_tenure_months} Months` : 'N/A'}
                </div>
                <span className="text-[10px] text-slate-400">Principal Amortization</span>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-2xl border">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Principal Moratorium</span>
                <div className="text-lg font-black text-slate-900 mt-1">
                  {fa.moratorium_months ? `${fa.moratorium_months} Months` : 'None'}
                </div>
                <span className="text-[10px] text-slate-400">Initial Grace Period</span>
              </div>
            </div>

            {/* Amortization Schedule Chart & Table */}
            {gs.is_credit_linked && amortizationChartData.length > 0 ? (
              <div className="space-y-4 pt-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-900 uppercase">
                    Authoritative Loan Amortization Schedule
                  </h3>
                  <span className="text-[10px] text-slate-400">Deterministic Equated Principal & Interest</span>
                </div>

                {/* Amortization Chart */}
                <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0]">
                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={amortizationChartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis dataKey="year" stroke="#64748B" fontSize={10} />
                        <YAxis stroke="#64748B" fontSize={10} tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`} />
                        <Tooltip formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Amount']} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                        <Bar dataKey="principal" name="Principal Paid" fill="#159A68" stackId="a" radius={[0, 0, 4, 4]} />
                        <Bar dataKey="interest" name="Interest Paid" fill="#F4A340" stackId="a" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Amortization Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border border-[#E2E8F0] rounded-xl overflow-hidden">
                    <thead className="bg-[#F8FAFC] text-[#64748B] font-bold uppercase text-[10px] border-b border-[#E2E8F0]">
                      <tr>
                        <th className="p-2.5">Period</th>
                        <th className="p-2.5 text-right">Opening Balance</th>
                        <th className="p-2.5 text-right">Principal Paid</th>
                        <th className="p-2.5 text-right">Interest Paid</th>
                        <th className="p-2.5 text-right">Annual Outflow</th>
                        <th className="p-2.5 text-right">Closing Balance</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                      {amortizationChartData.map((row, i) => (
                        <tr key={i} className="hover:bg-slate-50">
                          <td className="p-2.5 font-bold text-slate-800">{row.year}</td>
                          <td className="p-2.5 text-right text-slate-600">₹{row.openingBalance.toLocaleString('en-IN')}</td>
                          <td className="p-2.5 text-right text-blue-700 font-semibold">₹{row.principal.toLocaleString('en-IN')}</td>
                          <td className="p-2.5 text-right text-amber-700">₹{row.interest.toLocaleString('en-IN')}</td>
                          <td className="p-2.5 text-right font-bold text-slate-900">₹{row.totalPayment.toLocaleString('en-IN')}</td>
                          <td className="p-2.5 text-right text-slate-700 font-mono">₹{row.closingBalance.toLocaleString('en-IN')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-slate-50 border text-xs text-slate-600">
                <span className="font-bold text-slate-800 block mb-1">Non-Credit Linkage Notice</span>
                <p>Not applicable — programme is not credit-linked. Zero loan, interest rate, tenure, EMI, or amortization schedule fabricated.</p>
              </div>
            )}

            {/* Mandatory Illustrative Disclaimer */}
            <div className="p-4 rounded-2xl bg-orange-50/60 border border-orange-200 text-xs text-orange-950 flex items-start gap-2.5">
              <Info className="w-4 h-4 text-orange-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-orange-900 block mb-0.5">Illustrative Financial Assumptions</span>
                <p className="italic">"{ia.disclaimer}"</p>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 12: Risk Analysis & Climate Resilience */}
          {/* ============================================================= */}
          <section id="sec-risks" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-6">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  12
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Risk Analysis & Weather Activity Impact</h2>
              </div>
              <ProvenanceBadge tag={ra.provenance} />
            </div>

            {/* Dedicated Weather / Business Activity Intelligence Subsection */}
            <div className="p-5 rounded-2xl bg-slate-50 border space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-teal-600" />
                  <span className="text-xs font-bold text-slate-900 uppercase">
                    Weather / Business Activity Intelligence (Open-Meteo Centroid)
                  </span>
                </div>
                <ProvenanceBadge tag="MODELLED INDICATOR" />
              </div>

              {/* Weather Indicators Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-white rounded-xl border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Activity Score</span>
                  <div className="text-lg font-black text-teal-900 mt-0.5">
                    {ra.weather_activity_impact_score != null ? `${ra.weather_activity_impact_score.toFixed(1)} / 100` : 'Normal'}
                  </div>
                  <span className="text-[10px] text-teal-700 font-semibold">{ra.weather_activity_impact_label || 'Moderate Activity'}</span>
                </div>

                <div className="p-3 bg-white rounded-xl border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Heat Stress</span>
                  <div className="text-sm font-bold text-slate-800 mt-1">
                    {ra.heat_stress_level || 'Normal'}
                  </div>
                  <span className="text-[10px] text-slate-400">Threshold &gt; 38°C</span>
                </div>

                <div className="p-3 bg-white rounded-xl border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Rain Disruption</span>
                  <div className="text-sm font-bold text-slate-800 mt-1">
                    {ra.rain_disruption_level || 'None'}
                  </div>
                  <span className="text-[10px] text-slate-400">Precipitation signal</span>
                </div>

                <div className="p-3 bg-white rounded-xl border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Logistics Signal</span>
                  <div className="text-sm font-bold text-slate-800 mt-1">
                    {ra.logistics_disruption_level || 'Low Disruption'}
                  </div>
                  <span className="text-[10px] text-slate-400">Dispatch continuity</span>
                </div>
              </div>

              {/* Mandatory Weather Disclaimer */}
              <div className="p-3 rounded-xl bg-teal-50/70 border border-teal-200/80 text-[11px] text-teal-950 flex items-start gap-2">
                <Info className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" />
                <span>
                  <strong>Indicative Weather Activity Impact:</strong> Indicative weather impact on business activity — not observed footfall or a sales forecast. Zero customer counts or revenue impact fabricated.
                </span>
              </div>
            </div>

            {/* Operational Risk Matrix Table */}
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase mb-3">Operational & Financial Risk Matrix</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border rounded-xl overflow-hidden">
                  <thead className="bg-slate-100 text-slate-600 font-bold uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Risk Factor</th>
                      <th className="p-3 text-center">Severity</th>
                      <th className="p-3">Mitigation Strategy</th>
                      <th className="p-3 text-right">Provenance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {ra.identified_risks.map((r, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="p-3 font-bold text-slate-900">{r.risk}</td>
                        <td className="p-3 text-center">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            r.severity === 'High' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {r.severity}
                          </span>
                        </td>
                        <td className="p-3 text-slate-600 leading-relaxed">{r.mitigation}</td>
                        <td className="p-3 text-right">
                          <ProvenanceBadge tag="AI INTERPRETATION" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* SECTION 13: Implementation Plan */}
          {/* ============================================================= */}
          <section id="sec-implementation" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  13
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Project Implementation Roadmap (Months 1–6)</h2>
              </div>
              <ProvenanceBadge tag={dpr.implementation_plan.provenance} />
            </div>

            {/* Visual Milestones Stepper */}
            <div className="space-y-3">
              {dpr.implementation_plan.milestones.map((m) => (
                <div key={m.phase_number} className="p-4 bg-slate-50 rounded-2xl border flex items-start gap-4 text-xs">
                  <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                    M{m.phase_number}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between font-bold text-slate-900">
                      <span>{m.month_range}: {m.activity}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white border text-slate-600">
                        Phase {m.phase_number}
                      </span>
                    </div>
                    <p className="text-slate-600">
                      <span className="font-semibold text-slate-700">Critical Deliverable:</span> {m.critical_deliverable}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {dpr.implementation_plan.critical_path_notes.length > 0 && (
              <div className="p-4 bg-slate-50 rounded-2xl border text-xs space-y-1">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Critical Path Considerations</span>
                <ul className="space-y-1 text-slate-600">
                  {dpr.implementation_plan.critical_path_notes.map((note, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-indigo-500 font-bold">•</span>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {/* ============================================================= */}
          {/* AUXILIARY 14: Illustrative Operating Assumptions */}
          {/* ============================================================= */}
          <section id="sec-assumptions" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-orange-50 text-orange-700 flex items-center justify-center font-bold text-xs">
                  14
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Illustrative Operating Assumptions</h2>
              </div>
              <ProvenanceBadge tag={ia.provenance} />
            </div>

            <div className="p-4 rounded-2xl bg-orange-50/70 border border-orange-200 text-xs text-orange-950 space-y-2">
              <div className="flex items-center gap-2 font-bold text-orange-900">
                <AlertTriangle className="w-4 h-4 text-orange-600 shrink-0" />
                <span>Mandatory Zero-Fabrication Disclaimer</span>
              </div>
              <p className="italic font-medium pl-6">"{ia.disclaimer}"</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Working Capital Cycle & Break-Even</span>
                <p className="text-slate-700 font-semibold">Turnaround: {ia.working_capital_cycle_days} Days</p>
                <p className="text-slate-600">{ia.break_even_commentary}</p>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-1.5">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Capacity Utilization Schedule</span>
                <ul className="space-y-1 text-slate-600">
                  {ia.capacity_utilization_schedule.map((cap, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-orange-500 font-bold">•</span>
                      <span>{cap}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* AUXILIARY 15: Research Gaps & Field Validation Directives */}
          {/* ============================================================= */}
          <section id="sec-gaps" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  15
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Research Gaps & Field Validation Directives</h2>
              </div>
              <ProvenanceBadge tag={dpr.research_gaps.provenance} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Unorganized Sector Data Gaps</span>
                <ul className="space-y-1.5 text-slate-600">
                  {dpr.research_gaps.unorganized_data_gaps.map((gap, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-amber-500 font-bold">•</span>
                      <span>{gap}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border space-y-2">
                <span className="font-bold text-slate-900 uppercase text-[10px] block">Recommended Field Due Diligence</span>
                <ul className="space-y-1.5 text-slate-600">
                  {dpr.research_gaps.recommended_field_checks.map((chk, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{chk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* ============================================================= */}
          {/* AUXILIARY 16: Data Provenance & Audit Legend */}
          {/* ============================================================= */}
          <section id="sec-provenance" className="bg-white p-6 md:p-8 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#EAF7F0] text-[#159A68] flex items-center justify-center font-bold text-xs">
                  16
                </div>
                <h2 className="text-base font-bold text-slate-900 uppercase">Data Provenance Audit Trail (Zero-Fabrication Standard)</h2>
              </div>
              <ProvenanceBadge tag="STATUTORY AUDIT" />
            </div>

            <p className="text-xs text-slate-500">
              Every data point in this Detailed Project Report is strictly classified under one of the following authoritative provenance categories:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              {Object.entries(dpr.provenance_legend).map(([key, desc]) => (
                <div key={key} className="p-3.5 bg-slate-50 rounded-xl border flex items-start gap-3">
                  <ProvenanceBadge tag={key} />
                  <span className="text-[11px] text-slate-600 leading-snug">{desc}</span>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-2xl bg-slate-100 text-[11px] text-slate-500 leading-relaxed">
              <strong>Statutory Disclosure:</strong> {dpr.disclaimer}
            </div>
          </section>

        </main>
      </div>

      <ShareModal
        isOpen={shareOpen}
        onClose={() => setShareOpen(false)}
        businessId={advisoryMeta?.business?.id}
        advisoryId={advisoryMeta?.id}
      />
    </div>
  );
}
