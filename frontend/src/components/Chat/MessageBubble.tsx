import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage, ToolSource } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
}

/** Badge color mapping for each source type. */
const SOURCE_COLORS: Record<ToolSource['type'], string> = {
  sql: 'bg-purple-900/50 text-purple-300',
  file: 'bg-emerald-900/50 text-emerald-300',
  web: 'bg-orange-900/50 text-orange-300',
  analysis: 'bg-amber-900/50 text-amber-300',
};

/** Human-readable labels for source types. */
const SOURCE_LABELS: Record<ToolSource['type'], string> = {
  sql: 'SQL',
  file: 'File',
  web: 'Web',
  analysis: 'Analysis',
};

/**
 * Renders a single chat message bubble.
 *
 * User messages appear right-aligned in orange. Assistant messages
 * appear left-aligned in dark gray with markdown rendering and source
 * attribution badges.
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[75%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-orange-600 text-white'
            : 'bg-gray-800 text-gray-100 border border-gray-700'
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm prose-dark max-w-none overflow-x-auto prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-pre:my-2 prose-blockquote:my-2">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Streaming indicator */}
        {message.isStreaming && (
          <span className="inline-block mt-1 text-xs text-gray-500 animate-pulse">
            Generating...
          </span>
        )}

        {/* Source attribution badges */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-gray-700">
            {message.sources.map((source) => (
              <span
                key={source.tool_name}
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${SOURCE_COLORS[source.type]}`}
                title={source.tool_name}
              >
                {SOURCE_LABELS[source.type]}: {source.tool_name}
              </span>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className={`text-xs mt-1 ${isUser ? 'text-orange-200' : 'text-gray-500'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
