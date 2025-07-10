import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { suggestionsAPI } from '../lib/api';
import { SuggestionCard } from '../components/SuggestionCard';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';
import { Suggestion, VoteUpdateMessage, SuggestionUpdateMessage } from '../types';
import { Filter, Search } from 'lucide-react';

export const HomePage: React.FC = () => {
  const { user } = useAuth();
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch suggestions
  const { data: fetchedSuggestions, isLoading, refetch } = useQuery({
    queryKey: ['suggestions', filterCategory, filterStatus],
    queryFn: () => suggestionsAPI.getAll({
      category: filterCategory || undefined,
      status: filterStatus || undefined,
    }),
  });

  // Update local state when data is fetched
  useEffect(() => {
    if (fetchedSuggestions) {
      setSuggestions(fetchedSuggestions);
      setIsConnected(true); // Mark as connected when suggestions are loaded
    }
  }, [fetchedSuggestions]);

  // WebSocket connection for real-time updates
  useWebSocket(user?.id, {
    onVoteUpdate: (data: VoteUpdateMessage) => {
      setSuggestions(prev => 
        prev.map(suggestion => 
          suggestion.id === data.suggestion_id 
            ? { ...suggestion, vote_count: data.new_vote_count }
            : suggestion
        )
      );
    },
    onSuggestionUpdate: (data: SuggestionUpdateMessage) => {
      setSuggestions(prev => 
        prev.map(suggestion => 
          suggestion.id === data.suggestion.id 
            ? data.suggestion
            : suggestion
        )
      );
    },
    onNewSuggestion: (data: any) => {
      const newSuggestion: Suggestion = {
        id: data.id,
        title: data.title,
        description: data.description,
        category: data.category,
        status: data.status,
        author_id: data.author_id,
        vote_count: data.vote_count,
        created_at: data.created_at,
        author: data.author,
      };
      setSuggestions(prev => [newSuggestion, ...prev]);
    },
  });

  // Filter suggestions based on search term
  const filteredSuggestions = suggestions.filter(suggestion =>
    suggestion.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    suggestion.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    suggestion.author.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleVoteUpdate = (suggestionId: number, newVoteCount: number) => {
    setSuggestions(prev => 
      prev.map(suggestion => 
        suggestion.id === suggestionId 
          ? { ...suggestion, vote_count: newVoteCount }
          : suggestion
      )
    );
  };

  const categories = ['All', 'Feature', 'Bug Fix', 'Improvement', 'Documentation', 'Other'];
  const statuses = ['All', 'active', 'implemented', 'rejected'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">All Suggestions</h1>
          <p className="text-gray-600 dark:text-gray-300">
            {isConnected ? '🟢 Connected' : '🔴 Connecting...'}
          </p>
        </div>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {filteredSuggestions.length} suggestion{filteredSuggestions.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row md:items-end md:space-x-4 space-y-4 md:space-y-0 w-full">
          {/* Search */}
          <div className="relative flex-1 min-w-[180px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search suggesti..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Category Filter */}
          <div className="flex-1 min-w-[140px]">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Category
            </label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="input"
            >
              {categories.map(category => (
                <option key={category} value={category === 'All' ? '' : category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex-1 min-w-[140px]">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input"
            >
              {statuses.map(status => (
                <option key={status} value={status === 'All' ? '' : status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Clear Filters */}
          <div className="flex items-end">
            <button
              onClick={() => {
                setFilterCategory('');
                setFilterStatus('');
                setSearchTerm('');
              }}
              className="btn btn-secondary w-full md:w-auto"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400"></div>
        </div>
      )}

      {/* Suggestions List */}
      {!isLoading && (
        <div className="space-y-4">
          {filteredSuggestions.length === 0 ? (
            <div className="text-center py-12">
              <Filter className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No suggestions found</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Try adjusting your search or filter criteria.
              </p>
            </div>
          ) : (
            filteredSuggestions.map(suggestion => (
              <SuggestionCard
                key={suggestion.id}
                suggestion={suggestion}
                onVoteUpdate={handleVoteUpdate}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}; 