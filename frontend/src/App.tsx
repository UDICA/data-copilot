import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Layout/Sidebar';
import { ChatWindow } from './components/Chat/ChatWindow';
import { InputBar } from './components/Chat/InputBar';
import { useChat } from './hooks/useChat';
import { useDataSources } from './hooks/useDataSources';

/**
 * Root application component.
 *
 * Layout: Header at top, Sidebar on left (w-64), main content area
 * with the chat window and input bar filling the remaining space.
 */
function App() {
  const { messages, isLoading, sendMessage } = useChat();
  const { sources, loading: sourcesLoading, refresh: refreshSources } = useDataSources();

  return (
    <div className="flex flex-col h-screen bg-white">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          sources={sources}
          loading={sourcesLoading}
          onRefresh={refreshSources}
        />
        <main className="flex-1 flex flex-col min-w-0">
          <ChatWindow messages={messages} isLoading={isLoading} />
          <InputBar onSend={sendMessage} disabled={isLoading} />
        </main>
      </div>
    </div>
  );
}

export default App;
