'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { useLanguage } from '@/lib/i18n/useLanguage';
import { BadgeIndianRupee, Plus, Trash2, ArrowRight, Loader2, Building2, AlertCircle } from 'lucide-react';

function FinancialAdvisorForm() {
  const { t } = useLanguage();
  const router = useRouter();
  const searchParams = useSearchParams();

  const initialProgramId = searchParams.get('programId');
  const initialProgramCode = searchParams.get('programCode');
  const initialLoan = searchParams.get('loanNeeded');

  const [availablePrograms, setAvailablePrograms] = useState<any[]>([]);
  const [loadingPrograms, setLoadingPrograms] = useState(false);

  const [form, setForm] = useState({
    programId: initialProgramId ? parseInt(initialProgramId) : (undefined as number | undefined),
    programCode: initialProgramCode || '',
    monthlyIncome: 0,
    monthlyExpenses: 0,
    existingLoans: [] as { name: string; emi: number }[],
    creditHistory: 'Good Track Record',
    projectCost: initialLoan ? parseInt(initialLoan) : 0,
    loanNeeded: initialLoan ? parseInt(initialLoan) : 0,
    purpose: 'Equipment & Machinery Purchase',
    preferredTenure: 60,
    collateralAvailable: ['None (Collateral-Free MUDRA Coverage)'],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [profileLoaded, setProfileLoaded] = useState(false);

  // Load user business profile to pre-fill financial parameters
  useEffect(() => {
    fetch('/api/user/profile')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.business) {
          const b = data.business;
          const income = b.monthlyIncome || (b.annualIncome ? Math.round(b.annualIncome / 12) : 0);
          const expenses = b.monthlyExpenses || 0;
          const pCost = initialLoan ? parseInt(initialLoan) : (b.projectCost || b.estimatedCapital || 0);
          const lNeeded = initialLoan ? parseInt(initialLoan) : (b.requestedFinancing || b.projectCost || 0);
          const loans = b.existingMonthlyEmi && b.existingMonthlyEmi > 0
            ? [{ name: 'Existing Borrowings / EMI', emi: b.existingMonthlyEmi }]
            : [];

          setForm((prev) => ({
            ...prev,
            monthlyIncome: prev.monthlyIncome || income,
            monthlyExpenses: prev.monthlyExpenses || expenses,
            projectCost: prev.projectCost || pCost,
            loanNeeded: prev.loanNeeded || lNeeded,
            existingLoans: prev.existingLoans.length > 0 ? prev.existingLoans : loans,
          }));
        }
        setProfileLoaded(true);
      })
      .catch((e) => {
        console.warn('Could not load profile for financial advisor:', e);
        setProfileLoaded(true);
      });
  }, [initialLoan]);

  // Fetch available authoritative programmes to allow selection or switching
  useEffect(() => {
    setLoadingPrograms(true);
    fetch('/api/schemes?limit=60')
      .then((res) => res.json())
      .then((data) => {
        if (data.programs) {
          setAvailablePrograms(data.programs);
          // If no program selected from URL, default to first available program
          if (!form.programId && !form.programCode && data.programs.length > 0) {
            setForm((prev) => ({
              ...prev,
              programId: data.programs[0].id,
              programCode: data.programs[0].program_code,
            }));
          }
        }
      })
      .catch((e) => console.warn('Could not load programmes for selector:', e))
      .finally(() => setLoadingPrograms(false));
  }, []);

  const addLoan = () => {
    setForm({ ...form, existingLoans: [...form.existingLoans, { name: '', emi: 0 }] });
  };

  const removeLoan = (idx: number) => {
    const updated = form.existingLoans.filter((_, i) => i !== idx);
    setForm({ ...form, existingLoans: updated });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!form.programId && !form.programCode) {
      setError('Please select a target government programme to structure financing.');
      setLoading(false);
      return;
    }

    if (form.monthlyIncome <= 0) {
      setError('A valid monthly income greater than 0 is required for statutory debt serviceability evaluation.');
      setLoading(false);
      return;
    }

    if (form.projectCost <= 0) {
      setError('Total project cost greater than 0 is required for deterministic capital structuring.');
      setLoading(false);
      return;
    }

    try {
      const res = await fetch('/api/advisory/financial', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          projectCost: form.projectCost,
          loanNeeded: form.loanNeeded,
          programId: form.programId ? parseInt(form.programId.toString()) : undefined,
          programCode: form.programCode || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to generate financial advice');

      router.push(`/advisory/financial/${data.advisoryId}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectedProgramObj = availablePrograms.find(
    (p) => (form.programId && p.id === form.programId) || (form.programCode && p.program_code === form.programCode)
  );

  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 space-y-6">
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs max-w-3xl">
            <div className="flex items-center gap-3.5 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[#0B1736] text-[#F4A340] flex items-center justify-center shadow-xs">
                <BadgeIndianRupee className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-[#0B1736]">{t('advisory.financialAdvisor')}</h1>
                <p className="text-xs text-[#64748B]">
                  Deterministic statutory financial structuring: margin money, subsidy grants, risk guarantees, and affordable EMIs.
                </p>
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3.5 rounded-xl bg-red-50 text-red-700 text-xs font-semibold flex items-center gap-2 border border-red-200">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                <span>{error}</span>
              </div>
            )}

            {profileLoaded && (form.monthlyIncome <= 0 || form.projectCost <= 0) && (
              <div className="mb-4 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-amber-800">
                  <AlertCircle className="w-4 h-4 text-amber-600" />
                  Financial Parameters Needed
                </div>
                <p>
                  Statutory debt serviceability evaluation (FOIR / DSCR) and capital structuring require a verified monthly disposable income and total project cost. Enter them below or update your business profile.
                </p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Target Government Programme Selector */}
              <div className="bg-[#EEF4FA] p-4 rounded-xl border border-[#CBD5E1] space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-[#0B1736] flex items-center gap-1.5">
                    <Building2 className="w-4 h-4 text-[#159A68]" />
                    Target Government Assistance Programme
                  </label>
                  {form.programCode && (
                    <span className="px-2 py-0.5 rounded-full bg-white border border-[#CBD5E1] text-[#0B1736] text-[10px] font-bold font-mono">
                      {form.programCode}
                    </span>
                  )}
                </div>

                <select
                  required
                  value={form.programId || (selectedProgramObj ? selectedProgramObj.id : '')}
                  onChange={(e) => {
                    const pid = parseInt(e.target.value);
                    const prog = availablePrograms.find((p) => p.id === pid);
                    setForm({
                      ...form,
                      programId: pid,
                      programCode: prog ? prog.program_code : '',
                    });
                  }}
                  className="w-full px-3 py-2.5 rounded-xl border border-[#CBD5E1] text-xs font-semibold bg-white text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                >
                  {availablePrograms.length === 0 ? (
                    <option value="">{loadingPrograms ? 'Loading authoritative programmes...' : (form.programCode || 'Target Programme')}</option>
                  ) : (
                    availablePrograms.map((prog) => (
                      <option key={prog.id} value={prog.id}>
                        {prog.program_name} ({prog.program_code}) — {prog.primary_type}
                      </option>
                    ))
                  )}
                </select>

                {selectedProgramObj && (
                  <p className="text-[11px] text-[#475569] leading-snug">
                    {selectedProgramObj.benefit_summary || selectedProgramObj.description}
                  </p>
                )}
              </div>

              {/* Income & Expenses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">
                    {t('forms.currentIncome')} (₹ / Month) *
                  </label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={form.monthlyIncome || ''}
                    placeholder="e.g. 35000"
                    onChange={(e) => setForm({ ...form, monthlyIncome: parseInt(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-semibold text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                  <p className="text-[10px] text-[#94A3B8] mt-1">Monthly net operational surplus / household income</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Monthly Expenses (₹ / Month)</label>
                  <input
                    type="number"
                    min={0}
                    value={form.monthlyExpenses || ''}
                    placeholder="e.g. 15000"
                    onChange={(e) => setForm({ ...form, monthlyExpenses: parseInt(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-semibold text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                  <p className="text-[10px] text-[#94A3B8] mt-1">Living, household, and basic operational overheads</p>
                </div>
              </div>

              {/* Existing Loans Section */}
              <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0] space-y-3">
                <div className="flex justify-between items-center">
                  <div>
                    <label className="text-xs font-bold text-[#0B1736] block">Existing Debt Obligations</label>
                    <p className="text-[10px] text-[#64748B]">Active bank borrowings and monthly debt obligations</p>
                  </div>
                  <button
                    type="button"
                    onClick={addLoan}
                    className="text-xs font-semibold text-[#159A68] hover:text-[#128357] flex items-center gap-1 cursor-pointer transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Loan
                  </button>
                </div>

                {form.existingLoans.length === 0 ? (
                  <p className="text-xs text-[#94A3B8] italic py-1">No existing loans recorded. Click "Add Loan" if you have active borrowings.</p>
                ) : (
                  form.existingLoans.map((loan, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <input
                        type="text"
                        placeholder="Loan Name (e.g. Bike Loan)"
                        value={loan.name}
                        onChange={(e) => {
                          const updated = [...form.existingLoans];
                          updated[idx].name = e.target.value;
                          setForm({ ...form, existingLoans: updated });
                        }}
                        className="flex-1 px-3 py-2 rounded-xl border border-[#DCE3EA] text-xs text-[#0B1736]"
                      />
                      <input
                        type="number"
                        placeholder="Monthly EMI (₹)"
                        value={loan.emi || ''}
                        onChange={(e) => {
                          const updated = [...form.existingLoans];
                          updated[idx].emi = parseInt(e.target.value) || 0;
                          setForm({ ...form, existingLoans: updated });
                        }}
                        className="w-32 px-3 py-2 rounded-xl border border-[#DCE3EA] text-xs font-semibold text-[#0B1736]"
                      />
                      <button type="button" onClick={() => removeLoan(idx)} className="p-2 text-slate-400 hover:text-red-600 cursor-pointer">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>

              {/* Project Cost & Loan Needed */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Total Project Cost (₹) *</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={form.projectCost || ''}
                    placeholder="e.g. 500000"
                    onChange={(e) => setForm({ ...form, projectCost: parseInt(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-bold text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                  <p className="text-[10px] text-[#94A3B8] mt-1">Total capital expenditure + initial working capital</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Requested Loan Amount (₹) *</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={form.loanNeeded || ''}
                    placeholder="e.g. 400000"
                    onChange={(e) => setForm({ ...form, loanNeeded: parseInt(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-bold text-[#159A68] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                  <p className="text-[10px] text-[#94A3B8] mt-1">Statutory loan requirement (subject to promoter margin)</p>
                </div>
              </div>
              {/* Purpose of Loan */}
              <div>
                <label className="block text-xs font-semibold text-[#0B1736] mb-1">Purpose of Loan</label>
                <select
                  value={form.purpose}
                  onChange={(e) => setForm({ ...form, purpose: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-medium text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] bg-white transition-all"
                >
                  <option value="Equipment & Machinery Purchase">Equipment & Machinery Purchase</option>
                  <option value="Raw Material & Working Capital">Raw Material & Working Capital</option>
                  <option value="Livestock / Cattle Purchase">Livestock / Cattle Purchase</option>
                  <option value="New Business Setup">New Business Setup</option>
                </select>
              </div>

              {/* Credit History & Preferred Tenure */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Credit History</label>
                  <div className="space-y-1">
                    {['Good Track Record', 'No Prior Credit', 'Minor Overdues'].map((ch) => (
                      <label key={ch} className="flex items-center gap-2 text-xs text-[#334155] cursor-pointer">
                        <input
                          type="radio"
                          name="creditHistory"
                          checked={form.creditHistory === ch}
                          onChange={() => setForm({ ...form, creditHistory: ch })}
                          className="accent-[#159A68]"
                        />
                        <span>{ch}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Preferred Tenure</label>
                  <div className="flex gap-2">
                    {[36, 48, 60, 84].map((ten) => (
                      <button
                        key={ten}
                        type="button"
                        onClick={() => setForm({ ...form, preferredTenure: ten })}
                        className={`flex-1 py-2 rounded-xl text-xs font-semibold border transition-colors cursor-pointer ${
                          form.preferredTenure === ten ? 'bg-[#159A68] text-white border-[#159A68] shadow-xs' : 'bg-white text-[#475569] border-[#E2E8F0] hover:bg-[#F8FAFC]'
                        }`}
                      >
                        {ten} Mo
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-4 rounded-xl bg-[#0B1736] hover:bg-[#152347] text-white font-semibold text-sm shadow-xs transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>Structure Financing & Calculate Amortization <ArrowRight className="w-4 h-4 text-[#F4A340]" /></>}
              </button>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function FinancialAdvisorFormPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-100 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      }
    >
      <FinancialAdvisorForm />
    </Suspense>
  );
}
