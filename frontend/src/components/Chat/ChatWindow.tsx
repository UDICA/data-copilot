import { useEffect, useRef } from 'react';
import type { ChatMessage } from '../../types';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

/**
 * Scrollable container for chat messages with auto-scroll behavior.
 *
 * Shows a welcome prompt when no messages exist. Displays a typing
 * indicator when waiting for a response. Auto-scrolls to the bottom
 * whenever new content arrives.
 */
export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-gray-600 mx-auto mb-4"
            aria-hidden="true"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <h2 className="text-lg font-medium text-gray-200 mb-2">
            Start a conversation
          </h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            Ask questions about your data. You can query databases,
            explore files, search the web, and combine insights from
            multiple sources in a single conversation.
          </p>
          <div className="mt-6 space-y-2">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Try asking
            </p>
            {[
              'What were our top 5 products by revenue last quarter?',
              'Compare sales data with the regional targets CSV',
              'Summarize the company policy on returns',
            ].map((suggestion) => (
              <p
                key={suggestion}
                className="text-sm text-gray-400 bg-gray-800 rounded-lg px-3 py-2 border border-gray-700"
              >
                {suggestion}
              </p>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4" role="log" aria-label="Chat messages">
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Typing indicator shown when loading but no streaming message yet */}
        {isLoading && !messages.some(m => m.isStreaming) && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3">
              <div className="flex items-center gap-1.5" aria-label="Assistant is typing">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
