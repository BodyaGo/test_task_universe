import { ExclamationTriangleIcon, ClockIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { formatDistanceToNow } from 'date-fns'
import { BrandMention } from '../../lib/api'

interface ThreatsListProps {
  threats: BrandMention[]
}

const threatLevelColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800'
}

const threatLevelIcons = {
  low: '🟢',
  medium: '🟡',
  high: '🟠',
  critical: '🔴'
}

export default function ThreatsList({ threats }: ThreatsListProps) {
  if (!threats || threats.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            High Priority Threats
          </h3>
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No threats detected</h3>
            <p className="mt-1 text-sm text-gray-500">
              All mentions are currently at low threat levels.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
        Негативна інформація про Apple
      </h3>
        <div className="space-y-4">
          {threats.slice(0, 10).map((threat) => {
            const threatLevel = threat.threat_analysis?.threat_level || 'low'
            const timeAgo = threat.processed_at 
              ? formatDistanceToNow(new Date(threat.processed_at), { addSuffix: true })
              : 'Unknown time'

            return (
              <div
                key={threat.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{threatLevelIcons[threatLevel as keyof typeof threatLevelIcons]}</span>
                      <span className={clsx(
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        threatLevelColors[threatLevel as keyof typeof threatLevelColors]
                      )}>
                        {threatLevel.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        Score: {(threat.threat_analysis?.threat_score || 0).toFixed(2)}
                      </span>
                    </div>
                    
                    <h4 className="text-sm font-medium text-gray-900 truncate mb-1">
                      {threat.reddit_post?.title || 'No title'}
                    </h4>
                    
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {threat.reddit_post?.content || 'No content'}
                    </p>
                    
                    <div className="flex items-center text-xs text-gray-500 space-x-4">
                      <span>r/{threat.reddit_post?.subreddit || 'unknown'}</span>
                      <span>by {threat.reddit_post?.author || 'unknown'}</span>
                      <div className="flex items-center">
                        <ClockIcon className="h-3 w-3 mr-1" />
                        {timeAgo}
                      </div>
                    </div>
                    
                    {threat.threat_analysis?.keywords_matched && threat.threat_analysis.keywords_matched.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {threat.threat_analysis.keywords_matched.slice(0, 3).map((keyword, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {keyword}
                            </span>
                          ))}
                          {threat.threat_analysis.keywords_matched.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{threat.threat_analysis.keywords_matched.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {threat.threat_analysis?.threat_categories && threat.threat_analysis.threat_categories.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {threat.threat_analysis.threat_categories.slice(0, 2).map((category, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800"
                            >
                              {category}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4 flex-shrink-0">
                    <div className="flex flex-col items-end space-y-1">
                      <span className="text-xs text-gray-500">
                        {threat.reddit_post?.score || 0} points
                      </span>
                      <span className="text-xs text-gray-500">
                        {threat.reddit_post?.num_comments || 0} comments
                      </span>
                    </div>
                  </div>
                </div>
                
                {threat.response_recommendation && (
                  <div className="mt-3 p-2 bg-blue-50 rounded border-l-4 border-blue-400">
                    <p className="text-xs text-blue-800 font-medium">
                      Recommended Action: {threat.response_recommendation.action_type}
                    </p>
                    {threat.response_recommendation.escalation_needed && (
                      <p className="text-xs text-red-600 mt-1">
                        ⚠️ Escalation needed
                      </p>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
        
        {threats.length > 10 && (
          <div className="mt-4 text-center">
            <button className="text-sm text-blue-600 hover:text-blue-500 font-medium">
              View all {threats.length} threats →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}