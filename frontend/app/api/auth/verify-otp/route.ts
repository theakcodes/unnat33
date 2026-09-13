import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { signJwtToken, TOKEN_NAME } from '@/lib/auth';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { phone, otp } = body;

    if (!phone || !otp) {
      return NextResponse.json({ error: 'Phone and OTP are required' }, { status: 400 });
    }

    // OTP validation (accepts 123456 or any 6-digit OTP for MVP)
    if (otp !== '123456' && otp.length !== 6) {
      return NextResponse.json({ error: 'Invalid OTP code. Please enter 123456.' }, { status: 400 });
    }

    const user = await prisma.user.findUnique({ where: { phone } });
    if (!user) {
      return NextResponse.json({ error: 'User not found. Please register first.' }, { status: 404 });
    }

    const authToken = signJwtToken({
      userId: user.id,
      phone: user.phone,
      name: user.name,
      language: user.language,
    });

    const response = NextResponse.json({
      success: true,
      userId: user.id,
      authToken,
      user,
    });

    response.cookies.set(TOKEN_NAME, authToken, {
      httpOnly: true,
      path: '/',
      maxAge: 86400, // 24 hours
    });

    return response;
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Server error' }, { status: 500 });
  }
}
