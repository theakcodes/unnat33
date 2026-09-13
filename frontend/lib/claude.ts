import Anthropic from '@anthropic-ai/sdk';
import { logger } from './logger';

function getAnthropicClient() {
  const apiKey = process.env.ANTHROPIC_API_KEY || process.env.CLAUDE_API_KEY;
  if (!apiKey || apiKey.trim() === '') return null;
  return new Anthropic({
    apiKey: apiKey.trim(),
    defaultHeaders: {
      'anthropic-beta': 'prompt-caching-2024-07-31'
    }
  });
}

// System Prompt
const BASE_SYSTEM_PROMPT = `You are an expert hyper-local business advisor specializing in rural micro-entrepreneurship in India and Ministry of Social Justice and Empowerment (MoSJE) concessional loan schemes.
You have deep expertise in:
- MoSJE schemes (NBCFDC, NSFDC, NSKFDC Micro Finance & Term Loans): 10% Beneficiary Margin Money Contribution vs 90% State Channelizing Agency (SCA) Concessional Loan
- Indian government schemes (MUDRA Shishu/Kishor/Tarun, PM SVANidhi, PMEGP, Stand-Up India, NABARD, State schemes)
- Rural market dynamics, local supply chains, seasonal agricultural trends, livestock management, and small retail operations
- Micro-finance, EMI structuring, debt-to-income analysis, credit risk, and bank pre-approval requirements
- State-specific regulations, FSSAI, Udyam Registration, Trade Licenses, DIC procedures

IMPORTANT: Always deliver realistic, quantitative, highly actionable guidance customized for the user's specific state, district, and business domain.
Return output in strictly valid JSON without markdown wrapping.`;

export interface BusinessPlanInput {
  businessType: string;
  subType?: string;
  experienceLevel: string;
  targetMarket: string;
  currentIncome: number;
  estimatedCapital: number;
  existingDebt?: number;
  state: string;
  district: string;
  additionalContext?: string;
  language?: string;
}

export interface FinancialInput {
  monthlyIncome: number;
  monthlyExpenses: number;
  existingLoans: { name: string; emi: number }[];
  creditHistory: string;
  loanNeeded: number;
  purpose: string;
  preferredTenure: number;
  collateralAvailable: string[];
  state: string;
  district: string;
}

