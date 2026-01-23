import type { Project } from '../types';

interface ProjectCardProps {
  project: Project;
  onSelect: (project: Project) => void;
  onDelete: (id: string) => void;
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-500',
  analyzing: 'bg-yellow-500',
  ready_for_video: 'bg-blue-500',
  generating: 'bg-purple-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
};

const statusLabels: Record<string, string> = {
  draft: 'Bozza',
  analyzing: 'In analisi...',
  ready_for_video: 'Pronto per video',
  generating: 'Generazione...',
  completed: 'Completato',
  failed: 'Errore',
};

export function ProjectCard({ project, onSelect, onDelete }: ProjectCardProps) {
  return (
    <div
      className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => onSelect(project)}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
          {project.name}
        </h3>
        <span
          className={`${statusColors[project.status]} text-white text-xs px-2 py-1 rounded-full`}
        >
          {statusLabels[project.status]}
        </span>
      </div>

      {project.product_analysis && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            {project.product_analysis.product_name}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {project.product_analysis.category}
          </p>
        </div>
      )}

      <div className="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
        <span>{project.concepts.length} concept</span>
        <span>{project.videos.length} video</span>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(project.id);
          }}
          className="text-red-500 hover:text-red-700 text-sm"
        >
          Elimina
        </button>
      </div>
    </div>
  );
}
