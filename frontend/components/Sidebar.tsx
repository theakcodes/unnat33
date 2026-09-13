'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLanguage } from '@/lib/i18n/useLanguage';
import {
  LayoutDashboard,
  Building2,
  BarChart3,
  Landmark,
  BadgeIndianRupee,
  FileSpreadsheet,
  FileText,
  Bot,
  Lightbulb,
} from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();
  const { t } = useLanguage();

  const menuItems = [
    { href: '/dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
    { href: '/dashboard/profile', label: t('nav.businessProfile'), icon: Building2 },
    { href: '/advisory/business-plan', label: t('nav.marketAnalysis'), icon: BarChart3 },
    { href: '/advisory/schemes', label: t('nav.governmentSchemes'), icon: Landmark },
    { href: '/advisory/financial', label: t('nav.financialOptions'), icon: BadgeIndianRupee },
    { href: '/advisory/business-plan', label: t('nav.dprBuilder'), icon: FileSpreadsheet },
    { href: '/dashboard', label: t('nav.insightsReports'), icon: FileText },
    { href: '/chat', label: t('nav.aiAdvisor'), icon: Bot },
  ];

  return (
    <aside className="w-64 lg:w-72 bg-white border-r border-slate-200/80 min-h-[calc(100vh-4.5rem)] p-4 lg:p-5 flex flex-col justify-between hidden md:flex shrink-0 select-none">
      <div className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Main Menu
        </div>
        <nav className="space-y-1" aria-label="Sidebar Navigation">
          {menuItems.map((item, idx) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={idx}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'bg-[#EAF7F0] text-[#159A68] font-bold border-l-[3px] border-[#159A68] rounded-r-xl rounded-l-none pl-3'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-[#0B1736] font-medium rounded-xl pl-3.5'
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    isActive ? 'text-[#159A68]' : 'text-slate-400 group-hover:text-slate-600'
                  }`}
                />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Need Guidance Widget */}
      <div className="mt-8 bg-[#FDF9F2] border border-amber-200/70 rounded-2xl p-4 text-center relative overflow-hidden">
        <div className="w-10 h-10 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center mx-auto mb-2 shadow-xs">
          <Lightbulb className="w-5 h-5 fill-amber-400 stroke-amber-700" />
        </div>
        <h4 className="text-xs font-bold text-[#0B1736] mb-1">{t('dashboard.needGuidance')}</h4>
        <p className="text-[11px] text-slate-500 mb-3 leading-relaxed">{t('dashboard.askAdvisor')}</p>
        <Link
          href="/chat"
          className="inline-flex items-center justify-center w-full py-2 px-3 rounded-lg bg-[#F4A340] hover:bg-[#E2922F] text-white font-bold text-xs shadow-xs transition-colors"
        >
          Ask AI Advisor
        </Link>
      </div>
    </aside>
  );
}
