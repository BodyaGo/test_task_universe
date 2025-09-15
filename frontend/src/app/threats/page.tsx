'use client'

import { useState, useEffect } from 'react'
import { ExclamationTriangleIcon, ShieldExclamationIcon, ClockIcon, UserIcon, LinkIcon } from '@heroicons/react/24/outline'
import DashboardLayout from '../../components/layout/DashboardLayout'

interface Threat {
  id: string
  title: string
  description: string
  threat_level: 'low' | 'medium' | 'high' | 'critical'
  status: 'new' | 'investigating' | 'resolved' | 'dismissed'
  source: string
  author: string
  subreddit: string
  created_at: string
  updated_at: string
  url: string
  sentiment_score: number
  engagement: {
    upvotes: number
    comments: number
    shares: number
  }
  keywords: string[]
  ai_recommendation: string
}

export default function ThreatsPage() {
  const [threats, setThreats] = useState<Threat[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'new'>('all')
  const [sortBy, setSortBy] = useState<'date' | 'threat_level' | 'engagement'>('date')

  useEffect(() => {
    // Mock data for demonstration
    const mockThreats: Threat[] = [
      {
        id: '1',
        title: 'Viral complaint about product quality',
        description: 'A detailed post about declining product quality is gaining significant traction with multiple users sharing similar experiences.',
        threat_level: 'critical',
        status: 'new',
        source: 'Reddit',
        author: 'disappointed_customer',
        subreddit: 'r/technology',
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:30:00Z',
        url: 'https://reddit.com/r/technology/comments/example1',
        sentiment_score: -0.85,
        engagement: {
          upvotes: 1250,
          comments: 340,
          shares: 89
        },
        keywords: ['quality', 'defective', 'disappointed'],
        ai_recommendation: 'Immediate response required. Consider public statement addressing quality concerns and outline improvement measures.'
      },
      {
        id: '2',
        title: 'Customer service complaint thread',
        description: 'Multiple users discussing poor customer service experiences in a growing thread.',
        threat_level: 'high',
        status: 'investigating',
        source: 'Reddit',
        author: 'frustrated_user',
        subreddit: 'r/CustomerService',
        created_at: '2024-01-15T09:15:00Z',
        updated_at: '2024-01-15T11:00:00Z',
        url: 'https://reddit.com/r/CustomerService/comments/example2',
        sentiment_score: -0.65,
        engagement: {
          upvotes: 450,
          comments: 120,
          shares: 25
        },
        keywords: ['customer service', 'rude', 'unhelpful'],
        ai_recommendation: 'Monitor closely and prepare customer service improvement communication. Consider reaching out to affected customers.'
      },
      {
        id: '3',
        title: 'Pricing concerns discussion',
        description: 'Users discussing recent price increases and comparing with competitors.',
        threat_level: 'medium',
        status: 'new',
        source: 'Reddit',
        author: 'budget_conscious',
        subreddit: 'r/frugal',
        created_at: '2024-01-15T08:45:00Z',
        updated_at: '2024-01-15T08:45:00Z',
        url: 'https://reddit.com/r/frugal/comments/example3',
        sentiment_score: -0.35,
        engagement: {
          upvotes: 180,
          comments: 45,
          shares: 8
        },
        keywords: ['expensive', 'overpriced', 'competitors'],
        ai_recommendation: 'Monitor for escalation. Consider preparing value proposition messaging if discussion grows.'
      },
      {
        id: '4',
        title: 'Minor feature request complaint',
        description: 'User expressing frustration about missing features compared to competitors.',
        threat_level: 'low',
        status: 'dismissed',
        source: 'Reddit',
        author: 'tech_enthusiast',
        subreddit: 'r/ProductReviews',
        created_at: '2024-01-14T15:20:00Z',
        updated_at: '2024-01-15T09:00:00Z',
        url: 'https://reddit.com/r/ProductReviews/comments/example4',
        sentiment_score: -0.15,
        engagement: {
          upvotes: 25,
          comments: 8,
          shares: 1
        },
        keywords: ['features', 'missing', 'improvement'],
        ai_recommendation: 'Low priority. Consider for future product roadmap discussions.'
      }
    ]
    
    setTimeout(() => {
      setThreats(mockThreats)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredThreats = threats.filter(threat => {
    if (filter === 'critical') return threat.threat_level === 'critical'
    if (filter === 'high') return threat.threat_level === 'high' || threat.threat_level === 'critical'
    if (filter === 'new') return threat.status === 'new'
    return true
  })

  const sortedThreats = [...filteredThreats].sort((a, b) => {
    if (sortBy === 'threat_level') {
      const levels = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 }
      return levels[b.threat_level] - levels[a.threat_level]
    }
    if (sortBy === 'engagement') {
      return (b.engagement.upvotes + b.engagement.comments) - (a.engagement.upvotes + a.engagement.comments)
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  const updateThreatStatus = (threatId: string, newStatus: Threat['status']) => {
    setThreats(threats.map(threat => 
      threat.id === threatId 
        ? { ...threat, status: newStatus, updated_at: new Date().toISOString() }
        : threat
    ))
  }

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-800 bg-red-100 border-red-300'
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default: return 'text-green-600 bg-green-50 border-green-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'text-blue-600 bg-blue-100'
      case 'investigating': return 'text-yellow-600 bg-yellow-100'
      case 'resolved': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
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
        <div className="sm:flex sm:items-center sm:justify-between">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">Threat Management</h1>
            <p className="mt-2 text-sm text-gray-700">
              Monitor and manage potential threats to your brand reputation
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-3">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="date">Sort by Date</option>
              <option value="threat_level">Sort by Threat Level</option>
              <option value="engagement">Sort by Engagement</option>
            </select>
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
            All Threats
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'critical'
                ? 'bg-red-100 text-red-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Critical
          </button>
          <button
            onClick={() => setFilter('high')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'high'
                ? 'bg-red-100 text-red-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            High Priority
          </button>
          <button
            onClick={() => setFilter('new')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'new'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            New
          </button>
        </div>

        {/* Threats List */}
        <div className="mt-8 space-y-6">
          {sortedThreats.map((threat) => (
            <div key={threat.id} className={`border rounded-lg p-6 ${getThreatLevelColor(threat.threat_level)}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <ExclamationTriangleIcon className="h-6 w-6" />
                    <h3 className="text-lg font-medium text-gray-900">{threat.title}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      getThreatLevelColor(threat.threat_level)
                    }`}>
                      {threat.threat_level}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      getStatusColor(threat.status)
                    }`}>
                      {threat.status}
                    </span>
                  </div>
                  
                  <p className="mt-2 text-gray-600">{threat.description}</p>
                  
                  <div className="mt-3 flex items-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {threat.author}
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {new Date(threat.created_at).toLocaleDateString()}
                    </div>
                    <span>{threat.subreddit}</span>
                    <div className="flex items-center space-x-2">
                      <span>↑ {threat.engagement.upvotes}</span>
                      <span>💬 {threat.engagement.comments}</span>
                      <span>↗ {threat.engagement.shares}</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 flex flex-wrap gap-2">
                    {threat.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                  
                  <div className="mt-4 p-3 bg-blue-50 rounded-md">
                    <div className="flex items-start">
                      <ShieldExclamationIcon className="h-5 w-5 text-blue-400 mt-0.5 mr-2" />
                      <div>
                        <h4 className="text-sm font-medium text-blue-900">AI Recommendation</h4>
                        <p className="text-sm text-blue-700 mt-1">{threat.ai_recommendation}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="ml-6 flex flex-col space-y-2">
                  <a
                    href={threat.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <LinkIcon className="h-4 w-4 mr-1" />
                    View Source
                  </a>
                  
                  <select
                    value={threat.status}
                    onChange={(e) => updateThreatStatus(threat.id, e.target.value as Threat['status'])}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option value="new">New</option>
                    <option value="investigating">Investigating</option>
                    <option value="resolved">Resolved</option>
                    <option value="dismissed">Dismissed</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>

        {sortedThreats.length === 0 && (
          <div className="text-center py-12">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No threats found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No threats match your current filter criteria.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}