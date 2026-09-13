import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { getAdvisorChatResponse } from '@/lib/claude';

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser();
    const body = await req.json();
    const { message, conversationId, businessId } = body;

    if (!message) {
      return NextResponse.json({ error: 'Message content is required' }, { status: 400 });
    }

    let activeUser = user;
    if (!activeUser) {
      // Find or create default guest user for Prisma FK integrity
      try {
        activeUser = await prisma.user.upsert({
          where: { phone: '0000000000' },
          update: {},
          create: {
            phone: '0000000000',
            name: 'Guest Entrepreneur',
            language: 'en',
            state: 'Uttar Pradesh',
            district: 'Lucknow',
          },
        });
      } catch (err) {
        console.warn('Could not upsert guest user:', err);
      }
    }

    const userId = activeUser?.id;
    let session: any = null;

    if (userId) {
      try {
        if (conversationId) {
          session = await prisma.chatSession.findUnique({
            where: { id: conversationId },
            include: { messages: { orderBy: { createdAt: 'asc' } } }
          });
        }

        if (!session) {
          session = await prisma.chatSession.create({
            data: {
              userId,
              businessId: businessId || undefined
            },
            include: { messages: true }
          });
        }

        // Save user message
        await prisma.chatMessage.create({
          data: {
            sessionId: session.id,
            role: 'user',
            content: message
          }
        });
      } catch (err) {
        console.warn('Chat DB persistence error (proceeding with memory history):', err);
      }
    }

    const history = session?.messages
      ? [
          ...session.messages.map((m: any) => ({ role: m.role, content: m.content })),
          { role: 'user', content: message }
        ]
      : [{ role: 'user', content: message }];

    // Call AI advisor chat service
    const replyText = await getAdvisorChatResponse(history, {
      name: activeUser?.name || 'Entrepreneur',
      language: activeUser?.language || 'en',
      district: activeUser?.district || 'Lucknow',
      state: activeUser?.state || 'Uttar Pradesh'
    });

    if (session) {
      try {
        await prisma.chatMessage.create({
          data: {
            sessionId: session.id,
            role: 'assistant',
            content: replyText
          }
        });
      } catch (err) {
        console.warn('Could not save assistant message to DB:', err);
      }
    }

    return NextResponse.json({
      chatId: session?.id || 'guest_session',
      message: replyText,
      role: 'assistant',
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('Chat API error:', error);
    return NextResponse.json({ error: error.message || 'Chat error' }, { status: 500 });
  }
}
