import { prisma } from './prisma';

/**
 * Identify whether a business record is an orphan artifact created by a past
 * Advisory Plan generation flow without saved user profile details.
 */
export function isOrphanAdvisoryBusiness(b: any): boolean {
  if (!b) return false;
  return (
    !b.sector &&
    !b.activity &&
    !b.stage &&
    b.isNewBusiness === null &&
    b.projectCost === null &&
    b.monthlyIncome === null &&
    b.monthlyExpenses === null &&
    b.existingDebt === null &&
    b.existingMonthlyEmi === null &&
    b.annualIncome === null &&
    b.annualTurnover === null &&
    !b.requestedFinancing &&
    !b.promoterContribution
  );
}

/**
 * Deterministically resolve a user's business profile following strict priority:
 * a. Explicitly designated primary business, if schema supports it (currently no isPrimary column).
 * b. Existing business referenced by the user's profile/session/request (requestedBusinessId).
 * c. If exactly one business exists, use it.
 *    (Blank/orphan business records created by past Advisory Plan visits must not override the actual business profile).
 * d. If multiple legitimate businesses exist and there is no primary designation, do NOT guess (return null).
 */
export async function resolvePrimaryBusiness(userId: string, requestedBusinessId?: string | null) {
  const allBusinesses = await prisma.business.findMany({
    where: { userId },
    orderBy: { createdAt: 'desc' },
  });

  if (allBusinesses.length === 0) return null;

  // b. Existing business explicitly referenced by ID
  if (requestedBusinessId) {
    const found = allBusinesses.find((b) => b.id === requestedBusinessId);
    if (found) return found;
  }

  // Filter out blank/orphan advisory records
  const legitimateBusinesses = allBusinesses.filter((b) => !isOrphanAdvisoryBusiness(b));

  // c. If exactly one legitimate business exists, use it deterministically
  if (legitimateBusinesses.length === 1) {
    return legitimateBusinesses[0];
  }

  // If no legitimate business exists yet, check if there is only 1 business overall
  if (legitimateBusinesses.length === 0) {
    if (allBusinesses.length === 1) {
      return allBusinesses[0];
    }
    // Multiple orphan businesses exist and none is legitimate -> do not guess
    return null;
  }

  // d. Multiple legitimate businesses exist with no primary designation -> do NOT guess
  return null;
}