// 1. Business Plan Generator Service
export async function generateBusinessPlanAI(input: BusinessPlanInput) {
  const anthropic = getAnthropicClient();
  if (anthropic) {
    try {
      logger.info('🤖 Invoking Claude 3.5 Sonnet for Business Plan Generation...');
      const response = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2500,
        temperature: 0.3,
        system: BASE_SYSTEM_PROMPT,
        messages: [
          {
            role: 'user',
            content: `Generate a qualitative business plan advisory and operational implementation plan for:
Business Type: ${input.businessType} (${input.subType || 'General'})
Experience Level: ${input.experienceLevel}
Target Market: ${input.targetMarket}
Current Monthly Income: ₹${input.currentIncome}
Required Initial Capital: ₹${input.estimatedCapital}
Existing Debt: ₹${input.existingDebt || 0}
Location: ${input.district}, ${input.state}
Context: ${input.additionalContext || 'None'}
Language: ${input.language || 'en'}

CRITICAL INSTRUCTIONS:
- Do NOT invent or predict arbitrary revenue numbers, expenses, net profits, or break-even months.
- Do NOT output an unverified feasibility score.
- Focus strictly on qualitative business strategy, practical operational milestones, statutory licensing requirements, and risk mitigation.

Respond ONLY with JSON matching this structure:
{
  "feasibilityStatus": "pending_dpr_audit",
  "executiveSummary": "string",
  "marketAnalysis": {
    "demandStatus": "Field Verification Required",
    "competitionStatus": "Local Survey Required",
    "growthOpportunities": "string",
    "targetCustomers": "string"
  },
  "actionTimeline": [
    { "month": 1, "title": "string", "description": "string", "completed": boolean }
  ],
  "requiredPermits": ["string"],
  "risks": [
    { "risk": "string", "impact": "High" | "Medium" | "Low", "mitigation": "string" }
  ],
  "relevantSchemesPreview": ["string"]
}`,
          },
        ],
      });

      const text = response.content[0].type === 'text' ? response.content[0].text : '';
      const parsed = JSON.parse(text);
      // Ensure zero financial fabrication in output
      return {
        ...parsed,
        feasibilityScore: null,
        feasibilityStatus: 'pending_dpr_audit',
        financialProjections: null,
      };
    } catch (err) {
      logger.error('⚠️ Claude API call error, falling back to qualitative generator:', err);
    }
  }

  // Qualitative fallback generator (Zero-Fabrication)
  const isAgri = input.businessType.toLowerCase().includes('agri') || input.businessType.toLowerCase().includes('farm') || input.businessType.toLowerCase().includes('dairy');
  const cap = input.estimatedCapital || 500000;

  return {
    feasibilityScore: null,
    feasibilityStatus: 'pending_dpr_audit',
    executiveSummary: `Strategic operational plan for ${input.businessType} micro-enterprise in ${input.district}, ${input.state}. Statutory financing eligibility can be structured through central and state schemes (PMEGP, MUDRA, MoSJE). Commercial viability requires verified local unit economics and formal DPR appraisal.`,
    marketAnalysis: {
      demand: "Field Verification Required",
      competition: "Local Survey Required",
      growthOpportunities: `Enterprise scaling in ${input.district} is linked to securing formal credit linkages, reliable regional supply chains, and established off-take channels.`,
      targetCustomers: input.targetMarket || (isAgri ? "Local agricultural co-operatives, village traders, and regional Mandi buyers (user-declared)" : "Hyper-local retail households and nearby market trade outlets (user-declared)")
    },
    financialProjections: null,
    actionTimeline: [
      { month: 1, title: "Registration & Site Setup", description: "Complete Udyam registration and establish business premises/lease.", completed: true },
      { month: 2, title: "Statutory Scheme Application", description: `Submit credit proposal for capital target of ₹${cap.toLocaleString('en-IN')} under PMEGP / MUDRA at local bank branch.`, completed: false },
      { month: 3, title: "Procurement & Trial Operations", description: "Procure equipment/raw materials and initiate operational trial setup.", completed: false },
      { month: 4, title: "Commercial Launch", description: "Establish supply linkages with regional buyers and local commercial network.", completed: false },
      { month: 5, title: "Operations Streamlining", description: "Monitor operational overhead and build cash reserve buffer.", completed: false },
      { month: 6, title: "Stabilization Milestone", description: "Review debt serviceability and working capital turnaround.", completed: false }
    ],
    requiredPermits: [
      "Udyam Micro Registration (Free Online Portal)",
      "Local Gram Panchayat / Municipal Trade License",
      isAgri ? "FSSAI Basic Registration / Food License" : "Shop & Establishment License (State Portal)",
      "Business PAN & Current Bank Account"
    ],
    risks: [
      { risk: "Working capital delays", impact: "Medium", mitigation: "Maintain at least 2 months operational expense reserve." },
      { risk: "Input cost volatility", impact: "Medium", mitigation: "Establish multiple supplier relationships across " + input.district + "." },
      { risk: "Credit repayment strain", impact: "High", mitigation: "Align borrowing tenure with verified disposable income using statutory amortization structures." }
    ],
    relevantSchemesPreview: [
      "Prime Minister's Employment Generation Programme (PMEGP)",
      "Pradhan Mantri MUDRA Yojana (Kishor / Tarun)",
      "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
      "MoSJE Concessional Finance Schemes"
    ]
  };
}

