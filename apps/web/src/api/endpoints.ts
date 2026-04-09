import { apiGet, apiPatchJson, apiPostJson } from "@/api/client";
import type {
  AdminGrantCreditsResponse,
  AdminPaymentRow,
  AdminReviewActionResponse,
  AdminReviewOrderRow,
  AdminUserDetail,
  AdminUserRow,
} from "@/types/admin";
import type {
  BrandVoiceMeta,
  OrderCreatePayload,
  OrderDto,
  OrderGenerateResponse,
  OrderPayResponse,
  OrderQuotePreviewPayload,
  OrderQuoteResponse,
  RegisterResponse,
  TokenResponse,
  UserPublic,
  VerifyEmailResponse,
} from "@/types";

const V = "/api/v1";

export async function registerUser(payload: {
  email: string;
  username: string;
  password: string;
  referral_code?: string;
}): Promise<RegisterResponse> {
  return apiPostJson<RegisterResponse, typeof payload>(
    `${V}/auth/register`,
    payload
  );
}

export type ReferralSummary = {
  referral_code: string;
  referral_link_query: string;
  slug_locked: boolean;
  referrals_count: number;
  rewards_total_cents: number;
};

export async function fetchReferralSummary(): Promise<ReferralSummary> {
  return apiGet<ReferralSummary>(`${V}/referral/summary`);
}

export async function updateReferralCode(code: string): Promise<ReferralSummary> {
  return apiPatchJson<ReferralSummary, { code: string }>(`${V}/referral/code`, {
    code,
  });
}

export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  return apiPostJson<TokenResponse, typeof payload>(`${V}/auth/login`, payload);
}

export async function verifyEmailRequest(payload: {
  code: string;
}): Promise<VerifyEmailResponse> {
  return apiPostJson<VerifyEmailResponse, typeof payload>(
    `${V}/auth/verify-email`,
    payload
  );
}

/** Повторная отправка кода (email + пароль; JWT не нужен — до verify логин закрыт). */
export async function resendVerificationEmailRequest(payload: {
  email: string;
  password: string;
}): Promise<UserPublic> {
  return apiPostJson<UserPublic, typeof payload>(
    `${V}/auth/resend-verification-email`,
    payload
  );
}

export async function fetchMe(): Promise<UserPublic> {
  return apiGet<UserPublic>(`${V}/auth/me`);
}

export async function fetchAdminUsers(): Promise<AdminUserRow[]> {
  return apiGet<AdminUserRow[]>(`${V}/admin/users`);
}

export async function fetchAdminUserDetail(
  userId: number
): Promise<AdminUserDetail> {
  return apiGet<AdminUserDetail>(`${V}/admin/users/${userId}`);
}

export async function patchAdminUserActive(
  userId: number,
  isActive: boolean
): Promise<AdminUserRow> {
  return apiPatchJson<AdminUserRow, { is_active: boolean }>(
    `${V}/admin/users/${userId}`,
    { is_active: isActive }
  );
}

export async function grantAdminCredits(
  userId: number,
  amountCents: number,
  reason: string
): Promise<AdminGrantCreditsResponse> {
  return apiPostJson<
    AdminGrantCreditsResponse,
    { amount_cents: number; reason: string }
  >(`${V}/admin/users/${userId}/grant-credits`, {
    amount_cents: amountCents,
    reason,
  });
}

export async function fetchAdminPayments(): Promise<AdminPaymentRow[]> {
  return apiGet<AdminPaymentRow[]>(`${V}/admin/payments`);
}

export async function fetchAdminReviewQueue(): Promise<AdminReviewOrderRow[]> {
  return apiGet<AdminReviewOrderRow[]>(`${V}/admin/orders/review-queue`);
}

export async function approveAdminOrderReview(
  orderId: number,
  notes: string | null
): Promise<AdminReviewActionResponse> {
  return apiPostJson<
    AdminReviewActionResponse,
    { notes: string | null }
  >(`${V}/admin/orders/${orderId}/review/approve`, { notes });
}

export async function rejectAdminOrderReview(
  orderId: number,
  notes: string | null
): Promise<AdminReviewActionResponse> {
  return apiPostJson<
    AdminReviewActionResponse,
    { notes: string | null }
  >(`${V}/admin/orders/${orderId}/review/reject`, { notes });
}

/** Тестовое пополнение (только если на бэкенде enable_user_wallet_mock_topup). */
export async function mockUserWalletTopup(amountCents: number): Promise<{
  payment_id: number;
  user_balance_cents: number;
}> {
  return apiPostJson<
    { payment_id: number; user_balance_cents: number },
    { amount_cents: number }
  >(`${V}/wallet/mock-topup`, { amount_cents: amountCents });
}

export async function fetchYooKassaWalletStatus(): Promise<{
  yookassa_topup_available: boolean;
}> {
  return apiGet<{ yookassa_topup_available: boolean }>(
    `${V}/wallet/yookassa/status`
  );
}

export async function createYooKassaWalletTopup(amountCents: number): Promise<{
  payment_id: number;
  confirmation_url: string;
}> {
  return apiPostJson<
    { payment_id: number; confirmation_url: string },
    { amount_cents: number }
  >(`${V}/wallet/yookassa/create`, { amount_cents: amountCents });
}

export async function fetchBrandVoices(): Promise<{ items: BrandVoiceMeta[] }> {
  return apiGet<{ items: BrandVoiceMeta[] }>(`${V}/brand-voices`);
}

export async function previewOrderPrice(
  body: OrderQuotePreviewPayload
): Promise<OrderQuoteResponse> {
  return apiPostJson<OrderQuoteResponse, OrderQuotePreviewPayload>(
    `${V}/orders/preview-price`,
    body
  );
}

export async function createOrder(
  body: OrderCreatePayload
): Promise<OrderDto> {
  return apiPostJson<OrderDto, OrderCreatePayload>(`${V}/orders`, body);
}

export async function fetchOrders(): Promise<OrderDto[]> {
  return apiGet<OrderDto[]>(`${V}/orders`);
}

export async function payOrderFromBalance(
  orderId: number
): Promise<OrderPayResponse> {
  return apiPostJson<OrderPayResponse, Record<string, never>>(
    `${V}/orders/${orderId}/pay`,
    {}
  );
}

export async function generateOrderText(
  orderId: number
): Promise<OrderGenerateResponse> {
  return apiPostJson<OrderGenerateResponse, Record<string, never>>(
    `${V}/orders/${orderId}/generate`,
    {}
  );
}

export async function demoRewrite(body: {
  text: string;
  voice_id: string;
}): Promise<{ result: string }> {
  return apiPostJson<{ result: string }, typeof body>(`${V}/demo/rewrite`, body);
}
