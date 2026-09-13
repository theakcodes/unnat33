/**
 * SIH26091 - Centralized Logger Utility
 * Provides environment-aware logging with timestamps and level control.
 * Prevents raw console leakage in production environments.
 */

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

const IS_PRODUCTION = process.env.NODE_ENV === 'production';

export const logger = {
  info: (message: string, ...meta: any[]) => {
    if (!IS_PRODUCTION) {
      console.log(`[INFO] [${new Date().toISOString()}] ${message}`, ...meta);
    }
  },

  warn: (message: string, ...meta: any[]) => {
    console.warn(`[WARN] [${new Date().toISOString()}] ${message}`, ...meta);
  },

  error: (message: string, ...meta: any[]) => {
    console.error(`[ERROR] [${new Date().toISOString()}] ${message}`, ...meta);
  },

  debug: (message: string, ...meta: any[]) => {
    if (!IS_PRODUCTION && process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true') {
      console.debug(`[DEBUG] [${new Date().toISOString()}] ${message}`, ...meta);
    }
  },
};
