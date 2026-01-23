import { useState, useEffect, useCallback } from 'react';
import type { Project, ProjectCreate } from '../types';
import { projectsApi } from '../lib/api';

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsApi.list();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const createProject = async (data: ProjectCreate) => {
    const project = await projectsApi.create(data);
    setProjects((prev) => [...prev, project]);
    return project;
  };

  const deleteProject = async (id: string) => {
    await projectsApi.delete(id);
    setProjects((prev) => prev.filter((p) => p.id !== id));
  };

  const refreshProject = async (id: string) => {
    const project = await projectsApi.get(id);
    setProjects((prev) => prev.map((p) => (p.id === id ? project : p)));
    return project;
  };

  return {
    projects,
    loading,
    error,
    createProject,
    deleteProject,
    refreshProject,
    refetch: fetchProjects,
  };
}
