import { apiGet, apiPostJson } from "@/api/client";
import type {
  BrandVoiceMeta,
  OrderCreatePayload,
  OrderDto,
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
}): Promise<RegisterResponse> {
  return apiPostJson<RegisterResponse, typeof payload>(
    `${V}/auth/register`,
    payload
  );
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

export async function demoRewrite(body: {
  text: string;
  voice_id: string;
}): Promise<{ result: string }> {
  return apiPostJson<{ result: string }, typeof body>(`${V}/demo/rewrite`, body);
}
