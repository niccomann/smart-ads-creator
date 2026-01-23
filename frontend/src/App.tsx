import { useState } from 'react';
import { useProjects } from './hooks/useProjects';
import { ProjectCard } from './components/ProjectCard';
import { NewProjectForm } from './components/NewProjectForm';
import { ProjectDetail } from './components/ProjectDetail';
import { GitHubRepos } from './components/GitHubRepos';
import { VideoGallery } from './components/VideoGallery';
import type { Project, ProjectCreate } from './types';

type Tab = 'github' | 'videos' | 'projects' | 'new';

function App() {
  const { projects, loading, error, createProject, deleteProject, refreshProject, refetch } =
    useProjects();
  const [activeTab, setActiveTab] = useState<Tab>('github');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const handleCreateProject = async (data: ProjectCreate) => {
    const project = await createProject(data);
    setActiveTab('projects');
    setSelectedProject(project);
  };

  const handleProjectFromGitHub = (project: Project) => {
    refetch(); // Refresh projects list
    setSelectedProject(project);
  };

  const handleDeleteProject = async (id: string) => {
    if (confirm('Sei sicuro di voler eliminare questo progetto?')) {
      await deleteProject(id);
      if (selectedProject?.id === id) {
        setSelectedProject(null);
      }
    }
  };

  const handleRefreshProject = async (id: string) => {
    const updated = await refreshProject(id);
    setSelectedProject(updated);
    return updated;
  };

  // Show project detail view
  if (selectedProject) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <ProjectDetail
          project={selectedProject}
          onBack={() => setSelectedProject(null)}
          onRefresh={handleRefreshProject}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AdGenius AI
              </h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                Crea video pubblicitari per i tuoi progetti GitHub
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mt-6 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('github')}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
                activeTab === 'github'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              GitHub Repos
            </button>
            <button
              onClick={() => setActiveTab('videos')}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
                activeTab === 'videos'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Video Generati
            </button>
            <button
              onClick={() => setActiveTab('projects')}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
                activeTab === 'projects'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Progetti ({projects.length})
            </button>
            <button
              onClick={() => setActiveTab('new')}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
                activeTab === 'new'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              + Manuale
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Error State */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* GitHub Tab */}
        {activeTab === 'github' && (
          <GitHubRepos onProjectCreated={handleProjectFromGitHub} />
        )}

        {/* Videos Tab */}
        {activeTab === 'videos' && (
          <VideoGallery />
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <>
            {loading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
                <p className="mt-4 text-gray-500 dark:text-gray-400">
                  Caricamento progetti...
                </p>
              </div>
            )}

            {!loading && projects.length === 0 && (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">🎬</div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Nessun progetto
                </h2>
                <p className="text-gray-500 dark:text-gray-400 mb-6">
                  Seleziona un repository GitHub per creare il tuo primo video ad
                </p>
                <button
                  onClick={() => setActiveTab('github')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  Vai ai Repository
                </button>
              </div>
            )}

            {!loading && projects.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    onSelect={setSelectedProject}
                    onDelete={handleDeleteProject}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* New Project Form Tab */}
        {activeTab === 'new' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Nuovo Progetto Manuale
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Usa questo form per creare un progetto da un prodotto/servizio che non e' su GitHub.
            </p>
            <NewProjectForm
              onSubmit={handleCreateProject}
              onCancel={() => setActiveTab('github')}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
        AdGenius AI - Powered by Claude Code Max
      </footer>
    </div>
  );
}

export default App;
