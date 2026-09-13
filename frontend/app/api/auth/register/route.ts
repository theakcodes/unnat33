import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { signJwtToken, TOKEN_NAME } from '@/lib/auth';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { phone, name, language, state, district } = body;

    if (!phone || !name) {
      return NextResponse.json({ error: 'Phone number and name are required' }, { status: 400 });
    }

    const user = await prisma.user.upsert({
      where: { phone },
      update: {
        name,
        language: language || 'en',
        state: state || 'Uttar Pradesh',
        district: district || 'Lucknow',
      },
      create: {
        phone,
        name,
        language: language || 'en',
        state: state || 'Uttar Pradesh',
        district: district || 'Lucknow',
      },
    });

    const token = signJwtToken({
      userId: user.id,
      phone: user.phone,
      name: user.name,
      language: user.language,
    });

    const response = NextResponse.json({
      success: true,
      message: 'Registration successful. OTP sent.',
      userId: user.id,
      mockOtp: '123456',
    });

    response.cookies.set(TOKEN_NAME, token, {
      httpOnly: true,
      path: '/',
      maxAge: 86400, // 24 hours
    });

    return response;
  } catch (error: any) {
    console.error('Error in /api/auth/register:', error);
    return NextResponse.json({ error: error.message || 'Server error' }, { status: 500 });
  }
}
