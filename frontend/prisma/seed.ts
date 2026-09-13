import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const SCHEMES_DATA = [
  {
    name: "MoSJE Micro Finance Scheme (NBCFDC / NSFDC)",
    ministry: "Ministry of Social Justice and Empowerment (MoSJE)",
    description: "Special concessional micro-credit for small business units up to ₹1.40 Lakh project cost. Beneficiary contributes 10% (max ₹15,000) and State Channelizing Agencies (SCAs) provide 90% (max ₹1.25 Lakh) concessional loan.",
    loanMin: 20000,
    loanMax: 140000,
    interestRate: 5.0,
    tenure: 36,
    state: "all",
    keywords: "mosje,micro finance,margin money,concessional loan,sca,10 percent contribution",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["OBC", "SC", "ST", "Marginalized"],
      targetBusinessTypes: ["retail", "services", "agriculture", "manufacturing"],
      marginMoneyPercentage: 10,
      scaLoanPercentage: 90,
      maxProjectCost: 140000,
      maxScaLoan: 125000,
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "Beneficiary contributes only 10% of project cost as margin money",
        "SCA provides 90% (up to ₹1.25 Lakh) as concessional loan at 5% interest",
        "Targeted at economic empowerment of marginalized communities"
      ]
    })
  },
  {
    name: "MoSJE General Term Loan Scheme (Up to ₹10 Lakhs)",
    ministry: "Ministry of Social Justice and Empowerment (MoSJE)",
    description: "Concessional term loan scheme for establishing micro-enterprises up to ₹10.00 Lakhs. Beneficiary contributes 10% (₹1.00 Lakh for ₹10L project) and SCA provides 90% (₹9.00 Lakhs) at low interest.",
    loanMin: 140001,
    loanMax: 1000000,
    interestRate: 6.0,
    tenure: 60,
    state: "all",
    keywords: "mosje,term loan,10 lakh,margin money,10 percent,sca loan,concessional",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["OBC", "SC", "ST", "Marginalized"],
      targetBusinessTypes: ["agriculture", "manufacturing", "services", "retail", "transport"],
      marginMoneyPercentage: 10,
      scaLoanPercentage: 90,
      maxProjectCost: 1000000,
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "10% beneficiary margin money contribution (e.g. ₹1 Lakh for ₹10 Lakh enterprise)",
        "90% SCA concessional loan funding (e.g. ₹9 Lakh loan at 6% interest)",
        "Repayment tenure up to 5 years with flexible EMI options"
      ]
    })
  },
  {
    name: "MoSJE Mahila Samriddhi Yojana (Micro-Credit for Women)",
    ministry: "Ministry of Social Justice and Empowerment (MoSJE)",
    description: "Exclusive micro-finance scheme for women entrepreneurs from backward classes and target groups. Concessional loan up to ₹1.40 Lakh at ultra-low 4% annual interest rate.",
    loanMin: 10000,
    loanMax: 140000,
    interestRate: 4.0,
    tenure: 36,
    state: "all",
    keywords: "mosje,mahila samriddhi,women entrepreneur,micro credit,concessional 4 percent",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["Women", "OBC", "SC", "ST"],
      targetBusinessTypes: ["retail", "services", "agriculture"],
      marginMoneyPercentage: 5,
      scaLoanPercentage: 95,
      maxProjectCost: 140000,
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "Ultra-low 4% per annum interest rate for women entrepreneurs",
        "SCA funds 95% of unit cost with minimal beneficiary margin money",
        "Direct credit linkage with local Self-Help Groups (SHGs)"
      ]
    })
  },
  {
    name: "Pradhan Mantri MUDRA Yojana (Shishu)",
    ministry: "Ministry of Finance",
    description: "Micro-credit loan up to ₹50,000 for starting small businesses such as local shops, tailoring, food stalls, and artisan work with zero collateral.",
    loanMin: 10000,
    loanMax: 50000,
    interestRate: 8.5,
    tenure: 36,
    state: "all",
    keywords: "mudra,shishu,micro-loan,retail,services,zero collateral",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST"],
      targetBusinessTypes: ["retail", "services", "agriculture"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "No collateral or third-party guarantee required",
        "Up to 3-year repayment tenure",
        "Direct bank disbursement with MUDRA card"
      ]
    })
  },
  {
    name: "Pradhan Mantri MUDRA Yojana (Kishor)",
    ministry: "Ministry of Finance",
    description: "Loan support from ₹50,001 to ₹5,00,000 for expanding established micro-enterprises, buying machinery, inventory, or livestock.",
    loanMin: 50001,
    loanMax: 500000,
    interestRate: 9.0,
    tenure: 60,
    state: "all",
    keywords: "mudra,kishor,expansion,agriculture,manufacturing,dairy",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST"],
      targetBusinessTypes: ["agriculture", "manufacturing", "services", "retail", "transport"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "Suitable for purchasing machinery, cows/buffaloes, inventory",
        "Flexible EMI schedule based on cash flow",
        "Government credit guarantee cover"
      ]
    })
  },
  {
    name: "Pradhan Mantri MUDRA Yojana (Tarun)",
    ministry: "Ministry of Finance",
    description: "Loan range from ₹5,00,001 to ₹10,00,000 for scaling up high-growth micro-enterprises and purchasing commercial equipment.",
    loanMin: 500001,
    loanMax: 1000000,
    interestRate: 9.5,
    tenure: 60,
    state: "all",
    keywords: "mudra,tarun,scaling,transport,manufacturing,large micro-enterprise",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST"],
      targetBusinessTypes: ["manufacturing", "transport", "agriculture", "services"],
      creditHistoryRequired: true,
      collateralRequired: false,
      keyPoints: [
        "Maximum loan up to ₹10 Lakhs under MUDRA framework",
        "Ideal for commercial vehicle purchase, mini processing units",
        "Minimal documentation"
      ]
    })
  },
  {
    name: "PM SVANidhi Scheme",
    ministry: "Ministry of Housing and Urban Affairs",
    description: "Special micro-credit facility for street vendors, small village traders, and mobile service providers with 7% interest subsidy on timely repayment.",
    loanMin: 10000,
    loanMax: 50000,
    interestRate: 7.0,
    tenure: 24,
    state: "all",
    keywords: "svanidhi,vendor,trader,cashback,interest subsidy",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST"],
      targetBusinessTypes: ["retail", "services"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "7% annual interest subsidy deposited directly to bank account",
        "Digital transaction cashback incentive up to ₹1,200 per year",
        "Automatic eligibility for higher loan limits upon early repayment"
      ]
    })
  },
  {
    name: "PMEGP (Prime Minister's Employment Generation Programme)",
    ministry: "Ministry of MSME",
    description: "Credit-linked subsidy scheme offering 15% to 35% margin money subsidy for setting up new micro-manufacturing or service units in rural areas.",
    loanMin: 100000,
    loanMax: 1000000,
    interestRate: 9.25,
    tenure: 84,
    state: "all",
    keywords: "pmegp,subsidy,rural entrepreneur,khadi,kvic,margin money",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST", "Women"],
      targetBusinessTypes: ["manufacturing", "services", "agriculture"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "35% subsidy for SC/ST/OBC/Women/Rural applicants",
        "25% subsidy for General Category Rural applicants",
        "Mandatory 10-day Entrepreneurship Development Programme (EDP) training"
      ]
    })
  },
  {
    name: "Stand-Up India Scheme",
    ministry: "Ministry of Finance",
    description: "Promotes entrepreneurship among SC/ST and Women entrepreneurs for setting up greenfield micro-enterprises in manufacturing, services, or trading.",
    loanMin: 100000,
    loanMax: 1000000,
    interestRate: 8.75,
    tenure: 84,
    state: "all",
    keywords: "standup india,women entrepreneur,sc,st,greenfield",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["SC", "ST", "Women"],
      targetBusinessTypes: ["manufacturing", "services", "retail", "agriculture"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "Dedicated scheme for SC, ST, and Women micro-entrepreneurs",
        "Repayment tenure up to 7 years with 18-month moratorium period",
        "Supported by Credit Guarantee Scheme for Stand Up India Loans (CGFSIL)"
      ]
    })
  },
  {
    name: "NABARD Dairy Entrepreneurship Development",
    ministry: "Ministry of Agriculture & NABARD",
    description: "Financial subsidy and bank credit for establishing small dairy farms (2 to 10 cows/buffaloes), milk collection units, and vermicompost pits.",
    loanMin: 50000,
    loanMax: 700000,
    interestRate: 8.5,
    tenure: 60,
    state: "all",
    keywords: "dairy,nabard,livestock,cows,milk,agriculture",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST"],
      targetBusinessTypes: ["agriculture"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "25% capital subsidy for General Category, 33.33% for SC/ST farmers",
        "Covers cattle purchase, shed construction, and milking equipment",
        "Direct tie-up with local dairy cooperatives"
      ]
    })
  },
  {
    name: "UP Mukhya Mantri Yuva Swarozgar Yojana",
    ministry: "Government of Uttar Pradesh",
    description: "State-level scheme providing financial assistance up to ₹10 Lakhs with 25% margin money subsidy for unemployed youth starting ventures in UP.",
    loanMin: 50000,
    loanMax: 1000000,
    interestRate: 8.5,
    tenure: 60,
    state: "Uttar Pradesh",
    keywords: "up,swarozgar,uttar pradesh,yuva,state scheme",
    eligibility: JSON.stringify({
      minAge: 18,
      category: ["General", "OBC", "SC", "ST"],
      targetBusinessTypes: ["manufacturing", "services", "retail"],
      creditHistoryRequired: false,
      collateralRequired: false,
      keyPoints: [
        "25% capital grant / margin money subsidy",
        "Priority for Uttar Pradesh residents with minimum 10th pass qualification",
        "Easy single-window digital application through UP DIC portal"
      ]
    })
  }
];

async function main() {
  console.log("Seeding government schemes database (including MoSJE concessional loan schemes)...");

  for (const schemeData of SCHEMES_DATA) {
    await prisma.scheme.upsert({
      where: { name: schemeData.name },
      update: schemeData,
      create: schemeData,
    });
  }

  console.log(`Successfully seeded ${SCHEMES_DATA.length} government schemes!`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
