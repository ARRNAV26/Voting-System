import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { suggestionsAPI } from '../lib/api';
import { SuggestionCard } from '../components/SuggestionCard';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';
import { Suggestion, VoteUpdateMessage } from '../types';
import { TrendingUp, Trophy } from 'lucide-react';

export const TopSuggestionsPage: React.FC = () => {
  const { user } = useAuth();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [limit, setLimit] = useState(10);
  const limitOptions = [5, 10, 15, 30, 50, 100];

  // Fetch top suggestions
  const { data: fetchedSuggestions, isLoading } = useQuery({
    queryKey: ['top-suggestions', limit],
    queryFn: () => suggestionsAPI.getTop(limit),
  });

  // Update local state when data is fetched
  useEffect(() => {
    if (fetchedSuggestions) {
      setSuggestions(fetchedSuggestions);
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
        ).sort((a, b) => b.vote_count - a.vote_count) // Re-sort by vote count
      );
    },
  });

  const handleVoteUpdate = (suggestionId: number, newVoteCount: number) => {
    setSuggestions(prev => 
      prev.map(suggestion => 
        suggestion.id === suggestionId 
          ? { ...suggestion, vote_count: newVoteCount }
          : suggestion
      ).sort((a, b) => b.vote_count - a.vote_count) // Re-sort by vote count
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-yellow-100 rounded-lg">
            <Trophy className="h-6 w-6 text-yellow-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Top Suggestions</h1>
            <p className="text-gray-600">
              {/* You can add connection status here if needed */}
            </p>
          </div>
        </div>
        <div className="text-sm text-gray-500">
          {suggestions.length} suggestion{suggestions.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Limit Selector */}
      <div className="card p-4">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">
            Show top:
          </label>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="input w-24"
          >
            {limitOptions.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          <span className="text-sm text-gray-500">suggestions</span>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}

      {/* Suggestions List */}
      {!isLoading && (
        <div className="space-y-4">
          {suggestions.length === 0 ? (
            <div className="text-center py-12">
              <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No suggestions yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start by creating some suggestions and getting votes!
              </p>
            </div>
          ) : (
            suggestions.map((suggestion, index) => (
              <div key={suggestion.id} className="relative">
                {/* Rank Badge */}
                <div className="absolute -left-2 -top-2 z-10">
                  <div className={`
                    flex items-center justify-center w-8 h-8 rounded-full text-white font-bold text-sm
                    ${index === 0 ? 'bg-yellow-500' : ''}
                    ${index === 1 ? 'bg-gray-400' : ''}
                    ${index === 2 ? 'bg-orange-500' : ''}
                    ${index > 2 ? 'bg-gray-300' : ''}
                  `}>
                    {index + 1}
                  </div>
                </div>
                
                <SuggestionCard
                  suggestion={suggestion}
                  onVoteUpdate={handleVoteUpdate}
                />
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}; 