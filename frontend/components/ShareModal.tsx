'use client';

import React, { useState } from 'react';
import { QrCode, Copy, Check, X, Share2, Loader2 } from 'lucide-react';

export default function ShareModal({
  isOpen,
  onClose,
  businessId,
  advisoryId
}: {
  isOpen: boolean;
  onClose: () => void;
  businessId: string;
  advisoryId?: string;
}) {
  const [loading, setLoading] = useState(false);
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const generateLink = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ businessId, advisoryId }),
      });
      const data = await res.json();
      if (data.shareUrl) setShareUrl(data.shareUrl);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xl max-w-md w-full relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-700">
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto mb-3">
            <Share2 className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-extrabold text-slate-900">Share Business Advisory DPR</h3>
          <p className="text-xs text-slate-500 mt-1">Generate a 7-day secure read-only link for bank officers or partners.</p>
        </div>

        {!shareUrl ? (
          <button
            onClick={generateLink}
            disabled={loading}
            className="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl shadow-sm transition-colors flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Generate 7-Day Share Link</span>}
          </button>
        ) : (
          <div className="space-y-4">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
              <input
                type="text"
                readOnly
                value={shareUrl}
                className="bg-transparent text-xs font-mono text-slate-700 w-full focus:outline-none"
              />
              <button
                onClick={copyToClipboard}
                className="ml-2 px-3 py-1.5 rounded-lg bg-emerald-700 text-white text-xs font-bold shrink-0 flex items-center gap-1"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>

            <div className="text-center bg-emerald-50 p-4 rounded-2xl border border-emerald-100">
              <div className="w-28 h-28 bg-white mx-auto rounded-xl p-2 shadow-sm border flex items-center justify-center">
                <QrCode className="w-24 h-24 text-slate-800" />
              </div>
              <p className="text-[11px] text-emerald-800 font-semibold mt-2">Scan QR Code to open DPR Report on Mobile</p>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
