import Groq from 'groq-sdk';

export function getGroqClient(): Groq | null {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey || apiKey.trim() === '') {
    return null;
  }
  return new Groq({ apiKey: apiKey.trim() });
}

export const DEFAULT_GROQ_MODEL = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';
