import React, { useState } from 'react';
import { Suggestion } from '../types';
import { votesAPI, API_BASE_URL } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { ThumbsUp, ThumbsDown, User, Calendar } from 'lucide-react';
import { clsx } from 'clsx';
import axios from 'axios';

interface SuggestionCardProps {
  suggestion: Suggestion;
  onVoteUpdate?: (suggestionId: number, newVoteCount: number) => void;
  showActions?: boolean;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  onVoteUpdate,
  showActions = true
}) => {
  const { user } = useAuth();
  const [isVoting, setIsVoting] = useState(false);
  const [localVoteCount, setLocalVoteCount] = useState(suggestion.vote_count);
  const [userVote, setUserVote] = useState<boolean | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [status, setStatus] = useState(suggestion.status);
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState('');
  const [newStatus, setNewStatus] = useState('implemented');

  const handleVote = async (isUpvote: boolean) => {
    if (!user || isVoting) return;
    
    setIsVoting(true);
    try {
      const response = await votesAPI.create({
        suggestion_id: suggestion.id,
        is_upvote: isUpvote
      });
      
      setLocalVoteCount(response.vote_count);
      setUserVote(response.user_vote);
      onVoteUpdate?.(suggestion.id, response.vote_count);
    } catch (error) {
      console.error('Vote failed:', error);
    } finally {
      setIsVoting(false);
    }
  };

  const handleRemoveVote = async () => {
    if (!user || isVoting) return;
    
    setIsVoting(true);
    try {
      const response = await votesAPI.remove(suggestion.id);
      setLocalVoteCount(response.vote_count);
      setUserVote(null);
      onVoteUpdate?.(suggestion.id, response.vote_count);
    } catch (error) {
      console.error('Remove vote failed:', error);
    } finally {
      setIsVoting(false);
    }
  };

  const canVote = user && user.id !== suggestion.author_id;
  const canUpdateStatus = user && user.id === suggestion.author_id && status === 'active';

  const handleCardClick = () => {
    setShowModal(true);
  };

  const handleStatusUpdate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setStatusLoading(true);
    setStatusError('');
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.patch(
        `${API_BASE_URL}/suggestions/${suggestion.id}/status?new_status=${newStatus}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setStatus(res.data.status);
      setShowModal(false);
    } catch (err: any) {
      setStatusError(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setStatusLoading(false);
    }
  };

  return (
    <>
      <div
        className="card p-6 hover:shadow-lg dark:hover:shadow-gray-900/20 transition-shadow cursor-pointer"
        onClick={handleCardClick}
        tabIndex={0}
        role="button"
        aria-label="Open suggestion details"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200">
                {suggestion.category}
              </span>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {suggestion.title}
            </h3>
            
            <p className="text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">
              {suggestion.description}
            </p>
            
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <User className="h-4 w-4" />
                  <span>{suggestion.author.username}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>{new Date(suggestion.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            {/* Add a badge for status */}
            <div className="mt-2">
              <span className={clsx(
                "inline-block px-2 py-0.5 rounded text-xs font-semibold",
                status === 'active' && 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200',
                status === 'implemented' && 'bg-green-700 text-green-100 dark:bg-green-800 dark:text-green-200',
                status === 'rejected' && 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
              )}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
            </div>
          </div>
          
          {showActions && (
            <div className="flex flex-col items-center space-y-2 ml-4">
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => handleVote(true)}
                  disabled={!canVote || isVoting}
                  className={clsx(
                    "p-2 rounded-full transition-colors",
                    userVote === true 
                      ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400" 
                      : "text-gray-400 dark:text-gray-500 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20",
                    (!canVote || isVoting) && "opacity-50 cursor-not-allowed"
                  )}
                >
                  <ThumbsUp className="h-5 w-5" />
                </button>
                
                <span className="text-lg font-semibold text-gray-900 dark:text-white min-w-[2rem] text-center">
                  {localVoteCount}
                </span>
                
                <button
                  onClick={() => handleVote(false)}
                  disabled={!canVote || isVoting}
                  className={clsx(
                    "p-2 rounded-full transition-colors",
                    userVote === false 
                      ? "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400" 
                      : "text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20",
                    (!canVote || isVoting) && "opacity-50 cursor-not-allowed"
                  )}
                >
                  <ThumbsDown className="h-5 w-5" />
                </button>
              </div>
              
              {userVote !== null && canVote && (
                <button
                  onClick={handleRemoveVote}
                  disabled={isVoting}
                  className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
                >
                  Remove vote
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      {/* Modal for status update */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="rounded-xl shadow-2xl p-8 w-full max-w-2xl relative flex flex-col space-y-6 border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-[#171717]">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-2xl"
              onClick={() => setShowModal(false)}
              aria-label="Close"
            >
              ×
            </button>
            <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">Suggestion Details</h2>
            <div className="flex flex-col md:flex-row md:space-x-8 space-y-4 md:space-y-0">
              <div className="flex-1 space-y-2">
                <div className="font-semibold text-lg text-gray-700 dark:text-gray-200">{suggestion.title}</div>
                <div className="text-gray-500 dark:text-gray-400 text-base mb-2 whitespace-pre-line">{suggestion.description}</div>
                <div className="mb-2">
                  <span className="font-medium text-gray-900 dark:text-white">Category:</span> <span className="text-gray-900 dark:text-white">{suggestion.category}</span>
                </div>
                <div className="mb-2">
                  <span className="font-medium text-gray-900 dark:text-white">Status:</span> <span className="text-gray-900 dark:text-white">{status.charAt(0).toUpperCase() + status.slice(1)}</span>
                </div>
              </div>
              {canUpdateStatus && (
                <form className="flex-1 space-y-4" onSubmit={handleStatusUpdate}>
                  <label className="block text-base font-medium text-gray-700 dark:text-gray-300 mb-1">Update Status</label>
                  <select
                    className="input text-base"
                    value={newStatus}
                    onChange={e => setNewStatus(e.target.value)}
                    disabled={statusLoading}
                  >
                    <option value="implemented">Implemented</option>
                    <option value="rejected">Rejected</option>
                  </select>
                  <button
                    className="btn btn-primary mt-2 w-full text-base py-2"
                    type="submit"
                    disabled={statusLoading}
                  >
                    {statusLoading ? 'Updating...' : 'Update Status'}
                  </button>
                  {statusError && <div className="text-red-500 mt-2 text-sm">{statusError}</div>}
                </form>
              )}
            </div>
            {!canUpdateStatus && (
              <div className="text-gray-500 dark:text-gray-400 text-base mt-4">Only the author can update status when suggestion is active.</div>
            )}
          </div>
        </div>
      )}
    </>
  );
}; 