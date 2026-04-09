import type { OrderCreatePayload, SeoOrderConfig } from "@/types";
import { z } from "zod";

export const seoFormSchema = z.object({
  language: z.string().min(2).max(8),
  primary_keyword: z.string().min(1).max(256),
  keyword_density_percent: z.number().min(0.5).max(3),
  heading_format: z.enum(["strict_h1_h2_h3", "flat_h2_only", "review_blocks"]),
  meta_description_length: z.number().min(120).max(200),
  article_type: z.enum(["review", "comparison", "guide", "bonus", "news"]),
  include_faq_block: z.boolean(),
  include_table_compare: z.boolean(),
  canonical_url_hint: z.union([z.string().max(512), z.literal("")]).optional(),
});

export type SeoForm = z.infer<typeof seoFormSchema>;

function splitKeys(raw: string, max: number): string[] {
  return raw
    .split(/[\n,]+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, max);
}

export function buildOrderPayload(input: {
  brand_name: string;
  task_notes: string;
  keywords_raw: string;
  lsi_raw: string;
  target_word_count: number;
  brand_voice_id: string;
  seo: SeoForm;
}): { ok: true; payload: OrderCreatePayload } | { ok: false; error: string } {
  const keywords = splitKeys(input.keywords_raw, 50);
  if (keywords.length === 0) {
    return { ok: false, error: "Добавь хотя бы один ключ в поле «Ключи»." };
  }
  const lsi_keywords = splitKeys(input.lsi_raw, 80);
  const seoParsed = seoFormSchema.safeParse(input.seo);
  if (!seoParsed.success) {
    return { ok: false, error: "Проверь SEO-блок: " + seoParsed.error.message };
  }
  const seo: SeoOrderConfig = {
    ...seoParsed.data,
    canonical_url_hint:
      seoParsed.data.canonical_url_hint === ""
        ? null
        : seoParsed.data.canonical_url_hint ?? null,
  };
  return {
    ok: true,
    payload: {
      brand_name: input.brand_name.trim(),
      task_notes: input.task_notes.trim() || null,
      keywords,
      lsi_keywords,
      target_word_count: input.target_word_count,
      brand_voice_id: input.brand_voice_id,
      seo,
    },
  };
}
