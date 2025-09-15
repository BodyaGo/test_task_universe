import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import { MonitoringStats } from '../../lib/api'

interface SentimentChartProps {
  data: MonitoringStats | null
}

const SENTIMENT_COLORS = {
  positive: '#10B981', // green
  negative: '#EF4444', // red
  neutral: '#6B7280'   // gray
}

const THREAT_COLORS = {
  low: '#10B981',      // green
  medium: '#F59E0B',   // yellow
  high: '#F97316',     // orange
  critical: '#EF4444'  // red
}

export default function SentimentChart({ data }: SentimentChartProps) {
  if (!data) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Sentiment & Threat Analysis
          </h3>
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">No data available</div>
          </div>
        </div>
      </div>
    )
  }

  // Prepare sentiment data for pie chart
  const sentimentData = Object.entries(data.sentiment_distribution || {}).map(([sentiment, count]) => ({
    name: sentiment.charAt(0).toUpperCase() + sentiment.slice(1),
    value: count,
    color: SENTIMENT_COLORS[sentiment as keyof typeof SENTIMENT_COLORS] || '#6B7280'
  }))

  // Prepare threat data for bar chart
  const threatData = Object.entries(data.threat_distribution || {}).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    count: count,
    color: THREAT_COLORS[level as keyof typeof THREAT_COLORS] || '#6B7280'
  }))

  // Custom label function for pie chart
  const renderCustomizedLabel = (props: unknown) => {
    const { cx, cy, midAngle, innerRadius, outerRadius, percent } = props as {
      cx: number; cy: number; midAngle: number; innerRadius: number; outerRadius: number; percent: number;
    }
    if (percent < 0.05) return null // Don't show labels for slices smaller than 5%
    
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  const CustomTooltip = (props: unknown) => {
    const { active, payload, label } = props as {
      active?: boolean; payload?: Array<{ value: number }>; label?: string;
    }
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{`${label}: ${payload[0].value}`}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
          Аналіз тональності про Україну
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sentiment Distribution */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-4">Sentiment Distribution</h4>
            {sentimentData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={renderCustomizedLabel}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                
                {/* Legend */}
                <div className="flex justify-center mt-4 space-x-4">
                  {sentimentData.map((entry, index) => (
                    <div key={index} className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2" 
                        style={{ backgroundColor: entry.color }}
                      />
                      <span className="text-sm text-gray-600">
                        {entry.name} ({entry.value})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No sentiment data available
              </div>
            )}
          </div>

          {/* Threat Level Distribution */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-4">Threat Level Distribution</h4>
            {threatData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={threatData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fontSize: 12 }}
                      interval={0}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {threatData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No threat data available
              </div>
            )}
          </div>
        </div>

        {/* Summary Stats */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {data.total_mentions || 0}
              </div>
              <div className="text-sm text-gray-500">Total Mentions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {data.sentiment_distribution?.positive || 0}
              </div>
              <div className="text-sm text-gray-500">Positive</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {data.sentiment_distribution?.negative || 0}
              </div>
              <div className="text-sm text-gray-500">Negative</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {(data.threat_distribution?.high || 0) + (data.threat_distribution?.critical || 0)}
              </div>
              <div className="text-sm text-gray-500">High Threats</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}