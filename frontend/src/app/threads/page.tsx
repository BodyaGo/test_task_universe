'use client'

import { useState, useEffect } from 'react'
import { ChatBubbleLeftRightIcon, UserIcon, ClockIcon } from '@heroicons/react/24/outline'
import DashboardLayout from '../../components/layout/DashboardLayout'

interface Thread {
  id: string
  title: string
  author: string
  subreddit: string
  created_at: string
  replies_count: number
  sentiment: 'positive' | 'negative' | 'neutral'
  threat_level: 'low' | 'medium' | 'high' | 'critical'
  content: string
  url: string
}

export default function ThreadsPage() {
  const [threads, setThreads] = useState<Thread[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'high_threat' | 'negative'>('all')

  useEffect(() => {
    // Mock data for demonstration
    const mockThreads: Thread[] = [
      {
        id: '1',
        title: 'Discussion about our brand quality',
        author: 'user123',
        subreddit: 'r/technology',
        created_at: '2024-01-15T10:30:00Z',
        replies_count: 45,
        sentiment: 'negative',
        threat_level: 'high',
        content: 'I\'ve been using this brand for years, but lately the quality has really declined...',
        url: 'https://reddit.com/r/technology/comments/example1'
      },
      {
        id: '2',
        title: 'Great experience with customer service',
        author: 'happycustomer',
        subreddit: 'r/reviews',
        created_at: '2024-01-15T09:15:00Z',
        replies_count: 12,
        sentiment: 'positive',
        threat_level: 'low',
        content: 'Just wanted to share my positive experience with their customer support team...',
        url: 'https://reddit.com/r/reviews/comments/example2'
      },
      {
        id: '3',
        title: 'Product comparison thread',
        author: 'reviewer456',
        subreddit: 'r/buyitforlife',
        created_at: '2024-01-15T08:45:00Z',
        replies_count: 78,
        sentiment: 'neutral',
        threat_level: 'medium',
        content: 'Comparing different brands in this category. Here\'s my analysis...',
        url: 'https://reddit.com/r/buyitforlife/comments/example3'
      }
    ]
    
    setTimeout(() => {
      setThreads(mockThreads)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredThreads = threads.filter(thread => {
    if (filter === 'high_threat') return thread.threat_level === 'high' || thread.threat_level === 'critical'
    if (filter === 'negative') return thread.sentiment === 'negative'
    return true
  })

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100'
      case 'negative': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-800 bg-red-200'
      case 'high': return 'text-red-600 bg-red-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-green-600 bg-green-100'
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8 py-8">
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">Discussion Threads</h1>
            <p className="mt-2 text-sm text-gray-700">
              Monitor Reddit threads and discussions mentioning your brand
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="mt-6 flex space-x-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'all'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            All Threads
          </button>
          <button
            onClick={() => setFilter('high_threat')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'high_threat'
                ? 'bg-red-100 text-red-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            High Threat
          </button>
          <button
            onClick={() => setFilter('negative')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'negative'
                ? 'bg-red-100 text-red-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Negative Sentiment
          </button>
        </div>

        {/* Threads List */}
        <div className="mt-8 space-y-6">
          {filteredThreads.map((thread) => (
            <div key={thread.id} className="bg-white shadow rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <ChatBubbleLeftRightIcon className="h-5 w-5 text-gray-400" />
                    <h3 className="text-lg font-medium text-gray-900">
                      <a href={thread.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600">
                        {thread.title}
                      </a>
                    </h3>
                  </div>
                  
                  <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {thread.author}
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {new Date(thread.created_at).toLocaleDateString()}
                    </div>
                    <span>{thread.subreddit}</span>
                    <span>{thread.replies_count} replies</span>
                  </div>
                  
                  <p className="mt-3 text-gray-600 line-clamp-2">{thread.content}</p>
                </div>
                
                <div className="ml-6 flex flex-col space-y-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    getSentimentColor(thread.sentiment)
                  }`}>
                    {thread.sentiment}
                  </span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    getThreatColor(thread.threat_level)
                  }`}>
                    {thread.threat_level} threat
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredThreads.length === 0 && (
          <div className="text-center py-12">
            <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No threads found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No discussion threads match your current filter criteria.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}