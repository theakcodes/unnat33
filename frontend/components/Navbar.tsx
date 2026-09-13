'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useLanguage } from '@/lib/i18n/useLanguage';
import { useAppStore } from '@/lib/store';
import {
  Globe,
  LogOut,
  User as UserIcon,
  TrendingUp,
  ArrowRight,
  Menu,
  X,
  LayoutDashboard,
  Landmark,
  FileSpreadsheet,
  Bot,
  Building2,
  ChevronRight,
} from 'lucide-react';

export default function Navbar() {
  const { language, setLanguage, t } = useLanguage();
  const { user, logout } = useAppStore();
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    logout();
    router.push('/');
    setMobileMenuOpen(false);
  };

  const isAuthPage = pathname?.startsWith('/auth');
  const isDashboardOrAdvisory =
    pathname?.startsWith('/dashboard') ||
    pathname?.startsWith('/advisory') ||
    pathname?.startsWith('/chat');

  return (
    <header className="sticky top-0 z-50 w-full transition-all duration-300">
      <div
        className={`w-full bg-white/95 transition-all duration-300 border-b ${
          scrolled
            ? 'border-slate-200/90 shadow-sm backdrop-blur-md py-2.5'
            : 'border-slate-200/60 backdrop-blur-xs py-3.5'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
          {/* Brand Logo */}
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2.5 group shrink-0"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.png"
              alt="UnnatE - Business Grows A Stronger Bharat"
              className="h-10 sm:h-11 w-auto object-contain"
            />
            <span className="hidden sm:inline-flex text-[9px] font-bold text-[#159A68] bg-[#EAF6F0] px-1.5 py-0.5 rounded border border-[#159A68]/20 tracking-wider self-center">
              SIH26091
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          {!isAuthPage && !isDashboardOrAdvisory && (
            <nav className="hidden lg:flex items-center gap-7 text-xs font-semibold text-slate-700">
              <Link
                href="#how-it-works"
                className="hover:text-[#159A68] transition-colors py-1"
              >
                {t('nav.howItWorks')}
              </Link>
              <Link
                href="#analysis"
                className="hover:text-[#159A68] transition-colors py-1"
              >
                {t('nav.analysis')}
              </Link>
              <Link
                href="#entrepreneurs"
                className="hover:text-[#159A68] transition-colors py-1"
              >
                {t('nav.forEntrepreneurs')}
              </Link>
              <Link
                href="#about"
                className="hover:text-[#159A68] transition-colors py-1"
              >
                {t('nav.aboutUs')}
              </Link>
            </nav>
          )}

          {/* Right Action Controls */}
          <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
            {/* Bilingual Language Switcher Toggle */}
            <button
              onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 hover:text-slate-900 font-semibold text-xs transition-colors border border-slate-200 cursor-pointer"
              title="Switch Language / भाषा बदलें"
            >
              <Globe className="w-3.5 h-3.5 text-[#159A68]" />
              <span>{language === 'en' ? 'EN | हिन्दी' : 'हिन्दी | EN'}</span>
            </button>

            {user ? (
              <div className="hidden sm:flex items-center gap-2">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-[#0B1736] font-semibold text-xs transition-colors border border-slate-200"
                >
                  <UserIcon className="w-3.5 h-3.5 text-[#159A68]" />
                  <span className="max-w-[120px] truncate">{user.name}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer border border-transparent hover:border-rose-100"
                  title={t('nav.logout')}
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="hidden sm:flex items-center gap-2">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0B1736] hover:bg-[#159A68] text-white font-bold text-xs shadow-xs transition-colors group"
                >
                  <span>Explore Platform</span>
                  <ArrowRight className="w-3.5 h-3.5 text-white/80 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            )}

            {/* Mobile Menu Toggle Button */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 rounded-lg text-slate-700 hover:text-slate-900 hover:bg-slate-100 lg:hidden transition cursor-pointer border border-slate-200"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Dropdown Menu Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-slate-200 px-4 py-4 shadow-lg space-y-3">
          <nav className="space-y-1 text-xs font-semibold text-slate-700">
            {user ? (
              <>
                <div className="px-3 py-2 text-[11px] font-bold text-slate-900 bg-slate-50 rounded-lg mb-2 flex items-center justify-between border border-slate-200">
                  <div className="flex items-center gap-2">
                    <UserIcon className="w-3.5 h-3.5 text-[#159A68]" />
                    <span>{user.name}</span>
                  </div>
                  <span className="text-[10px] text-[#159A68] font-bold">Active</span>
                </div>
                <Link
                  href="/dashboard"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  <LayoutDashboard className="w-4 h-4 text-[#159A68]" />
                  <span>Dashboard</span>
                </Link>
                <Link
                  href="/dashboard/profile"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  <Building2 className="w-4 h-4 text-[#159A68]" />
                  <span>Business Profile</span>
                </Link>
                <Link
                  href="/advisory/schemes"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  <Landmark className="w-4 h-4 text-[#F4A340]" />
                  <span>Government Schemes</span>
                </Link>
                <Link
                  href="/advisory/business-plan"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  <FileSpreadsheet className="w-4 h-4 text-blue-600" />
                  <span>DPR Builder</span>
                </Link>
                <Link
                  href="/chat"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  <Bot className="w-4 h-4 text-purple-600" />
                  <span>AI Advisory Assistant</span>
                </Link>
                <div className="pt-2 border-t border-slate-100">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-rose-600 hover:bg-rose-50 transition text-left cursor-pointer"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Log Out</span>
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link
                  href="#how-it-works"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  {t('nav.howItWorks')}
                </Link>
                <Link
                  href="#analysis"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  {t('nav.analysis')}
                </Link>
                <Link
                  href="#entrepreneurs"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  {t('nav.forEntrepreneurs')}
                </Link>
                <Link
                  href="#about"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg hover:bg-slate-50 transition"
                >
                  {t('nav.aboutUs')}
                </Link>
                <Link
                  href="/dashboard"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block w-full py-2.5 px-4 rounded-lg bg-[#0B1736] text-white text-center font-bold shadow-xs mt-2"
                >
                  Explore Platform
                </Link>
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
