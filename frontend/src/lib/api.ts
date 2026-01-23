// API client for AdGenius backend

import type {
  Project,
  ProjectCreate,
  ProductAnalysis,
  MarketAnalysis,
  VideoConcept,
  GeneratedVideo,
  VideoProvider,
} from '../types';

const API_BASE = '/api';

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Projects
export const projectsApi = {
  list: () => fetchApi<Project[]>('/projects/'),

  get: (id: string) => fetchApi<Project>(`/projects/${id}`),

  create: (data: ProjectCreate) =>
    fetchApi<Project>('/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    fetchApi<{ status: string; id: string }>(`/projects/${id}`, {
      method: 'DELETE',
    }),
};

// Analysis
export const analysisApi = {
  analyzeProduct: (projectId: string) =>
    fetchApi<ProductAnalysis>(`/analysis/${projectId}/product`, {
      method: 'POST',
    }),

  analyzeMarket: (projectId: string, competitors?: string[], country = 'IT') =>
    fetchApi<MarketAnalysis>(`/analysis/${projectId}/market`, {
      method: 'POST',
      body: JSON.stringify({ competitor_names: competitors, country }),
    }),

  generateConcepts: (projectId: string, numConcepts = 3) =>
    fetchApi<VideoConcept[]>(
      `/analysis/${projectId}/concepts?num_concepts=${numConcepts}`,
      { method: 'POST' }
    ),

  runFullAnalysis: (projectId: string) =>
    fetchApi<{ status: string; message: string; project_id: string }>(
      `/analysis/${projectId}/full-analysis`,
      { method: 'POST' }
    ),
};

// Video
export const videoApi = {
  generate: (
    projectId: string,
    conceptIndex = 0,
    provider: VideoProvider = 'sora'
  ) =>
    fetchApi<GeneratedVideo>(
      `/video/${projectId}/generate/${conceptIndex}?provider=${provider}`,
      { method: 'POST' }
    ),

  list: (projectId: string) =>
    fetchApi<GeneratedVideo[]>(`/video/${projectId}/videos`),

  getDownloadUrl: (projectId: string, videoId: string) =>
    `${API_BASE}/video/${projectId}/videos/${videoId}/download`,
};

// GitHub Repository types
export interface GitHubRepo {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  url: string;
  homepage: string | null;
  language: string | null;
  topics: string[];
  stars: number;
  forks: number;
  is_private: boolean;
  created_at: string;
  updated_at: string;
  default_branch: string;
}

export interface RepoAnalysis {
  repo: GitHubRepo;
  analysis: {
    product_name: string;
    category: string;
    what_it_does: string;
    problem_solved: string;
    target_audience: {
      primary: string;
      interests: string[];
      pain_points: string[];
    };
    usp: string[];
    tech_stack: string[];
    status: string;
    product_url: string | null;
    visual_style: {
      recommended_style: string;
      mood: string;
      color_palette: string;
    };
    video_hook_ideas: string[];
  };
}

// GitHub
export const githubApi = {
  listRepos: (visibility = 'all', sort = 'updated') =>
    fetchApi<GitHubRepo[]>(`/github/repos?visibility=${visibility}&sort=${sort}`),

  analyzeRepo: (owner: string, repo: string) =>
    fetchApi<RepoAnalysis>(`/github/repos/${owner}/${repo}/analyze`, {
      method: 'POST',
    }),

  createProjectFromRepo: (owner: string, repo: string) =>
    fetchApi<Project>(`/github/repos/${owner}/${repo}/create-project`, {
      method: 'POST',
    }),

  generateVideoPrompt: (owner: string, repo: string) =>
    fetchApi<unknown>(`/github/repos/${owner}/${repo}/generate-video-prompt`, {
      method: 'POST',
    }),

  generateVideo: (owner: string, repo: string, provider = 'veo', duration = 8) =>
    fetchApi<VideoRecord>(`/github/repos/${owner}/${repo}/generate-video?provider=${provider}&duration=${duration}`, {
      method: 'POST',
    }),
};

// Video record from database
export interface VideoRecord {
  id: string;
  repo_owner: string | null;
  repo_name: string | null;
  repo_full_name: string | null;
  title: string;
  description: string | null;
  prompt: string | null;
  provider: string;
  status: string;
  duration_seconds: number;
  resolution: string;
  local_path: string | null;
  video_url: string | null;
  thumbnail_path: string | null;
  error: string | null;
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
}

export interface VideoListResponse {
  total: number;
  skip: number;
  limit: number;
  videos: VideoRecord[];
}

export interface VideoStatsResponse {
  total: number;
  completed: number;
  failed: number;
  processing: number;
  queued: number;
}

// Videos API (database-backed)
export const videosApi = {
  list: (skip = 0, limit = 50, status?: string) =>
    fetchApi<VideoListResponse>(`/videos?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`),

  getStats: () =>
    fetchApi<VideoStatsResponse>('/videos/stats'),

  get: (videoId: string) =>
    fetchApi<VideoRecord>(`/videos/${videoId}`),

  delete: (videoId: string) =>
    fetchApi<{ message: string; id: string }>(`/videos/${videoId}`, {
      method: 'DELETE',
    }),

  listForRepo: (owner: string, repo: string) =>
    fetchApi<{ repo: string; count: number; videos: VideoRecord[] }>(`/videos/repo/${owner}/${repo}`),

  getStreamUrl: (videoId: string) =>
    `${API_BASE}/videos/${videoId}/stream`,
};
