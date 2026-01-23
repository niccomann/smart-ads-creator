import { useState } from 'react';
import type { Project, VideoProvider } from '../types';
import { analysisApi, videoApi } from '../lib/api';

interface ProjectDetailProps {
  project: Project;
  onBack: () => void;
  onRefresh: (id: string) => Promise<Project>;
}

export function ProjectDetail({ project, onBack, onRefresh }: ProjectDetailProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (type: 'product' | 'market' | 'concepts' | 'full') => {
    setLoading(type);
    setError(null);

    try {
      switch (type) {
        case 'product':
          await analysisApi.analyzeProduct(project.id);
          break;
        case 'market':
          await analysisApi.analyzeMarket(project.id);
          break;
        case 'concepts':
          await analysisApi.generateConcepts(project.id);
          break;
        case 'full':
          await analysisApi.runFullAnalysis(project.id);
          break;
      }
      await onRefresh(project.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante l\'analisi');
    } finally {
      setLoading(null);
    }
  };

  const generateVideo = async (conceptIndex: number, provider: VideoProvider = 'sora') => {
    setLoading(`video-${conceptIndex}`);
    setError(null);

    try {
      await videoApi.generate(project.id, conceptIndex, provider);
      await onRefresh(project.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante la generazione');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={onBack}
          className="text-blue-600 hover:text-blue-800 flex items-center gap-2"
        >
          ← Indietro
        </button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {project.name}
        </h1>
        <span className="text-sm text-gray-500">{project.status}</span>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Analysis Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Analisi
        </h2>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => runAnalysis('full')}
            disabled={loading !== null}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:opacity-90 disabled:opacity-50"
          >
            {loading === 'full' ? 'Analisi in corso...' : 'Analisi Completa'}
          </button>
          <button
            onClick={() => runAnalysis('product')}
            disabled={loading !== null}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading === 'product' ? 'Analisi...' : 'Analizza Prodotto'}
          </button>
          <button
            onClick={() => runAnalysis('market')}
            disabled={loading !== null || !project.product_analysis}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading === 'market' ? 'Analisi...' : 'Analizza Mercato'}
          </button>
          <button
            onClick={() => runAnalysis('concepts')}
            disabled={loading !== null || !project.product_analysis}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {loading === 'concepts' ? 'Generazione...' : 'Genera Concept'}
          </button>
        </div>
      </div>

      {/* Product Analysis */}
      {project.product_analysis && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Analisi Prodotto
          </h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500 dark:text-gray-400">Nome:</span>
              <p className="font-medium text-gray-900 dark:text-white">
                {project.product_analysis.product_name}
              </p>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Categoria:</span>
              <p className="font-medium text-gray-900 dark:text-white">
                {project.product_analysis.category}
              </p>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Posizionamento:</span>
              <p className="font-medium text-gray-900 dark:text-white">
                {project.product_analysis.positioning}
              </p>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Target:</span>
              <p className="font-medium text-gray-900 dark:text-white">
                {project.product_analysis.target_audience.age_range},{' '}
                {project.product_analysis.target_audience.gender}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <span className="text-gray-500 dark:text-gray-400 text-sm">USP:</span>
            <ul className="list-disc list-inside mt-1">
              {project.product_analysis.usp.map((usp, i) => (
                <li key={i} className="text-gray-900 dark:text-white text-sm">
                  {usp}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Video Concepts */}
      {project.concepts.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Concept Video ({project.concepts.length})
          </h2>
          <div className="space-y-4">
            {project.concepts.map((concept, index) => (
              <div
                key={index}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {concept.title}
                  </h3>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {concept.style}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {concept.description}
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => generateVideo(index, 'sora')}
                    disabled={loading !== null}
                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading === `video-${index}` ? 'Generazione...' : 'Genera con Sora'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated Videos */}
      {project.videos.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Video Generati ({project.videos.length})
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {project.videos.map((video) => (
              <div
                key={video.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
              >
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  {video.concept_title}
                </h3>
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  <p>Provider: {video.provider}</p>
                  <p>Status: {video.status}</p>
                  <p>Durata: {video.duration_seconds}s</p>
                </div>
                {video.status === 'completed' && (
                  <a
                    href={videoApi.getDownloadUrl(project.id, video.id)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                    download
                  >
                    Download Video
                  </a>
                )}
                {video.error && (
                  <p className="text-red-500 text-sm">{video.error}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
