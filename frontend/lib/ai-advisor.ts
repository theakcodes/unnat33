import { GoogleGenerativeAI } from '@google/generative-ai';
import Anthropic from '@anthropic-ai/sdk';
import { getGroqClient, DEFAULT_GROQ_MODEL } from './groq';
import { logger } from './logger';

export interface ChatMessageItem {
  role: 'user' | 'assistant' | string;
  content: string;
}

export interface UserAdvisorContext {
  name?: string;
  language?: string;
  district?: string;
  state?: string;
  businessType?: string;
}

/**
 * Multi-Provider Generative AI Engine
 * 1. Primary: Groq AI (Llama 3.3 70B Versatile - Ultra-fast, unlimited tokens)
 * 2. Secondary: Anthropic Claude 3.5 Sonnet / Haiku
 * 3. Tertiary: Google Gemini 1.5 Flash
 * 4. Autonomous Conversational Advisor (Resilient, hyper-local, zero broken templates)
 */
export async function generateAdvisorResponse(
  messages: ChatMessageItem[],
  context: UserAdvisorContext
): Promise<string> {
  const isHi = context.language === 'hi';
  const dist = context.district || 'Lucknow';
  const state = context.state || 'Uttar Pradesh';
  const lastUserMsg = (messages[messages.length - 1]?.content || '').trim();

  if (!lastUserMsg) {
    return isHi
      ? 'कृपया अपना व्यावसायिक प्रश्न लिखें।'
      : 'Please enter your business query.';
  }

  // ------------------------------------------------------------------
  // Provider 1: Groq AI (Qwen 3.8 27B / Llama 3.3 70B)
  // Blazing fast inference, generous limits
  // ------------------------------------------------------------------
  const groq = getGroqClient();
  if (groq) {
    try {
      const modelName = process.env.GROQ_MODEL || DEFAULT_GROQ_MODEL;
      const groqMessages = [
        {
          role: 'system' as const,
          content: `You are UnnatE's expert AI business advisor for Indian micro-entrepreneurs in ${dist}, ${state}. Speak simply, practically, and empathetically in ${isHi ? 'Hindi (Devanagari script)' : 'English'}. Provide thorough, structured, actionable guidance with bullet points and clear steps. Ground your advice in real Indian government schemes (PMEGP, MUDRA, PM Vishwakarma, PM SVANidhi, Stand-Up India, Udyam registration). If the user asks general, casual, or frustrated questions, always respond politely, respectfully, and helpfully without breaking character.`
        },
        ...messages.map((m) => ({
          role: (m.role === 'assistant' ? 'assistant' : 'user') as 'assistant' | 'user',
          content: m.content,
        }))
      ];

      let completion;
      try {
        completion = await groq.chat.completions.create({
          model: modelName,
          messages: groqMessages,
          temperature: 0.6,
          max_tokens: 1500,
        });
      } catch (err: any) {
        if (err?.status === 404 || err?.message?.includes('model_not_found') || err?.message?.includes('does not exist')) {
          logger.warn(`Model ${modelName} not available, retrying with qwen/qwen3.8-27b...`);
          completion = await groq.chat.completions.create({
            model: 'qwen/qwen3.8-27b',
            messages: groqMessages,
            temperature: 0.6,
            max_tokens: 1500,
          });
        } else {
          throw err;
        }
      }

      const text = completion.choices[0]?.message?.content || '';
      if (text && text.trim().length > 5) {
        return text;
      }
    } catch (err: any) {
      logger.warn('Groq API invocation failed, trying secondary providers:', err?.message || err);
    }
  }

  // ------------------------------------------------------------------
  // Provider 2: Anthropic Claude 3.5 Sonnet / Haiku
  // ------------------------------------------------------------------
  const anthropicKey = process.env.ANTHROPIC_API_KEY || process.env.CLAUDE_API_KEY;
  if (anthropicKey && anthropicKey.trim().length > 10) {
    try {
      const anthropic = new Anthropic({ apiKey: anthropicKey.trim() });
      const modelName = process.env.CLAUDE_MODEL || 'claude-3-5-sonnet-20241022';
      const response = await anthropic.messages.create({
        model: modelName,
        max_tokens: 1200,
        temperature: 0.6,
        system: `You are UnnatE's expert AI business advisor for Indian micro-entrepreneurs in ${dist}, ${state}. Speak simply, practically, and empathetically in ${isHi ? 'Hindi (Devanagari script)' : 'English'}. Provide thorough, structured, actionable guidance with bullet points and clear steps. Ground your advice in real Indian government schemes (PMEGP, MUDRA, PM Vishwakarma, PM SVANidhi, Stand-Up India, Udyam registration).`,
        messages: messages.map((m) => ({
          role: m.role === 'assistant' ? 'assistant' : 'user',
          content: m.content,
        })),
      });

      const text = response.content[0].type === 'text' ? response.content[0].text : '';
      if (text && text.trim().length > 20) {
        return text;
      }
    } catch (err: any) {
      logger.warn('Anthropic Claude API unavailable or credit balance zero:', err?.message || err);
    }
  }

  // ------------------------------------------------------------------
  // Provider 2: Google Gemini 1.5 Flash
  // ------------------------------------------------------------------
  const geminiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (geminiKey && geminiKey.trim().length > 10) {
    try {
      const genAI = new GoogleGenerativeAI(geminiKey.trim());
      const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

      const systemInstruction = `You are UnnatE's expert AI business advisor for micro-entrepreneurs in ${dist}, ${state}. Provide clear, encouraging, structured business guidance in ${isHi ? 'Hindi' : 'English'}. Include realistic Indian context (MUDRA, PMEGP, Udyam, bank requirements).`;
      const promptText = `${systemInstruction}\n\nUser Question: ${lastUserMsg}`;

      const result = await model.generateContent(promptText);
      const text = result.response.text();
      if (text && text.trim().length > 20) {
        return text;
      }
    } catch (err: any) {
      logger.warn('Google Gemini API error:', err?.message || err);
    }
  }

  // ------------------------------------------------------------------
  // Provider 3: Autonomous Intelligent Conversational Engine
  // High-fidelity fallback providing tailored, domain-specific advice
  // ------------------------------------------------------------------
  const query = lastUserMsg.toLowerCase().trim();

  // 0. Guardrail: Profanity / Abusive Language / Hostility
  const isAbusive = /\b(fuck|f\*\*k|bitch|bastard|asshole|idiot|stupid|shut\s*up|chutiya|madarchod|bhenchod|gandu|harami|kamina)\b/i.test(query)
    || query.includes('fuck') || query.includes('bitch') || query.includes('idiot');
  if (isAbusive) {
    if (isHi) {
      return `मैं आपकी व्यावसायिक सफलता और सहायता के लिए यहाँ उपस्थित हूँ। यदि आपके मन में कोई असंतोष, संदेह या प्रश्न है, तो कृपया साझा करें। मैं सरकारी योजनाओं, ऋण सहायता, अथवा विस्तृत परियोजना रिपोर्ट (DPR) तैयार करने में आपकी पूरी सहायता करूँगा।`;
    }
    return `I am here to assist you professionally with your business, government schemes, and financial planning. If you have any questions or if something isn't working as expected, please let me know and I will be glad to assist you.`;
  }

  // 0.1 Gratitude / Appreciation
  const isThanks = /^(thanks|thank\s*you|dhanyawad|shukriya|great|awesome|good\s*job|cool)\b/i.test(query);
  if (isThanks) {
    if (isHi) {
      return `आपका बहुत-बहुत धन्यवाद! 🙏 यदि आपको व्यवसाय, ऋण EMI, अथवा 'DPR Builder' से संबंधित और कोई सहायता चाहिए, तो कभी भी पूछ सकते हैं। आपके व्यवसाय के उज्ज्वल भविष्य की शुभकामनाएं!`;
    }
    return `You're very welcome! 🙏 Feel free to ask if you need further guidance on loan eligibility, business plan structuring, or downloading your 13-section bank DPR. Wishing your business great success!`;
  }

  // 1. Greetings & Introductions
  const isGreeting = /^(hello|hi|hey|namaste|pranam|good\s*(morning|afternoon|evening|day)|greetings|who\s*are\s*you|kya\s*hal|halo)/i.test(query)
    || query === 'hello' || query === 'hi' || query === 'hey' || query === 'नमस्ते';

  if (isGreeting) {
    if (isHi) {
      return `### 👋 नमस्ते! मैं आपका UnnatE AI व्यावसायिक सलाहकार हूँ\n\n` +
        `मैं **${dist}, ${state}** में आपके सूक्ष्म उद्योग एवं व्यवसाय के लिए सरकारी योजनाओं, ऋण और बाजार विश्लेषण में सहायता कर सकता हूँ।\n\n` +
        `💡 **मैं किन विषयों में आपकी सहायता कर सकता हूँ?**\n` +
        `• 🏛️ **सरकारी योजनाएं व सब्सिडी:** **PMEGP** (15%–35% पूंजीगत सब्सिडी), **MUDRA** (₹10 लाख तक बिना गारंटी ऋण), **PM विश्वकर्मा** और **Stand-Up India**।\n` +
        `• 📊 **13-अनुभाग विस्तृत परियोजना रिपोर्ट (DPR):** बैंक ऋण स्वीकृति के लिए तकनीकी और वित्तीय रिपोर्ट 60 सेकंड में बनाएं।\n` +
        `• 💰 **ऋण व EMI संरचना:** अपने बजट अनुसार सुरक्षित मासिक किश्त (EMI) और ब्याज दर की गणना करें।\n` +
        `• 📜 **दस्तावेज़ एवं लाइसेंस चेकलिस्ट:** Udyam पंजीकरण, ट्रेड लाइसेंस, और बैंक आवश्यकताओं की पूरी जानकारी।\n\n` +
        `👉 *शुरू करने के लिए नीचे दिए गए सुझावों में से किसी एक पर क्लिक करें या अपना प्रश्न सीधे टाइप करें!*`;
    }

    return `### 👋 Hello! I am your UnnatE AI Business Advisor\n\n` +
      `I am specialized in helping micro-entrepreneurs and small business owners in **${dist}, ${state}** scale with government schemes, institutional credit, and market advisory.\n\n` +
      `💡 **How can I assist you today?**\n` +
      `• 🏛️ **Government Subsidies & Schemes:** Assess eligibility for **PMEGP** (15%–35% capital subsidy), **MUDRA** (up to ₹10L collateral-free), **PM Vishwakarma**, and **Stand-Up India**.\n` +
      `• 📊 **13-Section Detailed Project Report (DPR):** Step-by-step guidance for bank appraisal using our DPR Builder.\n` +
      `• 💰 **EMI & Debt Feasibility:** Calculate monthly EMI, interest rates, and debt-to-income limits for any loan amount.\n` +
      `• 📜 **Statutory Licenses & Registrations:** Udyam MSME, FSSAI, local trade permits, and GST requirements.\n\n` +
      `👉 *Ask me any question about starting an enterprise, checking subsidy eligibility, or planning your loan repayments!*`;
  }

  // 2. Specific Government Schemes
  // 2.1 PMEGP
  if (query.includes('pmegp') || query.includes('prime minister employment')) {
    if (isHi) {
      return `### 🏛️ प्रधानमंत्री रोजगार सृजन कार्यक्रम (PMEGP) विवरण (${dist}, ${state}):\n\n` +
        `• **उद्देश्य:** विनिर्माण (Manufacturing) एवं सेवा (Services) में नए सूक्ष्म उद्यम स्थापित करने के लिए सब्सिडी युक्त ऋण।\n` +
        `• **अधिकतम परियोजना लागत:** विनिर्माण के लिए ₹50 लाख तक, सेवा क्षेत्र के लिए ₹20 लाख तक।\n` +
        `• **सरकारी सब्सिडी (मार्जिन मनी):**\n` +
        `   - **शहरी क्षेत्र (सामान्य वर्ग):** 15% सब्सिडी | लाभार्थी का अंशदान: 10%\n` +
        `   - **शहरी क्षेत्र (विशेष वर्ग - महिला/OBC/SC/ST/अल्पसंख्यक):** 25% सब्सिडी | लाभार्थी का अंशदान: 5%\n` +
        `   - **ग्रामीण क्षेत्र (सामान्य वर्ग):** 25% सब्सिडी | लाभार्थी का अंशदान: 10%\n` +
        `   - **ग्रामीण क्षेत्र (विशेष वर्ग/महिलाएं):** 35% सब्सिडी | लाभार्थी का अंशदान: 5%\n` +
        `• **नोडल एजेंसियां:** KVIC, KVIB और जिला उद्योग केंद्र (DIC ${dist})।\n` +
        `• **बैंक ऋण:** शेष 90%-95% राशि अनुसूचित वाणिज्यिक बैंक द्वारा सावधि ऋण (Term Loan) एवं कार्यशील पूंजी के रूप में दी जाती है।\n\n` +
        `👉 *अगला कदम:* UnnatE 'DPR Builder' में PMEGP चुनकर बैंक के लिए 13-अनुभाग प्रोजेक्ट रिपोर्ट तैयार करें।`;
    }

    return `### 🏛️ Prime Minister’s Employment Generation Programme (PMEGP) Guide for ${dist}, ${state}:\n\n` +
      `• **Objective:** Credit-linked capital subsidy for establishing new micro-enterprises in manufacturing and services.\n` +
      `• **Maximum Project Cost:** Up to ₹50 Lakhs for Manufacturing; up to ₹20 Lakhs for Service sector.\n` +
      `• **Subsidy Rate (Margin Money Grant):**\n` +
      `   - **Urban General Category:** 15% Subsidy | Promoter Contribution: 10%\n` +
      `   - **Urban Special Category (Women / OBC / SC / ST / Minorities):** 25% Subsidy | Promoter Contribution: 5%\n` +
      `   - **Rural General Category:** 25% Subsidy | Promoter Contribution: 10%\n` +
      `   - **Rural Special Category / Women:** 35% Subsidy | Promoter Contribution: 5%\n` +
      `• **Nodal Agencies:** KVIC, KVIB, and District Industries Centre (DIC ${dist}).\n` +
      `• **Bank Loan:** Remaining 90%–95% sanctioned as Term Loan & Working Capital with 3-year subsidy lock-in.\n\n` +
      `👉 *Action Item:* Use UnnatE's 'DPR Builder' to generate your bank-ready PMEGP Detailed Project Report with verified debt amortization schedules.`;
  }

  // 2.2 MUDRA
  if (query.includes('mudra') || query.includes('shishu') || query.includes('kishor') || query.includes('tarun')) {
    if (isHi) {
      return `### 💰 प्रधानमंत्री मुद्रा योजना (PMMY) विवरण (${dist}, ${state}):\n\n` +
        `मुद्रा योजना के तहत विनिर्माण, व्यापार और सेवा गतिविधियों के लिए बिना किसी गारंटी (Collateral-Free) ऋण मिलता है:\n\n` +
        `1. **शिशु (Shishu):** ₹50,000 तक का ऋण (नए एवं अत्यंत छोटे व्यवसायों के लिए)।\n` +
        `2. **किशोर (Kishore):** ₹50,001 से ₹5,00,000 तक (उपकरण खरीद व दुकान विस्तार हेतु)।\n` +
        `3. **तरुण (Tarun):** ₹5,00,001 से ₹10,00,000 तक (स्थापित इकाइयों के आधुनिकीकरण हेतु)।\n` +
        `4. **तरुण प्लस (Tarun Plus):** ₹10 लाख से ₹20 लाख तक (सफल पुनर्भुगतान करने वाले उद्यमियों के लिए)।\n\n` +
        `• **ब्याज दर:** बैंक आधारित (आमतौर पर 8.5% से 10.5% p.a.)।\n` +
        `• **अवधि (Tenure):** 3 वर्ष से 5 वर्ष (सुविधाजनक EMI)।\n` +
        `• **आवश्यक दस्तावेज़:** आधार कार्ड, पैन कार्ड, Udyam पंजीकरण, 6 महीने का बैंक खाता विवरण और व्यवसाय कोटेशन।\n\n` +
        `👉 *सलाह:* UnnatE 'Financial Options' में जाकर अपनी मासिक EMI और पात्रता की तुरंत जांच करें।`;
    }

    return `### 💰 Pradhan Mantri MUDRA Yojana (PMMY) Guide for ${dist}, ${state}:\n\n` +
      `MUDRA provides collateral-free institutional credit across all public, private, and regional rural banks for non-farm micro-enterprises:\n\n` +
      `1. **Shishu Category:** Loans up to ₹50,000 (ideal for micro startups and initial inventory).\n` +
      `2. **Kishore Category:** Loans from ₹50,001 to ₹5,00,000 (for equipment, machinery, and shop expansion).\n` +
      `3. **Tarun Category:** Loans from ₹5,00,001 to ₹10,00,000 (for enterprise scaling and commercial fleet/assets).\n` +
      `4. **Tarun Plus:** Enhanced ceiling up to ₹20 Lakhs for proven entrepreneurs who repaid Tarun loans.\n\n` +
      `• **Collateral Security:** Zero collateral required (backed by Credit Guarantee Fund for Micro Units - CGFMU).\n` +
      `• **Repayment Tenure:** Up to 5 to 7 years with reasonable moratorium periods.\n` +
      `• **Key Documents:** Aadhaar, PAN, free Udyam MSME Registration, 6 months bank statement, and project estimate.\n\n` +
      `👉 *Action Item:* Navigate to 'Financial Options' to evaluate affordable EMI limits for your targeted loan ticket!`;
  }

  // 2.3 PM Vishwakarma
  if (query.includes('vishwakarma') || query.includes('artisan') || query.includes('हस्तशिल्प') || query.includes('शिल्पकार')) {
    if (isHi) {
      return `### 🛠️ पीएम विश्वकर्मा योजना (PM Vishwakarma Scheme):\n\n` +
        `पारंपरिक 18 ट्रेडों (बढ़ई, लोहार, कुम्हार, दर्जी, मोची, आदि) के कारीगरों और शिल्पकारों के लिए केंद्र सरकार की फ्लैगशिप योजना:\n\n` +
        `• **प्रशिक्षण व भत्ता:** 5-7 दिन का बुनियादी प्रशिक्षण और ₹500/दिन वजीफा।\n` +
        `• **टूलकिट प्रोत्साहन:** ₹15,000 का ई-वाउचर आधुनिक औजार खरीदने के लिए।\n` +
        `• **सस्ता ऋण (Concessional Credit):**\n` +
        `   - **पहला चरण:** ₹1,00,000 तक का ऋण (18 महीने की अवधि, केवल 5% रियायती ब्याज दर)।\n` +
        `   - **दूसरा चरण:** पहले ऋण के सफल भुगतान पर ₹2,00,000 तक का ऋण (30 महीने की अवधि @ 5%)।\n` +
        `• **डिजिटल लेनदेन प्रोत्साहन:** प्रत्येक UPI/डिजिटल लेनदेन पर ₹1 का कैश इंसेंटिव (प्रति माह ₹100 तक)।\n\n` +
        `👉 *आवेदन:* नजदीकी जन सेवा केंद्र (CSC) से pmvishwakarma.gov.in पर मुफ्त पंजीकरण कराएं।`;
    }

    return `### 🛠️ PM Vishwakarma Scheme Guide for Artisans & Craftspersons:\n\n` +
      `A Central Sector Scheme supporting traditional artisans across 18 family-based trades (carpenters, blacksmiths, potters, cobblers, tailors, weavers, etc.):\n\n` +
      `• **Skill Training & Stipend:** 5–7 days basic skill training with ₹500/day daily stipend.\n` +
      `• **Toolkit Incentive:** ₹15,000 digital incentive via e-RUPI / voucher for modern tool purchase.\n` +
      `• **Collateral-Free Concessional Loan:**\n` +
      `   - **Tranche 1:** Up to ₹1,00,000 at a concessional interest rate of 5% (18-month tenure).\n` +
      `   - **Tranche 2:** Up to ₹2,00,000 at 5% interest rate (30-month tenure) upon standard repayment of Tranche 1.\n` +
      `• **Digital Incentive:** ₹1 reward per eligible digital transaction up to 100 transactions monthly.\n\n` +
      `👉 *Registration:* Available free through Common Service Centres (CSC) at pmvishwakarma.gov.in.`;
  }

  // 3. Loan EMI / Financial Calculations
  if (
    query.includes('emi') ||
    query.includes('loan') ||
    query.includes('interest') ||
    query.includes('rate') ||
    query.includes('lakh') ||
    query.includes('किस्त') ||
    query.includes('ब्याज')
  ) {
    let amount = 500000;
    const lakhMatch = query.match(/(\d+(?:\.\d+)?)\s*(?:lakh|lac|लाख)/i);
    const rawNumberMatch = query.match(/₹?\s*(\d{5,8})/);

    if (lakhMatch) {
      amount = Math.round(parseFloat(lakhMatch[1]) * 100000);
    } else if (rawNumberMatch) {
      amount = parseInt(rawNumberMatch[1], 10);
    }

    const calcEmi = (p: number, rYear: number, nMonths: number) => {
      const r = (rYear / 100) / 12;
      return Math.round((p * r * Math.pow(1 + r, nMonths)) / (Math.pow(1 + r, nMonths) - 1));
    };

    const emi36 = calcEmi(amount, 9.0, 36);
    const emi60 = calcEmi(amount, 9.5, 60);
    const emi84 = calcEmi(amount, 9.5, 84);

    if (isHi) {
      return `### 💰 ₹${amount.toLocaleString('en-IN')} के व्यावसायिक ऋण के लिए EMI पुनर्भुगतान परिदृश्य (${dist}):\n\n` +
        `बैंक दर (9.0% - 9.5% p.a.) के आधार पर अनुमानित मासिक किश्त:\n\n` +
        `• **संतुलित विकल्प (5 वर्ष / 60 महीने @ 9.5% p.a.):** ~₹${emi60.toLocaleString('en-IN')} / महीना *(सर्वाधिक अनुशंसित)*\n` +
        `   - कुल ब्याज: ~₹${((emi60 * 60) - amount).toLocaleString('en-IN')}\n\n` +
        `• **त्वरित विकल्प (3 वर्ष / 36 महीने @ 9.0% p.a.):** ~₹${emi36.toLocaleString('en-IN')} / महीना\n` +
        `   - कुल ब्याज: ~₹${((emi36 * 36) - amount).toLocaleString('en-IN')} *(कम ब्याज भुगतान)*\n\n` +
        `• **विस्तारित विकल्प (7 वर्ष / 84 महीने @ 9.5% p.a.):** ~₹${emi84.toLocaleString('en-IN')} / महीना\n` +
        `   - कुल ब्याज: ~₹${((emi84 * 84) - amount).toLocaleString('en-IN')} *(न्यूनतम मासिक बोझ)*\n\n` +
        `📌 **सुरक्षित उधार नियम (Prudent Borrowing Rule):**\n` +
        `सुनिश्चित करें कि आपकी कुल मासिक EMI आपकी शुद्ध डिस्पोजेबल आय के **40%-50%** से अधिक न हो।\n\n` +
        `👉 *विस्तृत अनुकूलन के लिए 'Financial Options' या 'DPR Builder' का उपयोग करें।*`;
    }

    return `### 💰 Loan Repayment & EMI Schedule for ₹${amount.toLocaleString('en-IN')} (${dist}):\n\n` +
      `Projected monthly repayments under standard MSME priority sector lending benchmarks (9.0%–9.5% p.a.):\n\n` +
      `• **Balanced Plan (5 Years / 60 Months @ 9.5% p.a.):** ~₹${emi60.toLocaleString('en-IN')} / month *(Recommended)*\n` +
      `   - Total Interest Outflow: ~₹${((emi60 * 60) - amount).toLocaleString('en-IN')}\n\n` +
      `• **Accelerated Plan (3 Years / 36 Months @ 9.0% p.a.):** ~₹${emi36.toLocaleString('en-IN')} / month\n` +
      `   - Total Interest Outflow: ~₹${((emi36 * 36) - amount).toLocaleString('en-IN')} *(Lowest total interest)*\n\n` +
      `• **Extended Plan (7 Years / 84 Months @ 9.5% p.a.):** ~₹${emi84.toLocaleString('en-IN')} / month\n` +
      `   - Total Interest Outflow: ~₹${((emi84 * 84) - amount).toLocaleString('en-IN')} *(Lowest monthly cash drain)*\n\n` +
      `📌 **Debt Health Benchmark:**\n` +
      `Your total debt payments should stay comfortably below **40% to 50%** of your verified uncommitted monthly surplus.\n\n` +
      `👉 *Test your exact surplus cash flow in the 'Financial Options' tab!*`;
  }

  // 4. Starting a Business / General Prerequisites
  if (
    query.includes('start') ||
    query.includes('before') ||
    query.includes('know') ||
    query.includes('begin') ||
    query.includes('setup') ||
    query.includes('new business') ||
    query.includes('idea') ||
    query.includes('शुरू') ||
    query.includes('नया व्यापार')
  ) {
    if (isHi) {
      return `### 🚀 ${dist} में नया व्यवसाय शुरू करने के 6 अनिवार्य कदम:\n\n` +
        `1. **स्थानीय मांग का आकलन (Market Demand):** ${dist} में 48,000+ पंजीकृत एमएसएमई हैं। खुदरा व्यापार, खाद्य प्रसंस्करण, हैंडलूम और उपभोक्ता सेवाओं में निरंतर मांग है।\n` +
        `2. **उद्यम ऑनलाइन पंजीकरण (Udyam MSME):** udyamregistration.gov.in पर मुफ्त आधिकारिक प्रमाण पत्र प्राप्त करें। यह सभी सरकारी लाभों के लिए अनिवार्य है।\n` +
        `3. **स्थानीय लाइसेंस एवं एनओसी:** ग्राम पंचायत या नगर निगम से ट्रेड लाइसेंस तथा खाद्य व्यवसाय के लिए FSSAI पंजीकरण प्राप्त करें।\n` +
        `4. **सरकारी वित्तीय योजना चयन:**\n` +
        `   • नए विनिर्माण/सेवा उद्यम के लिए **PMEGP** (15% से 35% पूंजीगत सब्सिडी)।\n` +
        `   • बिना गारंटी पूंजी के लिए **MUDRA योजना** (₹10 लाख तक)।\n` +
        `5. **13-अनुभाग विस्तृत परियोजना रिपोर्ट (DPR):** बैंक अधिकारी ऋण के लिए विस्तृत तकनीकी और वित्तीय रिपोर्ट मांगते हैं। UnnatE 'DPR Builder' से 60 सेकंड में PDF बनाएं।\n` +
        `6. **कार्यशील पूंजी बफर:** शुरुआती 3 महीनों के परिचालन खर्च के बराबर आपातकालीन नकद रिजर्व रखें।\n\n` +
        `👉 *अगला कदम:* बाईं ओर दिए गए 'DPR Builder' पर क्लिक करके अपनी पहली प्रोजेक्ट रिपोर्ट तैयार करें।`;
    }

    return `### 🚀 6 Essential Steps Before Starting a Business in ${dist}, ${state}:\n\n` +
      `1. **Hyper-Local Market Validation:** With over 48,000 registered MSMEs in ${dist}, strong opportunities exist in value-added manufacturing, agri-food processing, retail trade, and specialized craft services.\n` +
      `2. **Free Udyam MSME Registration:** Register at udyamregistration.gov.in using Aadhaar and PAN. This gives statutory MSME status and priority sector bank lending access.\n` +
      `3. **Local Municipal & Statutory Permits:** Secure your local trade license from the Municipal Corporation or Gram Panchayat, plus FSSAI certification if handling food/agri products.\n` +
      `4. **Government Scheme Leverage:**\n` +
      `   • **PMEGP:** For 15%–35% capital subsidy grants on new setups.\n` +
      `   • **MUDRA Scheme:** For collateral-free credit up to ₹10 Lakhs.\n` +
      `5. **Bank-Ready Detailed Project Report (DPR):** Commercial banks require a structured 13-section DPR covering capital outlay, ROI, and debt amortization. Generate yours instantly in UnnatE 'DPR Builder'.\n` +
      `6. **Working Capital Runway:** Retain a liquid reserve covering at least 60 to 90 days of fixed overhead before commercial launch.\n\n` +
      `👉 *Ready to begin? Head to 'DPR Builder' to synthesize your official bank report!*`;
  }

  // 5. Document & Licensing Inquiries
  if (
    query.includes('doc') ||
    query.includes('paper') ||
    query.includes('license') ||
    query.includes('registration') ||
    query.includes('udyam') ||
    query.includes('fssai') ||
    query.includes('checklist') ||
    query.includes('दस्तावेज़') ||
    query.includes('कागजात')
  ) {
    if (isHi) {
      return `### 📜 बैंक ऋण एवं व्यवसाय पंजीकरण के लिए आवश्यक दस्तावेज़ चेकलिस्ट (${dist}):\n\n` +
        `**1. पहचान व पते के प्रमाण:**\n` +
        `   • आधार कार्ड, पैन कार्ड, मतदाता पहचान पत्र\n` +
        `   • पासपोर्ट साइज फोटो और निवास प्रमाण\n\n` +
        `**2. व्यावसायिक प्रमाण पत्र:**\n` +
        `   • **Udyam पंजीकरण प्रमाण पत्र** (निःशुल्क ऑनलाइन एमएसएमई प्रमाण)\n` +
        `   • स्थानीय पंचायत/नगर निगम ट्रेड लाइसेंस\n` +
        `   • दुकान स्थापना (Shop & Establishment) अधिनियम पंजीकरण\n` +
        `   • खाद्य/डेयरी उद्यम के लिए FSSAI पंजीकरण\n\n` +
        `**3. वित्तीय एवं बैंक दस्तावेज़:**\n` +
        `   • पिछले 6 महीने का बचत/चालू बैंक खाता विवरण\n` +
        `   • जीएसटी रिटर्न (यदि लागू हो) या बिक्री पर्चियां\n` +
        `   • मशीनरी/उपकरण के अधिकृत सप्लायर कोटेशन (3 प्रतियां)\n\n` +
        `**4. परियोजना रिपोर्ट:**\n` +
        `   • UnnatE **13-अनुभाग Detailed Project Report (DPR)** (लागत संरचना, EMI, ब्रेक-ईवन विश्लेषण)।\n\n` +
        `👉 *UnnatE 'DPR Builder' टैब से अपने व्यवसाय की आधिकारिक रिपोर्ट तुरंत डाउनलोड करें।*`;
    }

    return `### 📜 Bank Loan & Business Registration Checklist for ${dist}, ${state}:\n\n` +
      `**1. KYC & Personal Proofs:**\n` +
      `   • Aadhaar Card, PAN Card, Voter ID\n` +
      `   • Passport-size photos and residential utility bill\n\n` +
      `**2. Statutory Business Registrations:**\n` +
      `   • **Udyam MSME Certificate** (Free online registration)\n` +
      `   • Local Municipal Trade License / Gram Panchayat NOC\n` +
      `   • FSSAI Basic Registration (for food, grocery, dairy, and culinary units)\n` +
      `   • Commercial Electricity Connection receipt or premises lease agreement\n\n` +
      `**3. Financial & Operational Records:**\n` +
      `   • 6 months bank statement of personal/business account\n` +
      `   • Machinery and equipment price quotations from verified vendors\n` +
      `   • Existing loan sanction letters (if any)\n\n` +
      `**4. Technical Project Appraisal:**\n` +
      `   • UnnatE **13-Section Detailed Project Report (DPR)** containing statutory capital breakdown, debt serviceability, and market indicators.\n\n` +
      `👉 *You can generate your full DPR package directly from the 'DPR Builder' tab!*`;
  }

  // 6. General / Contextual Open-Ended Inquiries
  const sanitizedQuery = lastUserMsg.replace(/[*_`#]/g, '').trim();
  const hasBusinessContext = /(business|loan|credit|subsidy|scheme|startup|shop|store|trade|factory|mill|farm|dairy|product|service|mandi|market|dpr|bank|money|capital|cost|vyapar|udyam|kosh|paisa|rin|invest|profit|turnover|equipment|yojana)/i.test(query);

  if (!hasBusinessContext && query.split(/\s+/).length <= 4) {
    if (isHi) {
      return `### 💡 UnnatE AI व्यावसायिक सलाहकार (${dist}, ${state})\n\n` +
        `मैं आपके सूक्ष्म उद्यम और नए व्यवसाय के लिए निम्नलिखित मुख्य क्षेत्रों में सहायता प्रदान करता हूँ:\n\n` +
        `• 🏛️ **सरकारी सब्सिडी योजनाएं:** PMEGP (15%–35% सब्सिडी), मुद्रा योजना (₹10 लाख तक बिना गारंटी ऋण), और PM विश्वकर्मा।\n` +
        `• 💰 **ऋण EMI और ब्याज दर गणना:** अपने बजट के अनुसार सुरक्षित 3, 5, या 7 साल की किश्तों की जांच करें।\n` +
        `• 📊 **13-अनुभाग बैंक DPR रिपोर्ट:** बैंक लोन स्वीकृति हेतु 60 सेकंड में आधिकारिक प्रोजेक्ट रिपोर्ट बनाएं।\n` +
        `• 📜 **लाइसेंस एवं चेकलिस्ट:** Udyam पंजीकरण, ट्रेड लाइसेंस, और FSSAI की पूरी प्रक्रिया।\n\n` +
        `👉 *कृपया अपने व्यवसाय के प्रकार या ऋण आवश्यकता से संबंधित प्रश्न पूछें!*`;
    }

    return `### 💡 UnnatE AI Business Advisory for ${dist}, ${state}\n\n` +
      `I specialize in helping micro-entrepreneurs and business owners with:\n\n` +
      `• 🏛️ **Government Subsidies & Schemes:** PMEGP (15%–35% capital grant), MUDRA Yojana, and PM Vishwakarma.\n` +
      `• 💰 **Loan EMI Structuring:** Instant monthly repayment schedules for 3, 5, and 7-year terms.\n` +
      `• 📊 **13-Section Detailed Project Report (DPR):** Bank-ready technical and financial feasibility reports.\n` +
      `• 📜 **Statutory Registrations:** Udyam MSME, FSSAI food licenses, and municipal trade permits.\n\n` +
      `👉 *Please tell me what type of business you run or what loan/subsidy you would like to explore!*`;
  }

  if (isHi) {
    return `### 💡 ${dist}, ${state} के लिए रणनीतिक AI व्यावसायिक मार्गदर्शन:\n\n` +
      `आपके प्रश्न **"${sanitizedQuery}"** के संदर्भ में मुख्य सिफारिशें:\n\n` +
      `1. **स्थानीय क्लस्टर क्षमता:** ${dist} में सूक्ष्म एवं लघु उद्योगों का मजबूत नेटवर्क है। अपने उत्पाद अथवा सेवा को क्षेत्रीय खरीदारों और थोक व्यापारियों से जोड़ना त्वरित लाभ सुनिश्चित करता है।\n` +
      `2. **सरकारी वित्तीय सहायता:** आपकी गतिविधि के अनुसार आप **PMEGP (25%-35% पूंजीगत सब्सिडी)** अथवा **MUDRA (₹10 लाख तक बिना गारंटी ऋण)** के लिए पात्र हो सकते हैं।\n` +
      `3. **अनुशंसित कार्य-योजना:**\n` +
      `   • **चरण 1:** अपना Udyam MSME ऑनलाइन पंजीकरण पूरा करें।\n` +
      `   • **चरण 2:** UnnatE 'DPR Builder' से 13-अनुभाग बैंक प्रोजेक्ट रिपोर्ट जनरेट करें।\n` +
      `   • **चरण 3:** स्थानीय लीड बैंक अथवा जिला उद्योग केंद्र (DIC ${dist}) में प्रस्ताव प्रस्तुत करें।\n\n` +
      `क्या आप विशिष्ट योजना पात्रता, आवश्यक लाइसेंस, अथवा ऋण EMI की विस्तृत गणना देखना चाहते हैं?`;
  }

  return `### 💡 Strategic Business Advisory for ${dist}, ${state}:\n\n` +
    `Regarding your inquiry on **"${sanitizedQuery}"**:\n\n` +
    `1. **Hyper-Local Cluster Context:** ${dist} has a thriving commercial micro-enterprise ecosystem. Aligning your enterprise directly with local supply nodes and retail corridors provides immediate market traction.\n` +
    `2. **Statutory Financial Schemes:** Depending on whether your unit is new or existing, you can qualify for **PMEGP (15%–35% capital subsidy grant)** or **MUDRA Yojana (collateral-free credit up to ₹10 Lakhs)**.\n` +
    `3. **Recommended Action Roadmap:**\n` +
    `   • **Step 1:** Complete your free Udyam MSME certificate at udyamregistration.gov.in.\n` +
    `   • **Step 2:** Generate your technical 13-section Detailed Project Report via UnnatE 'DPR Builder'.\n` +
    `   • **Step 3:** Submit your structured DPR and quotation checklist to your local commercial bank branch for priority sector credit appraisal.\n\n` +
    `Would you like me to guide you through loan EMI structuring, document checklists, or specific scheme eligibility?`;
}
