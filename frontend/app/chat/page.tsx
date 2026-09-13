'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { useLanguage } from '@/lib/i18n/useLanguage';
import { useAppStore } from '@/lib/store';
import { Bot, Send, User, Sparkles, Loader2, Lightbulb } from 'lucide-react';

export default function ChatPage() {
  const { t, language } = useLanguage();
  const { user } = useAppStore();

  const [messages, setMessages] = useState<any[]>([
    {
      role: 'assistant',
      content: language === 'hi'
        ? `नमस्ते ${user?.name || 'उद्यमी'}! मैं आपका UnnatE AI व्यावसायिक सलाहकार हूँ। आप मुझसे अपने बिज़नेस प्लान, MUDRA ऋण आवेदन प्रक्रिया, या नया व्यवसाय शुरू करने के बारे में कुछ भी पूछ सकते हैं।`
        : `Hello ${user?.name || 'Entrepreneur'}! I am your UnnatE AI business advisor. Ask me anything about your business feasibility, starting a new business, MUDRA loan application steps, or government scheme eligibility.`
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const handleSend = async (textToSend?: string) => {
    const msg = textToSend || input;
    if (!msg.trim()) return;

    const newMsgs = [...messages, { role: 'user', content: msg }];
    setMessages(newMsgs);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msg,
          conversationId
        }),
      });

      const data = await res.json();
      if (data.chatId) setConversationId(data.chatId);
      if (data.message) {
        setMessages([...newMsgs, { role: 'assistant', content: data.message }]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = language === 'hi' ? [
    'नया व्यवसाय शुरू करने से पहले मुझे क्या जानना चाहिए?',
    'MUDRA लोन के लिए कौन से दस्तावेज़ चाहिए?',
    '5 लाख रुपये के लोन की मासिक EMI कितनी होगी?'
  ] : [
    'What shall I know before I start a business?',
    'What documents are needed for a MUDRA loan?',
    'What will be the monthly EMI for a ₹5 Lakh loan?'
  ];

  const renderFormattedContent = (content: string) => {
    if (!content) return null;
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      let formatted = line;
      const isHeading = line.startsWith('###');
      if (isHeading) {
        formatted = line.replace(/^###\s*/, '');
      }

      const parts = formatted.split(/(\*\*.*?\*\*)/g);
      const lineElements = parts.map((part, pIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={pIdx} className="font-extrabold text-slate-900">{part.slice(2, -2)}</strong>;
        }
        return part;
      });

      if (isHeading) {
        return (
          <div key={idx} className="text-sm font-black text-slate-900 mt-2 mb-1 border-b border-slate-200/80 pb-1">
            {lineElements}
          </div>
        );
      }

      return (
        <div key={idx} className={line.trim() === '' ? 'h-1.5' : ''}>
          {lineElements}
        </div>
      );
    });
  };

  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />

        <main className="flex-1 p-6 flex flex-col h-[calc(100vh-4rem)]">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xs flex-1 flex flex-col overflow-hidden">
            
            {/* Header */}
            <div className="p-4 border-b border-[#F1F5F9] flex items-center justify-between bg-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#0B1736] text-[#159A68] flex items-center justify-center shadow-xs">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h1 className="text-sm font-bold text-[#0B1736]">{t('nav.aiAdvisor')} Assistant</h1>
                  <p className="text-[11px] text-[#64748B]">Generative AI Rural Business Advisor • Multi-Model Intelligence</p>
                </div>
              </div>
            </div>

            {/* Messages Scroll Thread */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-[#F8FAFC]/50">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`flex gap-3 max-w-3xl ${m.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                      m.role === 'user' ? 'bg-[#0B1736] text-[#F4A340] border border-[#1E293B]' : 'bg-[#159A68] text-white'
                    }`}
                  >
                    {m.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <div
                    className={`p-4 rounded-2xl text-xs leading-relaxed shadow-xs ${
                      m.role === 'user'
                        ? 'bg-[#0B1736] text-white rounded-tr-none'
                        : 'bg-white text-[#334155] rounded-tl-none border border-[#E2E8F0]'
                    }`}
                  >
                    {renderFormattedContent(m.content)}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-3 mr-auto">
                  <div className="w-8 h-8 rounded-full bg-[#159A68] text-white flex items-center justify-center">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                  <div className="p-3 bg-white rounded-xl text-xs text-[#64748B] font-semibold border border-[#E2E8F0] shadow-xs animate-pulse">
                    Generative AI Advisor synthesizing response...
                  </div>
                </div>
              )}
            </div>

            {/* Quick Prompts (Preserving exact 3 prompts) */}
            <div className="px-4 py-2.5 border-t border-[#F1F5F9] bg-[#F8FAFC] flex flex-wrap gap-2">
              {quickPrompts.map((qp, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(qp)}
                  className="px-3 py-1.5 rounded-full bg-white border border-[#DCE3EA] text-[11px] font-semibold text-[#0B1736] hover:bg-[#EAF7F0] hover:border-[#159A68]/30 hover:text-[#159A68] transition-colors flex items-center gap-1.5 shadow-xs cursor-pointer"
                >
                  <Lightbulb className="w-3 h-3 text-[#D97706]" />
                  <span>{qp}</span>
                </button>
              ))}
            </div>

            {/* Input Box */}
            <form
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="p-4 border-t border-[#E2E8F0] flex gap-2 bg-white"
            >
              <input
                type="text"
                placeholder={language === 'hi' ? 'अपना प्रश्न यहाँ लिखें...' : 'Ask your business query here...'}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 px-4 py-2.5 rounded-xl border border-[#DCE3EA] text-xs text-[#0B1736] focus:outline-none focus:ring-2 focus:ring-[#159A68]/20 focus:border-[#159A68] transition-all"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-5 py-2.5 rounded-xl bg-[#159A68] hover:bg-[#128357] text-white font-semibold text-xs shadow-xs transition-colors flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>

          </div>
        </main>
      </div>
    </div>
  );
}
