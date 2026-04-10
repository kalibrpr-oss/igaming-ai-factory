/** Синхрон с backend/app/schemas/order.py и seo.py */

export type OrderKind = "generate" | "uniquify";

export interface BrandVoiceMeta {
  id: string;
  label: string;
  description: string;
}

export type BrandVoiceId =
  | "bold_daring"
  | "expert_precise"
  | "friendly_warm";

export type HeadingFormat =
  | "strict_h1_h2_h3"
  | "flat_h2_only"
  | "review_blocks";

export type ArticleType = "review" | "comparison" | "guide" | "bonus" | "news";

export interface SeoOrderConfig {
  language: string;
  primary_keyword: string;
  keyword_density_percent: number;
  heading_format: HeadingFormat;
  meta_description_length: number;
  article_type: ArticleType;
  include_faq_block: boolean;
  include_table_compare: boolean;
  canonical_url_hint?: string | null;
}

export interface OrderCreatePayload {
  order_kind?: OrderKind;
  brand_name: string;
  task_notes?: string | null;
  keywords: string[];
  lsi_keywords: string[];
  target_word_count: number;
  brand_voice_id: BrandVoiceId | string;
  seo: SeoOrderConfig;
  source_text?: string | null;
}

export interface OrderQuotePreviewPayload {
  order_kind?: OrderKind;
  target_word_count: number;
  brand_voice_id: BrandVoiceId | string;
  source_text?: string | null;
}

export interface OrderQuoteResponse {
  order_kind?: OrderKind;
  target_word_count: number;
  billing_word_count?: number | null;
  price_base_cents: number;
  discount_cents: number;
  price_cents: number;
  currency: string;
  first_order_bonus_applied?: boolean;
}

export type OrderStatus =
  | "draft"
  | "pending_payment"
  | "paid"
  | "generating"
  | "review_required"
  | "completed"
  | "failed"
  | "cancelled";

/** Ответ API заказа (синхрон с backend OrderResponse). */
export interface OrderDto {
  id: number;
  status: OrderStatus;
  order_kind?: OrderKind;
  brand_name: string;
  task_notes: string | null;
  source_text?: string | null;
  keywords: string[];
  lsi_keywords: string[];
  seo_config: Record<string, unknown>;
  target_word_count: number;
  price_base_cents: number;
  discount_cents: number;
  price_cents: number;
  brand_voice_id: string;
  generated_text: string | null;
  generated_asset_uri: string | null;
  moderated_at?: string | null;
  moderated_by_user_id?: number | null;
  moderation_notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrderPayResponse {
  order: OrderDto;
  user_balance_cents: number;
}

export interface OrderGenerateResponse {
  order: OrderDto;
}
