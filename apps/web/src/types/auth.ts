export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserPublic {
  id: number;
  email: string;
  username: string;
  is_admin: boolean;
  is_email_verified: boolean;
  balance_cents?: number;
  /** Скидка 30% на первый заказ ещё доступна */
  first_order_discount_active?: boolean;
}

export type RegisterStatus = "created" | "already_pending_verification";
export type VerificationDeliveryStatus =
  | "background_send_started"
  | "sent"
  | "cooldown";

export interface RegisterResponse extends UserPublic {
  registration_status: RegisterStatus;
  verification_delivery_status: VerificationDeliveryStatus;
  resend_available_in_seconds?: number | null;
}

export interface VerifyEmailResponse extends TokenResponse {
  user: UserPublic;
}
