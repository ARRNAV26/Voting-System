import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { suggestionsAPI } from '../lib/api';
import { SuggestionForm } from '../types';
import { Plus, ArrowLeft } from 'lucide-react';

export const NewSuggestionPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<SuggestionForm>({
    title: '',
    description: '',
    category: 'Feature'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Create suggestion mutation
  const createSuggestionMutation = useMutation({
    mutationFn: suggestionsAPI.create,
    onSuccess: () => {
      // Invalidate and refetch suggestions
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
      queryClient.invalidateQueries({ queryKey: ['top-suggestions'] });
      navigate('/');
    },
    onError: (error: any) => {
      console.error('Failed to create suggestion:', error);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await createSuggestionMutation.mutateAsync(formData);
    } catch (error) {
      // Error is handled by the mutation
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const categories = [
    'Feature',
    'Bug Fix',
    'Improvement',
    'Documentation',
    'Other'
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex items-center space-x-3">
          
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">New Suggestion</h1>
            <p className="text-gray-600 dark:text-gray-300">Share your idea with the team</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="card p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Title *
            </label>
            <input
              id="title"
              name="title"
              type="text"
              required
              value={formData.title}
              onChange={handleChange}
              className="input"
              placeholder="Enter a clear, concise title for your suggestion"
              maxLength={200}
            />
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {formData.title.length}/200 characters
            </p>
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Category *
            </label>
            <select
              id="category"
              name="category"
              required
              value={formData.category}
              onChange={handleChange}
              className="input"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description *
            </label>
            <textarea
              id="description"
              name="description"
              required
              value={formData.description}
              onChange={handleChange}
              rows={6}
              className="input resize-none"
              placeholder="Provide a detailed description of your suggestion. Include the problem it solves, benefits, and any implementation details."
            />
          </div>

          {/* Tips */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">Tips for a great suggestion:</h4>
            <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
              <li>• Be specific about the problem you're solving</li>
              <li>• Explain the benefits and impact</li>
              <li>• Consider implementation feasibility</li>
              <li>• Use clear, professional language</li>
            </ul>
          </div>

          {/* Error Message */}
          {createSuggestionMutation.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-md">
              {createSuggestionMutation.error?.response?.data?.detail || 'Failed to create suggestion'}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.title.trim() || !formData.description.trim()}
              className="btn btn-primary"
            >
              {isSubmitting ? 'Creating...' : 'Create Suggestion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 