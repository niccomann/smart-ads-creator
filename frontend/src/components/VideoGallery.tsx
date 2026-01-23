import { useState, useEffect } from 'react';
import { videosApi } from '../lib/api';
import type { VideoRecord, VideoStatsResponse } from '../lib/api';

export function VideoGallery() {
  const [videos, setVideos] = useState<VideoRecord[]>([]);
  const [stats, setStats] = useState<VideoStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const loadVideos = async () => {
    try {
      setLoading(true);
      setError(null);

      const [videosRes, statsRes] = await Promise.all([
        videosApi.list(0, 50, filter === 'all' ? undefined : filter),
        videosApi.getStats()
      ]);

      setVideos(videosRes.videos);
      setStats(statsRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVideos();
  }, [filter]);

  const handleDelete = async (videoId: string) => {
    if (!confirm('Sei sicuro di voler eliminare questo video?')) return;

    try {
      await videosApi.delete(videoId);
      loadVideos();
    } catch (err) {
      alert('Errore durante l\'eliminazione');
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      processing: 'bg-yellow-100 text-yellow-800',
      queued: 'bg-blue-100 text-blue-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('it-IT');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            <div className="text-sm text-gray-500">Totale</div>
          </div>
          <div className="bg-green-50 rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-sm text-green-700">Completati</div>
          </div>
          <div className="bg-yellow-50 rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.processing}</div>
            <div className="text-sm text-yellow-700">In Elaborazione</div>
          </div>
          <div className="bg-blue-50 rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.queued}</div>
            <div className="text-sm text-blue-700">In Coda</div>
          </div>
          <div className="bg-red-50 rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
            <div className="text-sm text-red-700">Falliti</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-700">Filtra per stato:</span>
        <div className="flex gap-2">
          {['all', 'completed', 'processing', 'queued', 'failed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 text-sm rounded-full transition-colors ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status === 'all' ? 'Tutti' : status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
        <button
          onClick={loadVideos}
          className="ml-auto px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          Aggiorna
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Video Grid */}
      {videos.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Nessun video</h3>
          <p className="mt-1 text-sm text-gray-500">
            Genera il tuo primo video pubblicitario da un repository GitHub.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.id}
              className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Video Preview */}
              <div className="aspect-[9/16] bg-gray-900 relative">
                {video.status === 'completed' && video.local_path ? (
                  <video
                    src={videosApi.getStreamUrl(video.id)}
                    className="w-full h-full object-cover"
                    controls
                    preload="metadata"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    {video.status === 'processing' || video.status === 'queued' ? (
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white mx-auto"></div>
                        <p className="text-white mt-2 text-sm">
                          {video.status === 'processing' ? 'Generazione in corso...' : 'In coda...'}
                        </p>
                      </div>
                    ) : video.status === 'failed' ? (
                      <div className="text-center px-4">
                        <svg
                          className="mx-auto h-10 w-10 text-red-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <p className="text-red-300 mt-2 text-xs">{video.error || 'Errore sconosciuto'}</p>
                      </div>
                    ) : (
                      <svg
                        className="h-16 w-16 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                    )}
                  </div>
                )}
              </div>

              {/* Video Info */}
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {video.title}
                    </h3>
                    {video.repo_full_name && (
                      <p className="text-xs text-gray-500 mt-1">
                        {video.repo_full_name}
                      </p>
                    )}
                  </div>
                  <span
                    className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(video.status)}`}
                  >
                    {video.status}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <span>{video.duration_seconds}s • {video.provider}</span>
                  <span>{formatDate(video.created_at)}</span>
                </div>

                {/* Actions */}
                <div className="mt-4 flex gap-2">
                  {video.status === 'completed' && (
                    <a
                      href={videosApi.getStreamUrl(video.id)}
                      download
                      className="flex-1 px-3 py-2 text-sm text-center bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Download
                    </a>
                  )}
                  <button
                    onClick={() => handleDelete(video.id)}
                    className="px-3 py-2 text-sm text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    Elimina
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
