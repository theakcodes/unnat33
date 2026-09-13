/**
 * SIH26091 - Centralized Application Constants & Configuration
 * Ensures zero hard-coded strings, endpoints, or numbers across components.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.BACKEND_URL ||
  'http://127.0.0.1:8080';

export const API_ENDPOINTS = {
  HEALTH: '/api/v1/health',
  AUTH: {
    REGISTER: '/api/v1/users/register',
    LOGIN: '/api/v1/users/token',
    ME: '/api/v1/users/me',
  },
  BUSINESSES: {
    LIST: '/api/v1/business-profiles',
    CREATE: '/api/v1/business-profiles',
    GET: (id: string | number) => `/api/v1/business-profiles/${id}`,
    UPDATE: (id: string | number) => `/api/v1/business-profiles/${id}`,
  },
  PROGRAMS: {
    LIST: '/api/v1/programs',
    GET: (id: string | number) => `/api/v1/programs/${id}`,
    EVALUATE_ELIGIBILITY: '/api/v1/programs/evaluate-eligibility',
  },
  RECOMMENDATIONS: {
    RECOMMEND: '/api/v1/recommendations/recommend',
    FINANCIAL_STRUCTURING: '/api/v1/recommendations/financial-structuring',
  },
  RESEARCH: {
    DISTRICT_CONTEXT: '/api/v1/research/district-market-context',
    MARKET_INTELLIGENCE: '/api/v1/research/district-market-intelligence',
  },
  DPR: {
    GENERATE: '/api/v1/dpr/generate-canonical-dpr',
  },
} as const;

export const PAGE_LIMITS = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_FILE_SIZE_MB: 5,
  SESSION_TIMEOUT_MINUTES: 1440,
} as const;

export const BUSINESS_TYPES = {
  AGRICULTURE: 'agriculture',
  RETAIL: 'retail',
  SERVICES: 'services',
  MANUFACTURING: 'manufacturing',
} as const;

export const EXPERIENCE_LEVELS = {
  NO_EXPERIENCE: 'no_experience',
  ONE_TO_THREE: '1-3_years',
  THREE_TO_FIVE: '3-5_years',
  FIVE_PLUS: '5_plus_years',
} as const;

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  UNAUTHORIZED: 'Your session has expired. Please log in again.',
  FORBIDDEN: 'You do not have permission to access this resource.',
  NOT_FOUND: 'The requested resource could not be found.',
  VALIDATION_ERROR: 'Please check your inputs and try again.',
  SERVER_ERROR: 'An internal server error occurred. Please try again later.',
} as const;

export const SUCCESS_MESSAGES = {
  PLAN_CREATED: 'Business plan created successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  DPR_GENERATED: 'Detailed Project Report (DPR) generated successfully!',
} as const;
