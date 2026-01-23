import { useState, useEffect } from 'react';
import { githubApi } from '../lib/api';
import type { GitHubRepo, VideoRecord } from '../lib/api';
import type { Project } from '../types';

interface GitHubReposProps {
  onProjectCreated: (project: Project) => void;
}

type VideoProvider = 'sora' | 'veo' | 'runway';

const PROVIDERS: { value: VideoProvider; label: string; icon: string }[] = [
  { value: 'runway', label: 'Runway ML', icon: '🎬' },
  { value: 'sora', label: 'OpenAI Sora', icon: '🤖' },
  { value: 'veo', label: 'Google Veo', icon: '🎥' },
];

export function GitHubRepos({ onProjectCreated }: GitHubReposProps) {
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingRepo, setProcessingRepo] = useState<string | null>(null);
  const [processingAction, setProcessingAction] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<Record<string, unknown> | null>(null);
  const [videoResult, setVideoResult] = useState<VideoRecord | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<VideoProvider>('runway');

  useEffect(() => {
    loadRepos();
  }, []);

  const loadRepos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await githubApi.listRepos('all', 'updated');
      setRepos(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load repos');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (repo: GitHubRepo) => {
    const [owner, name] = repo.full_name.split('/');
    setProcessingRepo(repo.full_name);
    setProcessingAction('analyze');
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await githubApi.analyzeRepo(owner, name);
      setAnalysisResult(result as unknown as Record<string, unknown>);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setProcessingRepo(null);
      setProcessingAction(null);
    }
  };

  const _handleCreateProject = async (repo: GitHubRepo) => {
    const [owner, name] = repo.full_name.split('/');
    setProcessingRepo(repo.full_name);
    setProcessingAction('project');
    setError(null);

    try {
      const project = await githubApi.createProjectFromRepo(owner, name);
      onProjectCreated(project);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Project creation failed');
      setProcessingRepo(null);
      setProcessingAction(null);
    }
  };

  // Expose for potential future use
  void _handleCreateProject;

  const handleGenerateVideo = async (repo: GitHubRepo) => {
    const [owner, name] = repo.full_name.split('/');
    setProcessingRepo(repo.full_name);
    setProcessingAction('video');
    setError(null);
    setVideoResult(null);

    try {
      const duration = selectedProvider === 'runway' ? 5 : 8;
      const result = await githubApi.generateVideo(owner, name, selectedProvider, duration);
      setVideoResult(result);
      if (result.status === 'failed') {
        setError(result.error || 'Video generation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Video generation failed');
    } finally {
      setProcessingRepo(null);
      setProcessingAction(null);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <p className="mt-4 text-gray-500 dark:text-gray-400">
          Caricamento repository GitHub...
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          I Tuoi Repository GitHub
        </h2>
        <button
          onClick={loadRepos}
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          Aggiorna
        </button>
      </div>

      {/* Provider Selector */}
      <div className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Provider Video AI
        </label>
        <div className="flex gap-2 flex-wrap">
          {PROVIDERS.map((provider) => (
            <button
              key={provider.value}
              onClick={() => setSelectedProvider(provider.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedProvider === provider.value
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {provider.icon} {provider.label}
            </button>
          ))}
        </div>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          {selectedProvider === 'runway' && 'Runway ML - 125 crediti gratuiti, 5 crediti/secondo'}
          {selectedProvider === 'sora' && 'OpenAI Sora - Richiede verifica organizzazione'}
          {selectedProvider === 'veo' && 'Google Veo - Richiede piano a pagamento Gemini'}
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Analysis Result Modal */}
      {analysisResult && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Analisi Repository
              </h3>
              <button
                onClick={() => setAnalysisResult(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded text-xs overflow-x-auto">
              {JSON.stringify(analysisResult, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Video Result Modal */}
      {videoResult && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-lg w-full p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {videoResult.status === 'completed' ? 'Video Generato!' : 'Risultato Generazione'}
              </h3>
              <button
                onClick={() => setVideoResult(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {videoResult.status === 'completed' ? (
              <div className="text-center">
                <div className="text-6xl mb-4">🎬</div>
                <p className="text-green-600 font-medium mb-4">
                  Video generato con successo!
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  {videoResult.title}
                </p>
                <a
                  href={`/api/videos/${videoResult.id}/stream`}
                  download
                  className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Scarica Video
                </a>
              </div>
            ) : (
              <div className="text-center">
                <div className="text-6xl mb-4">⚠️</div>
                <p className="text-red-600 font-medium mb-2">
                  Generazione fallita
                </p>
                <p className="text-sm text-gray-500 bg-gray-100 p-3 rounded">
                  {videoResult.error || 'Errore sconosciuto'}
                </p>
                <p className="text-xs text-gray-400 mt-4">
                  Provider: {videoResult.provider} | ID: {videoResult.id}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {repos.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          Nessun repository trovato
        </div>
      ) : (
        <div className="grid gap-4">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {repo.name}
                    </h3>
                    {repo.is_private && (
                      <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
                        Private
                      </span>
                    )}
                    {repo.language && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                        {repo.language}
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {repo.description || 'Nessuna descrizione'}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>⭐ {repo.stars}</span>
                    <span>🍴 {repo.forks}</span>
                    {repo.homepage && (
                      <a
                        href={repo.homepage}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        🔗 Live
                      </a>
                    )}
                    {repo.topics.length > 0 && (
                      <span className="flex gap-1">
                        {repo.topics.slice(0, 3).map((t) => (
                          <span
                            key={t}
                            className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded"
                          >
                            {t}
                          </span>
                        ))}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleAnalyze(repo)}
                    disabled={processingRepo === repo.full_name}
                    className="px-3 py-1.5 text-sm border border-gray-300 text-gray-600 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    {processingRepo === repo.full_name && processingAction === 'analyze' ? '...' : 'Analizza'}
                  </button>
                  <button
                    onClick={() => handleGenerateVideo(repo)}
                    disabled={processingRepo === repo.full_name}
                    className="px-3 py-1.5 text-sm bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded hover:opacity-90 disabled:opacity-50"
                  >
                    {processingRepo === repo.full_name && processingAction === 'video' ? (
                      <span className="flex items-center gap-1">
                        <span className="animate-spin">⏳</span> Generando...
                      </span>
                    ) : (
                      '🎬 Genera Video'
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
