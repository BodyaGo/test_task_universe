'use client'

import { useState, useEffect } from 'react'
import { 
  ChartBarIcon, 
  ExclamationTriangleIcon, 
  ChatBubbleLeftRightIcon,
  EyeIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'
import DashboardLayout from '../components/layout/DashboardLayout'
import StatsCard from '../components/dashboard/StatsCard'
import ThreatsList from '../components/dashboard/ThreatsList'
import SentimentChart from '../components/dashboard/SentimentChart'
import RecentMentions from '../components/dashboard/RecentMentions'
import { fetchMonitoringStats, fetchHighPriorityThreats, fetchRecentMentions, MonitoringStats, BrandMention } from '../lib/api'

export default function Dashboard() {
  const [stats, setStats] = useState<MonitoringStats | null>(null)
  const [threats, setThreats] = useState<BrandMention[]>([])
  const [mentions, setMentions] = useState<BrandMention[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsData, threatsData, mentionsData] = await Promise.all([
        fetchMonitoringStats(),
        fetchHighPriorityThreats(),
        fetchRecentMentions()
      ])
      
      setStats(statsData)
      setThreats(threatsData)
      setMentions(mentionsData)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
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
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Apple Brand Monitor Dashboard</h1>
            <p className="text-gray-600">Real-time monitoring of Apple brand mentions on Reddit</p>
          </div>
          <button
            onClick={loadDashboardData}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <EyeIcon className="-ml-1 mr-2 h-4 w-4" />
            Refresh
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Apple Mentions"
            value={stats?.total_mentions || 0}
            icon={ChatBubbleLeftRightIcon}
            color="blue"
            change="+12%"
            changeType="increase"
          />
          <StatsCard
            title="Negative Mentions"
            value={threats.filter(t => t.threat_analysis?.threat_level === 'high').length}
            icon={ExclamationTriangleIcon}
            color="red"
            change="-5%"
            changeType="decrease"
          />
          <StatsCard
            title="Positive Feedback"
            value={`${Math.round((stats?.sentiment_distribution?.positive || 0) / Math.max(stats?.total_mentions || 1, 1) * 100)}%`}
            icon={ChartBarIcon}
            color="green"
            change="+8%"
            changeType="increase"
          />
          <StatsCard
            title="Active Monitoring"
            value="24/7"
            icon={EyeIcon}
            color="purple"
            change="100%"
            changeType="neutral"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-6">
            <SentimentChart data={stats} />
            <RecentMentions mentions={mentions} />
          </div>

          {/* Right Column - Threats */}
          <div className="lg:col-span-1">
            <ThreatsList threats={threats} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
