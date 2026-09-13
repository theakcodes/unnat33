'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  TrendingUp,
  Plus,
  Award,
  CheckCircle,
  Loader2,
  Calendar
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';

export default function ProgressTrackerPage({ params }: { params: { id: string } }) {
  const { t } = useLanguage();
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    month: new Date().toISOString().substring(0, 7), // YYYY-MM
    actualIncome: 35000,
    actualExpense: 18000,
    notes: 'Good sales month, local Mandi demand increased.',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchComparison = async () => {
    try {
      const res = await fetch(`/api/progress/${params.id}/comparison`);
      const data = await res.json();
      setComparison(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparison();
  }, [params.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch(`/api/progress/${params.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (res.ok) {
        fetchComparison();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 space-y-6">
          
          <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs flex items-center justify-between">
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-[#0B1736]">Progress Tracker</h1>
              <p className="text-xs text-[#64748B]">Log monthly income & expenses to track performance against AI plan targets.</p>
            </div>
          </div>

          {/* Log New Month Form */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs max-w-3xl">
            <h3 className="text-sm font-bold text-[#0B1736] mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-[#159A68]" />
              Log Monthly Performance
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Month (YYYY-MM)</label>
                  <input
                    type="month"
                    required
                    value={form.month}
                    onChange={(e) => setForm({ ...form, month: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-semibold text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Actual Income (₹)</label>
                  <input
                    type="number"
                    required
                    value={form.actualIncome}
                    onChange={(e) => setForm({ ...form, actualIncome: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-semibold text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0B1736] mb-1">Actual Expense (₹)</label>
                  <input
                    type="number"
                    required
                    value={form.actualExpense}
                    onChange={(e) => setForm({ ...form, actualExpense: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-semibold text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#0B1736] mb-1">Notes (Optional)</label>
                <input
                  type="text"
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE3EA] text-xs font-medium text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
                  placeholder="e.g. Purchased 2 new cows, sales increased 15%"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="py-2.5 px-5 bg-[#159A68] hover:bg-[#128357] text-white font-semibold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                <span>Save Progress Log</span>
              </button>
            </form>
          </div>

          {/* Comparison Line Chart & Table */}
          {comparison?.chartData?.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-6">
              
              {/* Celebration Banner */}
              {comparison.chartData[comparison.chartData.length - 1]?.exceeded && (
                <div className="p-4 bg-gradient-to-r from-[#159A68] to-[#128357] text-white rounded-xl flex items-center gap-3 shadow-xs">
                  <Award className="w-8 h-8 text-[#F4A340] shrink-0" />
                  <div>
                    <h4 className="text-sm font-bold">Congratulations! You Exceeded Plan Targets 🎉</h4>
                    <p className="text-xs text-emerald-100">Your net profit for {comparison.chartData[comparison.chartData.length - 1].month} exceeded the planned target by 10%+.</p>
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-[#0B1736]">Plan vs. Actual Profit Comparison</h3>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={comparison.chartData}>
                    <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(v) => `₹${v/1000}k`} />
                    <Tooltip formatter={(val: any) => [`₹${val.toLocaleString('en-IN')}`, 'Amount']} />
                    <Legend />
                    <Line type="monotone" dataKey="actualProfit" name="Actual Profit" stroke="#159A68" strokeWidth={3} />
                    <Line type="monotone" dataKey="plannedProfit" name="Planned Target" stroke="#0B1736" strokeWidth={2} strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[#E2E8F0] text-[#64748B] font-semibold uppercase text-[10px]">
                      <th className="pb-3">Month</th>
                      <th className="pb-3">Actual Income</th>
                      <th className="pb-3">Actual Expense</th>
                      <th className="pb-3">Actual Net Profit</th>
                      <th className="pb-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F1F5F9] font-medium">
                    {comparison.chartData.map((row: any, i: number) => (
                      <tr key={i} className="hover:bg-[#F8FAFC]">
                        <td className="py-3 font-bold text-[#0B1736]">{row.month}</td>
                        <td className="py-3 text-[#159A68] font-semibold">₹{row.actualIncome.toLocaleString('en-IN')}</td>
                        <td className="py-3 text-[#D97706] font-semibold">₹{row.actualExpense.toLocaleString('en-IN')}</td>
                        <td className="py-3 font-bold text-[#0B1736]">₹{row.actualProfit.toLocaleString('en-IN')}</td>
                        <td className="py-3">
                          {row.exceeded ? (
                            <span className="px-2 py-0.5 rounded-full bg-[#EAF7F0] text-[#159A68] border border-[#159A68]/20 text-[10px] font-bold">Above Target</span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-full bg-[#FFF5DF] text-[#D97706] border border-[#FDE68A] text-[10px] font-bold">On Track</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          )}

        </main>
      </div>
    </div>
  );
}

