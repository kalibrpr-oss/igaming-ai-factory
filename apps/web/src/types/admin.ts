export type AdminUserRow = {
  id: number;
  email: string;
  username: string;
  created_at: string;
  is_active: boolean;
  is_admin: boolean;
  orders_total: number;
  payments_succeeded: number;
  last_seen_at: string | null;
  last_device_kind: string;
};

export type AdminUserBrief = {
  id: number;
  email: string;
  username: string;
};

export type AdminReferralInviteRow = {
  id: number;
  email: string;
  username: string;
  created_at: string;
};

export type AdminOrderBrief = {
  id: number;
  status: string;
  brand_name: string;
  price_cents: number;
  created_at: string;
};

export type AdminUserDetail = {
  id: number;
  email: string;
  username: string;
  created_at: string;
  is_active: boolean;
  is_admin: boolean;
  is_email_verified: boolean;
  balance_cents: number;
  referral_code: string | null;
  referral_slug_locked: boolean;
  referrer: AdminUserBrief | null;
  referrals: AdminReferralInviteRow[];
  referral_rewards_total_cents: number;
  orders: AdminOrderBrief[];
  last_seen_at: string | null;
  last_device_kind: string;
};

export type AdminPaymentRow = {
  id: number;
  user_id: number;
  user_email: string;
  user_username: string;
  order_id: number | null;
  kind: string;
  provider: string;
  amount_cents: number;
  currency: string;
  status: string;
  created_at: string;
};

export type AdminGrantCreditsResponse = {
  transaction_id: number;
  new_balance_cents: number;
};

/** Заказ в очереди модерации (статус review_required). */
export type AdminReviewOrderRow = {
  id: number;
  user_id: number;
  brand_name: string;
  target_word_count: number;
  price_cents: number;
  status: string;
  created_at: string;
  updated_at: string;
};

export type AdminReviewActionResponse = {
  order_id: number;
  status: string;
  moderated_at: string;
  moderation_notes: string | null;
};
