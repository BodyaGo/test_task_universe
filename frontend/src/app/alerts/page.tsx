'use client'

import { useState, useEffect } from 'react'
import { BellIcon, ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import DashboardLayout from '../../components/layout/DashboardLayout'

interface Alert {
  id: string
  title: string
  message: string
  type: 'threat' | 'mention' | 'sentiment' | 'system'
  severity: 'low' | 'medium' | 'high' | 'critical'
  created_at: string
  read: boolean
  source: string
  action_required: boolean
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unread' | 'high_priority'>('all')

  useEffect(() => {
    // Mock data for demonstration
    const mockAlerts: Alert[] = [
      {
        id: '1',
        title: 'High Threat Detected',
        message: 'Negative discussion about product quality detected in r/technology with high engagement',
        type: 'threat',
        severity: 'high',
        created_at: '2024-01-15T10:30:00Z',
        read: false,
        source: 'Reddit Monitor',
        action_required: true
      },
      {
        id: '2',
        title: 'Sentiment Drop Alert',
        message: 'Brand sentiment has dropped by 15% in the last 24 hours',
        type: 'sentiment',
        severity: 'medium',
        created_at: '2024-01-15T09:15:00Z',
        read: false,
        source: 'Sentiment Analysis',
        action_required: true
      },
      {
        id: '3',
        title: 'New Brand Mention',
        message: 'Your brand was mentioned in a popular thread with 500+ upvotes',
        type: 'mention',
        severity: 'low',
        created_at: '2024-01-15T08:45:00Z',
        read: true,
        source: 'Reddit Monitor',
        action_required: false
      },
      {
        id: '4',
        title: 'System Update',
        message: 'Monitoring system has been updated with new threat detection algorithms',
        type: 'system',
        severity: 'low',
        created_at: '2024-01-15T07:30:00Z',
        read: true,
        source: 'System',
        action_required: false
      },
      {
        id: '5',
        title: 'Critical Threat Alert',
        message: 'Potential PR crisis detected - multiple negative threads gaining traction',
        type: 'threat',
        severity: 'critical',
        created_at: '2024-01-15T06:00:00Z',
        read: false,
        source: 'Threat Detection',
        action_required: true
      }
    ]
    
    setTimeout(() => {
      setAlerts(mockAlerts)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'unread') return !alert.read
    if (filter === 'high_priority') return alert.severity === 'high' || alert.severity === 'critical'
    return true
  })

  const markAsRead = (alertId: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, read: true } : alert
    ))
  }

  const markAllAsRead = () => {
    setAlerts(alerts.map(alert => ({ ...alert, read: true })))
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-800 bg-red-100 border-red-200'
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default: return 'text-blue-600 bg-blue-50 border-blue-200'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'threat': return ExclamationTriangleIcon
      case 'mention': return BellIcon
      case 'sentiment': return CheckCircleIcon
      default: return BellIcon
    }
  }

  const unreadCount = alerts.filter(alert => !alert.read).length

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
            <h1 className="text-2xl font-semibold text-gray-900">
              Alerts
              {unreadCount > 0 && (
                <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  {unreadCount} unread
                </span>
              )}
            </h1>
            <p className="mt-2 text-sm text-gray-700">
              Stay informed about important events and threats related to your brand
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <button
              onClick={markAllAsRead}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Mark all as read
            </button>
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
            All Alerts
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'unread'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Unread ({unreadCount})
          </button>
          <button
            onClick={() => setFilter('high_priority')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'high_priority'
                ? 'bg-red-100 text-red-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            High Priority
          </button>
        </div>

        {/* Alerts List */}
        <div className="mt-8 space-y-4">
          {filteredAlerts.map((alert) => {
            const IconComponent = getTypeIcon(alert.type)
            return (
              <div
                key={alert.id}
                className={`border rounded-lg p-4 ${
                  alert.read ? 'bg-white' : 'bg-blue-50'
                } ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <IconComponent className="h-6 w-6" />
                  </div>
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className={`text-sm font-medium ${
                        alert.read ? 'text-gray-900' : 'text-gray-900 font-semibold'
                      }`}>
                        {alert.title}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          getSeverityColor(alert.severity)
                        }`}>
                          {alert.severity}
                        </span>
                        {alert.action_required && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Action Required
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">{alert.message}</p>
                    <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                      <div className="flex items-center space-x-4">
                        <span>Source: {alert.source}</span>
                        <span>{new Date(alert.created_at).toLocaleString()}</span>
                      </div>
                      {!alert.read && (
                        <button
                          onClick={() => markAsRead(alert.id)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Mark as read
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {filteredAlerts.length === 0 && (
          <div className="text-center py-12">
            <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No alerts match your current filter criteria.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}