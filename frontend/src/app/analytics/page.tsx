'use client'

import { useState, useEffect } from 'react'
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, CalendarIcon } from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import DashboardLayout from '../../components/layout/DashboardLayout'

interface AnalyticsData {
  mentions_over_time: Array<{
    date: string
    mentions: number
    positive: number
    negative: number
    neutral: number
  }>
  sentiment_distribution: {
    positive: number
    negative: number
    neutral: number
  }
  threat_levels: {
    low: number
    medium: number
    high: number
    critical: number
  }
  top_subreddits: Array<{
    name: string
    mentions: number
    sentiment_score: number
  }>
  keyword_performance: Array<{
    keyword: string
    mentions: number
    trend: 'up' | 'down' | 'stable'
    change: number
  }>
  engagement_metrics: {
    total_upvotes: number
    total_comments: number
    average_engagement: number
    viral_posts: number
  }
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  useEffect(() => {
    // Mock data for demonstration
    const mockAnalytics: AnalyticsData = {
      mentions_over_time: [
        { date: '2024-01-01', mentions: 45, positive: 20, negative: 15, neutral: 10 },
        { date: '2024-01-02', mentions: 52, positive: 25, negative: 12, neutral: 15 },
        { date: '2024-01-03', mentions: 38, positive: 18, negative: 8, neutral: 12 },
        { date: '2024-01-04', mentions: 67, positive: 30, negative: 20, neutral: 17 },
        { date: '2024-01-05', mentions: 73, positive: 35, negative: 18, neutral: 20 },
        { date: '2024-01-06', mentions: 41, positive: 22, negative: 9, neutral: 10 },
        { date: '2024-01-07', mentions: 59, positive: 28, negative: 16, neutral: 15 },
        { date: '2024-01-08', mentions: 84, positive: 40, negative: 25, neutral: 19 },
        { date: '2024-01-09', mentions: 76, positive: 38, negative: 22, neutral: 16 },
        { date: '2024-01-10', mentions: 63, positive: 32, negative: 14, neutral: 17 },
        { date: '2024-01-11', mentions: 55, positive: 28, negative: 12, neutral: 15 },
        { date: '2024-01-12', mentions: 48, positive: 25, negative: 10, neutral: 13 },
        { date: '2024-01-13', mentions: 71, positive: 35, negative: 18, neutral: 18 },
        { date: '2024-01-14', mentions: 89, positive: 45, negative: 24, neutral: 20 },
        { date: '2024-01-15', mentions: 92, positive: 48, negative: 26, neutral: 18 }
      ],
      sentiment_distribution: {
        positive: 485,
        negative: 249,
        neutral: 266
      },
      threat_levels: {
        low: 156,
        medium: 89,
        high: 34,
        critical: 8
      },
      top_subreddits: [
        { name: 'r/technology', mentions: 145, sentiment_score: -0.2 },
        { name: 'r/reviews', mentions: 98, sentiment_score: 0.4 },
        { name: 'r/buyitforlife', mentions: 76, sentiment_score: 0.1 },
        { name: 'r/frugal', mentions: 65, sentiment_score: -0.1 },
        { name: 'r/ProductReviews', mentions: 54, sentiment_score: 0.3 },
        { name: 'r/CustomerService', mentions: 43, sentiment_score: -0.5 },
        { name: 'r/gadgets', mentions: 38, sentiment_score: 0.2 }
      ],
      keyword_performance: [
        { keyword: 'quality', mentions: 234, trend: 'down', change: -12 },
        { keyword: 'price', mentions: 189, trend: 'up', change: 8 },
        { keyword: 'customer service', mentions: 156, trend: 'down', change: -15 },
        { keyword: 'features', mentions: 134, trend: 'stable', change: 2 },
        { keyword: 'reliability', mentions: 98, trend: 'up', change: 18 },
        { keyword: 'support', mentions: 87, trend: 'down', change: -8 }
      ],
      engagement_metrics: {
        total_upvotes: 12450,
        total_comments: 3890,
        average_engagement: 16.3,
        viral_posts: 5
      }
    }
    
    setTimeout(() => {
      setAnalytics(mockAnalytics)
      setLoading(false)
    }, 1000)
  }, [timeRange])

