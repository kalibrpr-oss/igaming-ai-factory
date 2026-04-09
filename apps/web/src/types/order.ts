/** Синхрон с backend/app/schemas/order.py и seo.py */

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
  brand_name: string;
  task_notes?: string | null;
  keywords: string[];
  lsi_keywords: string[];
  target_word_count: number;
  brand_voice_id: BrandVoiceId | string;
  seo: SeoOrderConfig;
}

export interface OrderQuotePreviewPayload {
  target_word_count: number;
  brand_voice_id: BrandVoiceId | string;
}

export interface OrderQuoteResponse {
  target_word_count: number;
  price_cents: number;
  currency: string;
}

export type OrderStatus =
  | "draft"
  | "pending_payment"
  | "paid"
  | "generating"
  | "completed"
  | "failed"
  | "cancelled";

export interface OrderDto {
  id: number;
  status: OrderStatus;
  brand_name: string;
  task_notes: string | null;
  keywords: string[];
  lsi_keywords: string[];
  seo_config: Record<string, unknown>;
  target_word_count: number;
  price_cents: number;
  brand_voice_id: string;
  generated_asset_uri: string | null;
  created_at: string;
  updated_at: string;
}
