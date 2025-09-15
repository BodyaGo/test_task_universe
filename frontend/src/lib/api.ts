import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Types
export interface BrandMention {
  id: string
  reddit_post: {
    id: string
    title: string
    content: string
    author: string
    subreddit: string
    url: string
    score: number
    num_comments: number
    created_utc: string
    post_type: string
    permalink: string
  }
  sentiment_analysis: {
    sentiment: 'positive' | 'negative' | 'neutral'
    confidence: number
    positive_score: number
    negative_score: number
    neutral_score: number
  }
  threat_analysis: {
    threat_level: 'low' | 'medium' | 'high' | 'critical'
    threat_score: number
    threat_categories: string[]
    keywords_matched: string[]
    context_analysis: string
    potential_impact: string
  }
  response_recommendation?: {
    action_type: string
    priority: number
    message_template: string
    escalation_needed: boolean
    reasoning: string
  }
  processed_at: string
  is_reviewed: boolean
  notes: string
  tags: string[]
}

export interface MonitoringStats {
  total_mentions: number
  threat_distribution: Record<string, number>
  sentiment_distribution: Record<string, number>
  top_subreddits: Array<{
    subreddit: string
    count: number
  }>
  trending_keywords: string[]
  last_updated: string
}

export interface APIResponse<T = unknown> {
  success: boolean
  message: string
  data: T
  error?: string
  timestamp: string
}

// API Functions
export const fetchMonitoringStats = async (): Promise<MonitoringStats> => {
  try {
    const response = await api.get<APIResponse<MonitoringStats>>('/monitoring/stats')
    return response.data.data
  } catch (error) {
    console.error('Error fetching monitoring stats:', error)
    // Return default stats on error
    return {
      total_mentions: 0,
      threat_distribution: {},
      sentiment_distribution: {},
      top_subreddits: [],
      trending_keywords: [],
      last_updated: new Date().toISOString()
    }
  }
}

export const fetchHighPriorityThreats = async (limit: number = 20): Promise<BrandMention[]> => {
  try {
    const response = await api.get<APIResponse<{ threats: BrandMention[] }>>(`/mentions/threats/high-priority?limit=${limit}`)
    return response.data.data.threats || []
  } catch (error) {
    console.error('Error fetching high priority threats:', error)
    return []
  }
}

export const fetchRecentMentions = async (limit: number = 50): Promise<BrandMention[]> => {
  const response = await api.get<APIResponse<{ mentions: BrandMention[] }>>(`/mentions/?limit=${limit}`)
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch recent mentions')
  }
  return response.data.data.mentions
}

export const fetchMentions = async (params: {
  limit?: number
  skip?: number
  threat_level?: string
  sentiment?: string
  subreddit?: string
  start_date?: string
  end_date?: string
}): Promise<{ mentions: BrandMention[], total: number }> => {
  try {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString())
      }
    })
    
    const response = await api.get<APIResponse<{ mentions: BrandMention[], total: number }>>(`/mentions?${queryParams}`)
    return response.data.data
  } catch (error) {
    console.error('Error fetching mentions:', error)
    return { mentions: [], total: 0 }
  }
}

export const fetchMentionById = async (id: string): Promise<BrandMention | null> => {
  try {
    const response = await api.get<APIResponse<BrandMention>>(`/mentions/${id}`)
    return response.data.data
  } catch (error) {
    console.error('Error fetching mention:', error)
    return null
  }
}

export const triggerManualScan = async (): Promise<{ mentions_found: number }> => {
  try {
    const response = await api.post<APIResponse<{ mentions_found: number }>>('/mentions/scan')
    return response.data.data
  } catch (error) {
    console.error('Error triggering manual scan:', error)
    throw error
  }
}

export const scanSpecificPost = async (postId: string): Promise<BrandMention> => {
  try {
    const response = await api.post<APIResponse<BrandMention>>(`/mentions/scan/${postId}`)
    return response.data.data
  } catch (error) {
    console.error('Error scanning specific post:', error)
    throw error
  }
}

export const markMentionReviewed = async (id: string, notes?: string): Promise<void> => {
  try {
    await api.patch(`/mentions/${id}/review`, { notes })
  } catch (error) {
    console.error('Error marking mention as reviewed:', error)
    throw error
  }
}

export const fetchMonitoringStatus = async (): Promise<{
  monitor_initialized: boolean
  scheduler_running: boolean
  reddit_client_status: string
  ai_analyzer_status: string
}> => {
  try {
    const response = await api.get('/monitoring/status')
    return response.data.data
  } catch (error) {
    console.error('Error fetching monitoring status:', error)
    return {
      monitor_initialized: false,
      scheduler_running: false,
      reddit_client_status: 'disconnected',
      ai_analyzer_status: 'not_ready'
    }
  }
}

export const startMonitoring = async (): Promise<void> => {
  try {
    await api.post('/monitoring/start')
  } catch (error) {
    console.error('Error starting monitoring:', error)
    throw error
  }
}

export const stopMonitoring = async (): Promise<void> => {
  try {
    await api.post('/monitoring/stop')
  } catch (error) {
    console.error('Error stopping monitoring:', error)
    throw error
  }
}

export const fetchAnalyticsOverview = async (days: number = 7): Promise<unknown> => {
  try {
    const response = await api.get(`/analytics/overview?days=${days}`)
    return response.data.data
  } catch (error) {
    console.error('Error fetching analytics overview:', error)
    return null
  }
}

export const fetchSentimentTrends = async (days: number = 30, granularity: string = 'daily'): Promise<unknown> => {
  try {
    const response = await api.get(`/analytics/sentiment-trends?days=${days}&granularity=${granularity}`)
    return response.data.data
  } catch (error) {
    console.error('Error fetching sentiment trends:', error)
    return null
  }
}

export const fetchThreatAnalysis = async (days: number = 7, minThreatScore: number = 0.0): Promise<unknown> => {
  try {
    const response = await api.get(`/analytics/threat-analysis?days=${days}&min_threat_score=${minThreatScore}`)
    return response.data.data
  } catch (error) {
    console.error('Error fetching threat analysis:', error)
    return null
  }
}

export default api