  const COLORS = ['#10B981', '#EF4444', '#6B7280', '#F59E0B']
  const SENTIMENT_COLORS = ['#10B981', '#EF4444', '#6B7280']

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  if (!analytics) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No analytics data available</h3>
        </div>
      </DashboardLayout>
    )
  }

  const sentimentData = [
    { name: 'Positive', value: analytics.sentiment_distribution.positive, color: '#10B981' },
    { name: 'Negative', value: analytics.sentiment_distribution.negative, color: '#EF4444' },
    { name: 'Neutral', value: analytics.sentiment_distribution.neutral, color: '#6B7280' }
  ]

  const threatData = [
    { name: 'Low', value: analytics.threat_levels.low, color: '#10B981' },
    { name: 'Medium', value: analytics.threat_levels.medium, color: '#F59E0B' },
    { name: 'High', value: analytics.threat_levels.high, color: '#EF4444' },
    { name: 'Critical', value: analytics.threat_levels.critical, color: '#DC2626' }
  ]

  return (
    <DashboardLayout>
      <div className="px-4 sm:px-6 lg:px-8 py-8">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div className="sm:flex-auto">
            <h1 className="text-2xl font-semibold text-gray-900">Brand Analytics</h1>
            <p className="mt-2 text-sm text-gray-700">
              Comprehensive analytics and insights about your brand mentions
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as typeof timeRange)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Mentions</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {analytics.sentiment_distribution.positive + analytics.sentiment_distribution.negative + analytics.sentiment_distribution.neutral}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ArrowTrendingUpIcon className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Engagement</dt>
                    <dd className="text-lg font-medium text-gray-900">{analytics.engagement_metrics.average_engagement}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ArrowTrendingUpIcon className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Upvotes</dt>
                    <dd className="text-lg font-medium text-gray-900">{analytics.engagement_metrics.total_upvotes.toLocaleString()}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ArrowTrendingUpIcon className="h-6 w-6 text-purple-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Viral Posts</dt>
                    <dd className="text-lg font-medium text-gray-900">{analytics.engagement_metrics.viral_posts}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Mentions Over Time */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Mentions Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analytics.mentions_over_time}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Area type="monotone" dataKey="positive" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
                <Area type="monotone" dataKey="neutral" stackId="1" stroke="#6B7280" fill="#6B7280" fillOpacity={0.6} />
                <Area type="monotone" dataKey="negative" stackId="1" stroke="#EF4444" fill="#EF4444" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment Distribution */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index % SENTIMENT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Threat Levels */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Threat Level Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={threatData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8">
                  {threatData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Top Subreddits */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Top Subreddits</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.top_subreddits} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="mentions" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Keyword Performance */}
        <div className="mt-8 bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Keyword Performance</h3>
          </div>
          <div className="px-6 py-4">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Keyword
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Mentions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trend
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Change
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analytics.keyword_performance.map((keyword, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {keyword.keyword}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {keyword.mentions}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {keyword.trend === 'up' && <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />}
                          {keyword.trend === 'down' && <ArrowTrendingDownIcon className="h-4 w-4 text-red-500 mr-1" />}
                          {keyword.trend === 'stable' && <div className="h-4 w-4 bg-gray-400 rounded-full mr-1" />}
                          <span className={`text-sm ${
                            keyword.trend === 'up' ? 'text-green-600' : 
                            keyword.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                          }`}>
                            {keyword.trend}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`${
                          keyword.change > 0 ? 'text-green-600' : 
                          keyword.change < 0 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {keyword.change > 0 ? '+' : ''}{keyword.change}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}