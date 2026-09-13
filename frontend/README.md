# UnnatE (SIH26091) - AI-Driven Hyper-Local Business Advisory & Financial Structuring Assistant

**UnnatE** (Plan • Grow • Succeed) is a complete full-stack web application designed for Smart India Hackathon (SIH26091) to empower rural micro-entrepreneurs in India seeking loans between ₹50,000 to ₹10,000,000 through government schemes like MUDRA, PM SVANidhi, PMEGP, Stand-Up India, and state-specific programs.

---

## Key Features

1. **Exact UI matching UnnatE Mockups:** Hero section ("Know Your Business"), Dashboard stats cards (Market Demand, Relevant Schemes, Estimated Funding, Business Readiness), Recharts Growth Projection line chart & Funding Sources donut chart, location selector ("Uttar Pradesh"), and navigation sidebar.
2. **Bilingual Support (Hindi & English):** Real-time language toggle across all pages, forms, advisories, and AI chat responses.
3. **Claude AI Integration:** Powered by Claude 3.5 Sonnet & Haiku with prompt caching strategy for government schemes and hyper-local insights. Includes fallback response generators.
4. **Hybrid Scheme Eligibility Matcher:** `pgvector` similarity search combined with Claude enrichment for 10+ core Indian government schemes (MUDRA Shishu/Kishor/Tarun, PM SVANidhi, PMEGP, Stand-Up India, NABARD Dairy, UP MMYSY, DAY-NRLM).
5. **Financial Structuring Engine:** Calculates Debt-to-Income (DTI) ratio, safe monthly EMI limits, 3 loan structures (Conservative 48m, Balanced 60m, Extended 72m), and pre-approval document checklists.
6. **Progress Tracking & Analytics:** Monthly actual income/expense logging, plan vs. actual performance charts, and milestone celebration alerts.
7. **7-Day Shareable Reports & QR Code:** Generate public read-only DPR links and downloadable advisories.
8. **PWA Offline Support:** Service worker caching for 2G rural network access.

---

## Tech Stack

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, TanStack Query, Zustand, React Hook Form, Lucide Icons.
- **Backend:** Node.js Express/Next.js REST API routes, JWT authentication (24-hour expiry, HTTP-only cookies).
- **Database:** PostgreSQL 15 with `pgvector` extension + Prisma ORM.
- **AI Engine:** Anthropic Claude API (`@anthropic-ai/sdk`) using `claude-3-5-sonnet-20241022` and `claude-3-haiku-20240307` with prompt caching.

---

## Setup & Running Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your PostgreSQL database URL and Anthropic API key:
```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/unnate_db?schema=public"
JWT_SECRET="unnate_super_secret_jwt_key_sih26091_2026_rural_entrepreneur"
ANTHROPIC_API_KEY="your_claude_api_key_here"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### 3. Setup Database Schema & Seed Data
```bash
npx prisma generate
npx prisma db push
npm run db:seed
```

### 4. Start Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## API Endpoints

- `POST /api/auth/register` - User registration & OTP trigger
- `POST /api/auth/verify-otp` - Verify 6-digit OTP (test code: `123456`)
- `POST /api/auth/logout` - Logout & clear cookie
- `GET/PUT /api/user/profile` - Profile management
- `POST /api/advisory/business-plan` - Claude AI Business Plan generator
- `POST /api/advisory/financial` - Claude AI Financial advisor & EMI structures
- `POST /api/advisory/schemes` - Scheme eligibility vector search & AI enrichment
- `GET/POST /api/businesses` - Business entity management
- `POST/GET /api/progress/:businessId` - Monthly progress logging & comparison analytics
- `POST /api/chat` - Multi-turn AI advisory chat assistant
- `POST /api/reports/generate` - Generate 7-day shareable DPR link & QR code
- `GET /api/reports/share/:shareToken` - Public read-only report view
