'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  Building2,
  TrendingUp,
  FileSpreadsheet,
  BadgeIndianRupee,
  Landmark,
  LineChart as LineChartIcon,
  Download,
  Share2,
  Loader2,
  Plus
} from 'lucide-react';

export default function BusinessDetailPage({ params }: { params: { id: string } }) {
  const { t } = useLanguage();
  const [business, setBusiness] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/businesses/${params.id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.business) setBusiness(data.business);
      })
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center p-8">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin" />
        </div>
      </div>
    );
  }

  if (!business) {
    return (
      <div className="min-h-screen bg-slate-100 flex flex-col">
        <Navbar />
        <div className="p-8 text-center text-slate-600">Business entity not found</div>
      </div>
    );
  }

  const latestAdvisory = business.advisories?.[0];

  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 space-y-6">
          
          {/* Header Card */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-xl bg-[#EAF7F0] text-[#159A68] flex items-center justify-center">
                  <Building2 className="w-5 h-5" />
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-[#0B1736] capitalize">{business.type} Business</h1>
                  <p className="text-xs text-[#64748B]">Created: {new Date(business.createdAt).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link
                href={`/dashboard/businesses/${business.id}/progress`}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0B1736] hover:bg-[#152347] text-white font-semibold text-xs shadow-xs transition-colors"
              >
                <LineChartIcon className="w-4 h-4 text-[#F4A340]" />
                <span>Progress Tracker</span>
              </Link>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex gap-2 border-b border-[#E2E8F0] pb-2">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'advisories', label: 'Generated Advisories' },
              { id: 'progress', label: 'Progress Logs' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  activeTab === tab.id ? 'bg-[#0B1736] text-white shadow-xs' : 'bg-white text-[#475569] border border-[#E2E8F0] hover:bg-[#F8FAFC]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Contents */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-xs">
                  <div className="text-xs font-semibold text-[#64748B]">Target Capital</div>
                  <div className="text-2xl font-bold text-[#0B1736] mt-1">₹{business.estimatedCapital?.toLocaleString('en-IN')}</div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-xs">
                  <div className="text-xs font-semibold text-[#64748B]">Target Monthly Income</div>
                  <div className="text-2xl font-bold text-[#159A68] mt-1">₹{business.targetMonthlyIncome?.toLocaleString('en-IN') || '50,000'}</div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-xs">
                  <div className="text-xs font-semibold text-[#64748B]">Advisories Count</div>
                  <div className="text-2xl font-bold text-[#0B1736] mt-1">{business.advisories?.length || 0}</div>
                </div>
              </div>

              {latestAdvisory && (
                <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-3">
                  <h3 className="text-sm font-bold text-[#0B1736]">Latest AI Advisory Report</h3>
                  <p className="text-xs text-[#475569]">{latestAdvisory.planJson?.executiveSummary}</p>
                  <Link
                    href={`/advisory/business-plan/${latestAdvisory.id}`}
                    className="inline-block text-xs font-semibold text-[#159A68] hover:underline"
                  >
                    View Full Plan & Financial Breakdown →
                  </Link>
                </div>
              )}
            </div>
          )}

          {activeTab === 'advisories' && (
            <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-4">
              <h3 className="text-sm font-bold text-[#0B1736]">Advisory History</h3>
              {business.advisories?.length === 0 ? (
                <p className="text-xs text-[#64748B]">No advisories generated yet.</p>
              ) : (
                <div className="space-y-3">
                  {business.advisories.map((ad: any, i: number) => (
                    <div key={i} className="p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex justify-between items-center text-xs">
                      <div>
                        <strong className="text-[#0B1736] uppercase font-bold">{ad.type} Advisory</strong>
                        <span className="text-[#64748B] block text-[11px]">{new Date(ad.createdAt).toLocaleString()}</span>
                      </div>
                      <Link
                        href={`/advisory/business-plan/${ad.id}`}
                        className="px-3.5 py-1.5 rounded-xl bg-[#EAF7F0] text-[#159A68] font-semibold hover:bg-[#D4EFE0] transition-colors"
                      >
                        Open Advisory
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'progress' && (
            <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-bold text-[#0B1736]">Monthly Progress Logs</h3>
                <Link
                  href={`/dashboard/businesses/${business.id}/progress`}
                  className="px-3.5 py-1.5 bg-[#159A68] hover:bg-[#128357] text-white font-semibold text-xs rounded-xl shadow-xs transition-colors"
                >
                  Log New Month
                </Link>
              </div>

              {business.progress?.length === 0 ? (
                <p className="text-xs text-[#64748B]">No monthly logs recorded yet.</p>
              ) : (
                <div className="space-y-2">
                  {business.progress?.map((p: any, i: number) => (
                    <div key={i} className="p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] flex justify-between text-xs">
                      <div>
                        <strong className="text-[#0B1736]">Month {p.monthNumber} ({p.year})</strong>
                        <span className="text-[#64748B] block">Revenue: ₹{p.actualRevenue?.toLocaleString('en-IN')} | Profit: ₹{p.actualProfit?.toLocaleString('en-IN')}</span>
                      </div>
                      <span className="text-[10px] text-[#94A3B8]">{new Date(p.createdAt).toLocaleDateString()}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
