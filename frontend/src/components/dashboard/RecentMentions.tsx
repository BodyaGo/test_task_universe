import { ChatBubbleLeftRightIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { formatDistanceToNow } from 'date-fns'
import { BrandMention } from '../../lib/api'

interface RecentMentionsProps {
  mentions: BrandMention[]
}

const sentimentColors = {
  positive: 'bg-green-100 text-green-800',
  negative: 'bg-red-100 text-red-800',
  neutral: 'bg-gray-100 text-gray-800'
}

const sentimentEmojis = {
  positive: '😊',
  negative: '😞',
  neutral: '😐'
}

export default function RecentMentions({ mentions }: RecentMentionsProps) {
  if (!mentions || mentions.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Mentions
          </h3>
          <div className="text-center py-8">
            <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No mentions found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No brand mentions have been detected recently.
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
        Recent Apple Mentions
      </h3>
        
        <div className="space-y-4">
          {mentions.slice(0, 8).map((mention) => {
            const sentiment = mention.sentiment_analysis?.sentiment || 'neutral'
            const timeAgo = mention.processed_at 
              ? formatDistanceToNow(new Date(mention.processed_at), { addSuffix: true })
              : 'Unknown time'

            return (
              <div
                key={mention.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{sentimentEmojis[sentiment as keyof typeof sentimentEmojis]}</span>
                      <span className={clsx(
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        sentimentColors[sentiment as keyof typeof sentimentColors]
                      )}>
                        {sentiment.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        Confidence: {((mention.sentiment_analysis?.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      {mention.reddit_post?.title || 'No title'}
                    </h4>
                    
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {mention.reddit_post?.content || 'No content'}
                    </p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center text-xs text-gray-500 space-x-4">
                        <span className="font-medium">r/{mention.reddit_post?.subreddit || 'unknown'}</span>
                        <span>by {mention.reddit_post?.author || 'unknown'}</span>
                        <span>{timeAgo}</span>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>{mention.reddit_post?.score || 0} points</span>
                        <span>{mention.reddit_post?.num_comments || 0} comments</span>
                        {mention.reddit_post?.permalink && (
                          <a
                            href={`https://reddit.com${mention.reddit_post.permalink}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-blue-600 hover:text-blue-500"
                          >
                            <ArrowTopRightOnSquareIcon className="h-3 w-3 ml-1" />
                          </a>
                        )}
                      </div>
                    </div>
                    
                    {/* Threat Score */}
                    {mention.threat_analysis && (
                      <div className="mt-2 flex items-center space-x-2">
                        <span className="text-xs text-gray-500">Threat Score:</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-24">
                          <div 
                            className={clsx(
                              'h-2 rounded-full',
                              mention.threat_analysis.threat_score >= 0.7 ? 'bg-red-500' :
                              mention.threat_analysis.threat_score >= 0.4 ? 'bg-yellow-500' :
                              'bg-green-500'
                            )}
                            style={{ width: `${(mention.threat_analysis.threat_score || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">
                          {((mention.threat_analysis.threat_score || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    
                    {/* Keywords */}
                    {mention.threat_analysis?.keywords_matched && mention.threat_analysis.keywords_matched.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {mention.threat_analysis.keywords_matched.slice(0, 3).map((keyword, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {keyword}
                            </span>
                          ))}
                          {mention.threat_analysis.keywords_matched.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{mention.threat_analysis.keywords_matched.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Response Recommendation */}
                {mention.response_recommendation && (
                  <div className="mt-3 p-2 bg-blue-50 rounded border-l-4 border-blue-400">
                    <p className="text-xs text-blue-800 font-medium">
                      💡 {mention.response_recommendation.action_type}
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Priority: {mention.response_recommendation.priority}/5
                    </p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
        
        {mentions.length > 8 && (
          <div className="mt-4 text-center">
            <button className="text-sm text-blue-600 hover:text-blue-500 font-medium">
              View all {mentions.length} mentions →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}