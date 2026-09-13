import { NextResponse } from 'next/server';
import { getCurrentUser, TOKEN_NAME } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function DELETE() {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    await prisma.user.delete({ where: { id: user.id } });

    const response = NextResponse.json({ deleted: true });
    response.cookies.delete(TOKEN_NAME);
    return response;
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