// 2. Financial Advisor Service
export async function generateFinancialAdviceAI(input: FinancialInput) {
  const anthropic = getAnthropicClient();
  const existingEmiTotal = input.existingLoans?.reduce((acc, curr) => acc + curr.emi, 0) || 0;
  const netAvailableIncome = input.monthlyIncome - input.monthlyExpenses - existingEmiTotal;
  const dti = Math.min(100, Math.round(((existingEmiTotal) / (input.monthlyIncome || 1)) * 100));
  const maxAffordableEMI = Math.max(2000, Math.round(netAvailableIncome * 0.5));
  const amount = input.loanNeeded || 300000;

  if (anthropic) {
    try {
      logger.info('🤖 Invoking Claude 3.5 Sonnet for Financial Advisory...');
      const response = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2500,
        temperature: 0.2,
        system: BASE_SYSTEM_PROMPT,
        messages: [
          {
            role: 'user',
            content: `Analyze micro-finance loan structuring for:
Monthly Income: ₹${input.monthlyIncome}
Monthly Expenses: ₹${input.monthlyExpenses}
Existing EMIs: ₹${existingEmiTotal}
Required Loan: ₹${amount}
Purpose: ${input.purpose}
Credit History: ${input.creditHistory}
Location: ${input.district}, ${input.state}

Respond ONLY with valid JSON structure:
{
  "debtToIncomeRatio": number,
  "affordableEMI": number,
  "creditAssessment": "Low Risk" | "Moderate Risk" | "High Risk",
  "structures": {
    "conservative": { "tenureMonths": 48, "interestRate": number, "monthlyEMI": number, "totalInterest": number, "feasibility": "string" },
    "balanced": { "tenureMonths": 60, "interestRate": number, "monthlyEMI": number, "totalInterest": number, "feasibility": "string" },
    "extended": { "tenureMonths": 72, "interestRate": number, "monthlyEMI": number, "totalInterest": number, "feasibility": "string" }
  },
  "preApprovalChecklist": ["string"],
  "nextSteps": ["string"]
}`
          }
        ]
      });

      const text = response.content[0].type === 'text' ? response.content[0].text : '';
      return JSON.parse(text);
    } catch (e) {
      logger.error('⚠️ Claude financial API error, using mock fallback:', e);
    }
  }

  // Exact interest & EMI calculation fallback
  const calcEmi = (p: number, rYear: number, nMonths: number) => {
    const r = rYear / (12 * 100);
    const emi = (p * r * Math.pow(1 + r, nMonths)) / (Math.pow(1 + r, nMonths) - 1);
    return Math.round(emi);
  };

  const emi48 = calcEmi(amount, 9.5, 48);
  const emi60 = calcEmi(amount, 9.0, 60);
  const emi72 = calcEmi(amount, 9.5, 72);

  return {
    debtToIncomeRatio: dti,
    affordableEMI: maxAffordableEMI,
    creditAssessment: dti < 35 ? "Low Risk" : dti < 55 ? "Moderate Risk" : "High Risk",
    structures: {
      conservative: {
        tenureMonths: 48,
        interestRate: 9.5,
        monthlyEMI: emi48,
        totalInterest: (emi48 * 48) - amount,
        feasibility: emi48 <= maxAffordableEMI ? "Highly Affordable" : "Requires income boost"
      },
      balanced: {
        tenureMonths: 60,
        interestRate: 9.0,
        monthlyEMI: emi60,
        totalInterest: (emi60 * 60) - amount,
        feasibility: "Recommended (Lowest Interest Rate)"
      },
      extended: {
        tenureMonths: 72,
        interestRate: 9.5,
        monthlyEMI: emi72,
        totalInterest: (emi72 * 72) - amount,
        feasibility: "Lowest Monthly Outflow"
      }
    },
    preApprovalChecklist: [
      "Aadhaar Card & PAN Card copy",
      "Bank Account Statement for last 6 months",
      "Proof of Business Location (Gram Panchayat letter / lease / electricity bill)",
      "Udyam Registration Certificate",
      "Project Cost Estimate / Quotation for equipment"
    ],
    nextSteps: [
      `Visit local bank branch in ${input.district} with completed pre-approval checklist.`,
      `Request MoSJE / MUDRA Kishor / Tarun scheme application form for ₹${amount.toLocaleString('en-IN')}.`,
      "Submit project report and financial projections generated by UnnatE."
    ]
  };
}

import { generateAdvisorResponse } from './ai-advisor';

// 3. AI Chat Assistant Service
export async function getAdvisorChatResponse(messages: { role: string; content: string }[], userContext: any) {
  return generateAdvisorResponse(messages, userContext);
}
