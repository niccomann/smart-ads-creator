// Project types matching backend schemas

export type ProjectStatus =
  | 'draft'
  | 'analyzing'
  | 'ready_for_video'
  | 'generating'
  | 'completed'
  | 'failed';

export type VideoStyle =
  | 'cinematic'
  | 'lifestyle'
  | 'ugc_style'
  | 'product_demo'
  | 'testimonial';

export type VideoPlatform =
  | 'instagram_reels'
  | 'tiktok'
  | 'youtube_shorts'
  | 'facebook_feed';

export type VideoProvider = 'sora' | 'runway' | 'kling';

export interface ProductInput {
  url?: string;
  images: string[];
  description?: string;
  category?: string;
}

export interface BrandInfo {
  name: string;
  tone_of_voice: string;
  colors: Record<string, string>;
}

export interface TargetAudience {
  age_range: string;
  gender: string;
  interests: string[];
  pain_points: string[];
}

export interface VisualStyle {
  aesthetic: string;
  photography_style: string;
  suggested_video_style: string;
}

export interface ProductAnalysis {
  product_name: string;
  category: string;
  price?: number;
  currency: string;
  positioning: string;
  brand: BrandInfo;
  usp: string[];
  target_audience: TargetAudience;
  visual_style: VisualStyle;
  cta_current?: string;
  competitors_inferred: string[];
}

export interface CompetitorAd {
  ad_id: string;
  page_name: string;
  ad_text?: string;
  media_url?: string;
  cta?: string;
  start_date?: string;
  is_active: boolean;
  format: string;
}

export interface CompetitorAnalysis {
  name: string;
  total_active_ads: number;
  dominant_formats: Record<string, number>;
  top_ads: CompetitorAd[];
  messaging_themes: string[];
  gaps_identified: string[];
}

export interface MarketAnalysis {
  competitors: CompetitorAnalysis[];
  industry_trends: Record<string, unknown>;
  opportunities: string[];
}

export interface VideoPrompt {
  provider: VideoProvider;
  main_prompt: string;
  style_reference?: string;
  negative_prompt?: string;
  duration_seconds: number;
  resolution: string;
}

export interface VideoConcept {
  title: string;
  description: string;
  style: VideoStyle;
  platform: VideoPlatform;
  duration_seconds: number;
  prompts: Record<string, VideoPrompt>;
  post_production_notes: Record<string, unknown>;
}

export interface GeneratedVideo {
  id: string;
  project_id: string;
  concept_title: string;
  provider: VideoProvider;
  status: string;
  video_url?: string;
  thumbnail_url?: string;
  duration_seconds: number;
  resolution: string;
  created_at: string;
  error?: string;
}

export interface Project {
  id: string;
  name: string;
  status: ProjectStatus;
  product_input: ProductInput;
  product_analysis?: ProductAnalysis;
  market_analysis?: MarketAnalysis;
  concepts: VideoConcept[];
  videos: GeneratedVideo[];
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  product_input: ProductInput;
}
