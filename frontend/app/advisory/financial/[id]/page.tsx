'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  BadgeIndianRupee,
  ShieldCheck,
  CheckSquare,
  ArrowRight,
  Loader2,
  CheckCircle2,
  Sparkles,
  ChevronRight,
  AlertCircle,
  Building2,
  Check
} from 'lucide-react';

export default function FinancialResultsPage({ params }: { params: { id: string } }) {
  const { t } = useLanguage();
  const [advisory, setAdvisory] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/advisory/${params.id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.advisory) setAdvisory(data.advisory);
      })
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center p-8">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      </div>
    );
  }

  const fin = advisory?.financialJson || {};
  const structures = fin.structures || {};
  const capital = fin.capitalBreakdown;
  const warnings = fin.warnings || [];

  const promoterMarginPct = capital?.promoter_contribution_pct ?? null;
  const promoterMarginAmt = capital?.promoter_contribution_amount ?? null;
  const effectiveDebtAmt = capital?.net_effective_debt ?? capital?.initial_bank_loan ?? null;
  const hasSubsidy = capital?.subsidy_amount != null && capital.subsidy_amount > 0;
  const hasGuarantee = !!capital?.credit_guarantee_eligible;

  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 space-y-6">
          
          {/* Header & Key Financial Gauges */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-[#0B1736]">{t('advisory.financialAdvisor')} Results</h1>
                <p className="text-xs text-[#64748B]">
                  {fin.source || 'Deterministic financial structuring based on income, expenses, and statutory guidelines.'}
                </p>
              </div>
              <span className="px-3 py-1 rounded-full bg-[#EAF7F0] text-[#159A68] border border-[#159A68]/20 font-semibold text-xs">
                Risk Assessment: {fin.creditAssessment || 'Evaluated on sanction'}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* Debt to Income Gauge */}
              <div className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-[#64748B]">{t('advisory.debtToIncome')}</div>
                  <div className="text-2xl font-bold text-[#0B1736] mt-0.5">
                    {fin.debtToIncomeRatio != null ? `${fin.debtToIncomeRatio}%` : 'Not available'}
                  </div>
                  <div className="text-[11px] text-[#94A3B8] mt-1">Healthy statutory threshold: Below 40-50%</div>
                </div>
                <div className={`w-14 h-14 rounded-full border-4 flex items-center justify-center font-bold text-xs bg-white ${
                  fin.debtToIncomeRatio != null && fin.debtToIncomeRatio <= 40
                    ? 'border-[#159A68] text-[#159A68]'
                    : fin.debtToIncomeRatio != null
                    ? 'border-amber-500 text-amber-700'
                    : 'border-slate-300 text-slate-400'
                }`}>
                  {fin.debtToIncomeRatio != null ? (fin.debtToIncomeRatio <= 40 ? 'Good' : 'Stretched') : 'N/A'}
                </div>
              </div>

              {/* Affordable Monthly EMI */}
              <div className="p-4 bg-[#EAF7F0] rounded-xl border border-[#159A68]/20 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-[#159A68]">{t('advisory.affordableEMI')}</div>
                  <div className="text-2xl font-bold text-[#0B1736] mt-0.5">
                    {fin.affordableEMI != null ? `₹${fin.affordableEMI.toLocaleString('en-IN')} / mo` : 'Not available'}
                  </div>
                  <div className="text-[11px] text-[#159A68] mt-1">Dual-gate verified safe repayment capacity</div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-[#159A68] text-white flex items-center justify-center">
                  <BadgeIndianRupee className="w-6 h-6" />
                </div>
              </div>

            </div>

            {/* Authoritative Capital Stack & Margin Money Card */}
            <div className="p-5 bg-[#EEF4FA] rounded-xl border border-[#CBD5E1] space-y-3">
              <div className="flex justify-between items-center flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full bg-[#0B1736] text-white text-[10px] font-bold uppercase">
                    {fin.programName || 'Statutory Financial Structure'}
                  </span>
                  <h3 className="text-xs font-bold text-[#0B1736]">Authoritative Capital Stack & Margin Breakdown</h3>
                </div>
                <span className="text-xs font-semibold text-[#0B1736] bg-white px-2.5 py-1 rounded-lg shadow-xs border border-[#CBD5E1]">
                  {promoterMarginPct != null ? `${promoterMarginPct}% Margin : ${100 - promoterMarginPct}% Debt/Grant` : 'Statutory Capital Stack'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-white rounded-xl border border-[#E2E8F0]">
                  <div className="text-[11px] font-semibold text-[#64748B]">
                    {promoterMarginPct != null ? `${promoterMarginPct}% Beneficiary Margin Money` : 'Beneficiary Margin Money'}
                  </div>
                  <div className="text-lg font-bold text-[#0B1736] mt-0.5">
                    {promoterMarginAmt != null ? `₹${Math.round(promoterMarginAmt).toLocaleString('en-IN')}` : 'As per scheme rules'}
                  </div>
                  <div className="text-[10px] text-[#94A3B8]">
                    {capital?.is_statutory_margin ? 'Authoritative statutory equity rule' : 'Required self-contribution fraction'}
                  </div>
                </div>

                <div className="p-3 bg-white rounded-xl border border-[#E2E8F0]">
                  <div className="text-[11px] font-semibold text-[#0B1736]">Net Bank Debt Financing</div>
                  <div className="text-lg font-bold text-[#0B1736] mt-0.5">
                    {effectiveDebtAmt != null ? `₹${Math.round(effectiveDebtAmt).toLocaleString('en-IN')}` : 'Evaluated on sanction'}
                  </div>
                  <div className="text-[10px] text-[#64748B]">Funded via scheduled commercial bank loan</div>
                </div>

                {hasSubsidy && capital?.subsidy_amount != null ? (
                  <div className="p-3 bg-[#EAF7F0] rounded-xl border border-[#159A68]/30">
                    <div className="text-[11px] font-bold text-[#159A68]">Capital Subsidy / Grant</div>
                    <div className="text-lg font-bold text-[#0B1736] mt-0.5">₹{Math.round(capital.subsidy_amount).toLocaleString('en-IN')}</div>
                    <div className="text-[10px] text-[#159A68]">
                      {capital.subsidy_pct ? `${capital.subsidy_pct}% statutory grant` : 'Government back-ended subsidy'}
                    </div>
                  </div>
                ) : hasGuarantee ? (
                  <div className="p-3 bg-purple-50 rounded-xl border border-purple-200">
                    <div className="text-[11px] font-bold text-purple-800">Credit Guarantee Cover</div>
                    <div className="text-lg font-bold text-purple-900 mt-0.5">
                      {capital.guaranteed_amount != null ? `₹${Math.round(capital.guaranteed_amount).toLocaleString('en-IN')}` : 'Collateral-free risk coverage'}
                    </div>
                    <div className="text-[10px] text-purple-700">
                      {capital.guarantee_coverage_pct ? `${capital.guarantee_coverage_pct}% lender risk mitigation` : 'Lender risk coverage'}
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          {/* 3 Loan Structure Cards (Conservative, Balanced, Extended) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Conservative */}
            <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs flex flex-col justify-between">
              <div>
                <div className="text-xs font-semibold uppercase text-[#94A3B8]">{t('advisory.conservative')}</div>
                <div className="text-2xl font-bold text-[#0B1736] mt-2">
                  {structures.conservative?.monthlyEMI != null ? (
                    <>₹{structures.conservative.monthlyEMI.toLocaleString('en-IN')} <span className="text-xs font-normal text-[#94A3B8]">/mo</span></>
                  ) : (
                    <span className="text-sm font-semibold text-[#64748B]">Subject to terms</span>
                  )}
                </div>
                
                <div className="space-y-2 text-xs text-[#475569] mt-4 border-t border-[#F1F5F9] pt-4">
                  <div className="flex justify-between">
                    <span>Tenure:</span>
                    <strong className="text-[#0B1736]">
                      {structures.conservative?.tenureMonths != null ? `${structures.conservative.tenureMonths} Months` : 'Not specified'}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Interest Rate:</span>
                    <strong className="text-[#0B1736]">
                      {structures.conservative?.interestRate != null
                        ? `${structures.conservative.interestRate}% p.a.`
                        : (structures.conservative?.isMarketLinked ? 'Market-Linked' : (structures.conservative?.rateNote || 'Lender benchmark'))}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Interest:</span>
                    <strong className="text-[#0B1736]">
                      {structures.conservative?.totalInterest != null ? `₹${structures.conservative.totalInterest.toLocaleString('en-IN')}` : 'Calculated on sanction'}
                    </strong>
                  </div>
                </div>
              </div>
              <div className="mt-6 pt-3 border-t border-[#F1F5F9] text-[11px] font-semibold text-[#64748B] bg-[#F8FAFC] p-2.5 rounded-xl text-center">
                {structures.conservative?.feasibility || 'Fastest debt-free horizon'}
              </div>
            </div>

            {/* Balanced - Recommended */}
            <div className="bg-[#EAF7F0]/30 p-6 rounded-2xl border-2 border-[#159A68] shadow-xs flex flex-col justify-between relative">
              <div className="absolute -top-3 right-4 px-3 py-0.5 rounded-full bg-[#159A68] text-white font-bold text-[10px] uppercase tracking-wider">
                Recommended
              </div>

              <div>
                <div className="text-xs font-bold uppercase text-[#159A68]">{t('advisory.balanced')}</div>
                <div className="text-2xl font-bold text-[#0B1736] mt-2">
                  {structures.balanced?.monthlyEMI != null ? (
                    <>₹{structures.balanced.monthlyEMI.toLocaleString('en-IN')} <span className="text-xs font-normal text-[#94A3B8]">/mo</span></>
                  ) : (
                    <span className="text-sm font-semibold text-[#64748B]">Subject to terms</span>
                  )}
                </div>
                
                <div className="space-y-2 text-xs text-[#334155] mt-4 border-t border-[#159A68]/20 pt-4">
                  <div className="flex justify-between">
                    <span>Tenure:</span>
                    <strong className="text-[#0B1736]">
                      {structures.balanced?.tenureMonths != null ? `${structures.balanced.tenureMonths} Months` : 'Not specified'}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Interest Rate:</span>
                    <strong className="text-[#0B1736]">
                      {structures.balanced?.interestRate != null
                        ? `${structures.balanced.interestRate}% p.a.`
                        : (structures.balanced?.isMarketLinked ? 'Market-Linked' : (structures.balanced?.rateNote || 'Lender benchmark'))}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Interest:</span>
                    <strong className="text-[#0B1736]">
                      {structures.balanced?.totalInterest != null ? `₹${structures.balanced.totalInterest.toLocaleString('en-IN')}` : 'Calculated on sanction'}
                    </strong>
                  </div>
                </div>
              </div>
              <div className="mt-6 pt-3 border-t border-[#159A68]/20 text-[11px] font-bold text-[#159A68] bg-[#EAF7F0] p-2.5 rounded-xl text-center">
                {structures.balanced?.feasibility || 'Optimized Cashflow Balance'}
              </div>
            </div>

            {/* Extended */}
            <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs flex flex-col justify-between">
              <div>
                <div className="text-xs font-semibold uppercase text-[#94A3B8]">{t('advisory.extended')}</div>
                <div className="text-2xl font-bold text-[#0B1736] mt-2">
                  {structures.extended?.monthlyEMI != null ? (
                    <>₹{structures.extended.monthlyEMI.toLocaleString('en-IN')} <span className="text-xs font-normal text-[#94A3B8]">/mo</span></>
                  ) : (
                    <span className="text-sm font-semibold text-[#64748B]">Subject to terms</span>
                  )}
                </div>
                
                <div className="space-y-2 text-xs text-[#475569] mt-4 border-t border-[#F1F5F9] pt-4">
                  <div className="flex justify-between">
                    <span>Tenure:</span>
                    <strong className="text-[#0B1736]">
                      {structures.extended?.tenureMonths != null ? `${structures.extended.tenureMonths} Months` : 'Not specified'}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Interest Rate:</span>
                    <strong className="text-[#0B1736]">
                      {structures.extended?.interestRate != null
                        ? `${structures.extended.interestRate}% p.a.`
                        : (structures.extended?.isMarketLinked ? 'Market-Linked' : (structures.extended?.rateNote || 'Lender benchmark'))}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Interest:</span>
                    <strong className="text-[#0B1736]">
                      {structures.extended?.totalInterest != null ? `₹${structures.extended.totalInterest.toLocaleString('en-IN')}` : 'Calculated on sanction'}
                    </strong>
                  </div>
                </div>
              </div>
              <div className="mt-6 pt-3 border-t border-[#F1F5F9] text-[11px] font-semibold text-[#64748B] bg-[#F8FAFC] p-2.5 rounded-xl text-center">
                {structures.extended?.feasibility || 'Lowest Monthly Outflow'}
              </div>
            </div>

          </div>

          {/* Pre-Approval Document Checklist */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs">
            <h3 className="text-sm font-bold text-[#0B1736] mb-3 flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-[#159A68]" />
              Pre-Approval Required Documents Checklist
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {fin.preApprovalChecklist?.map((doc: string, idx: number) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0]">
                  <CheckCircle2 className="w-4 h-4 text-[#159A68] shrink-0" />
                  <span className="text-xs text-[#334155] font-medium">{doc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Statutory Warnings & Advisory Caveats */}
          {warnings.length > 0 && (
            <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-800 space-y-1">
              <div className="font-bold flex items-center gap-2 text-amber-900">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Underwriting & Regulatory Caveats</span>
              </div>
              <ul className="list-disc list-inside space-y-1 pl-1">
                {warnings.map((w: string, idx: number) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Next Steps CTA */}
          <div className="bg-[#0B1736] text-white p-6 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 border border-[#1E293B]">
            <div>
              <h3 className="text-base font-bold">Ready to apply for Government Loan / Subsidy?</h3>
              <p className="text-xs text-slate-300 mt-1">Explore matching government schemes with high approval rates in your district.</p>
            </div>

            <Link
              href="/advisory/schemes"
              className="px-6 py-3 rounded-xl bg-[#159A68] hover:bg-[#128357] text-white font-semibold text-xs transition-colors shrink-0 flex items-center gap-2 cursor-pointer shadow-xs"
            >
              <span>Match Schemes Now</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

        </main>
      </div>
    </div>
  );
}
