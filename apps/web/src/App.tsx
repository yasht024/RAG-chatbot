import React, { useState, useRef, useEffect } from 'react';
import { AssistantClient } from './api/client';
import type { QueryRequest, FactualResponse, TerminalState } from './api/client';
import { MessageCard } from './components/Message';

const apiClient = new AssistantClient('http://localhost:8000');

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'system', content: string, response?: FactualResponse }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userQuery = query.trim();
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setIsLoading(true);

    try {
      const idempotencyKey = `idem_${Date.now()}`;
      const req: QueryRequest = {
        query: userQuery,
        conversation_id: 'conv_frontend_1',
        history: messages.map(m => ({ role: m.role, content: m.content }))
      };
      
      const res = await apiClient.askQuestion(req, idempotencyKey);
      setMessages(prev => [...prev, { role: 'system', content: '', response: res }]);
    } catch (error: any) {
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: '', 
        response: {
          status: 'TEMPORARILY_UNAVAILABLE' as TerminalState,
          refusal_reason: error.message || 'Service temporarily unavailable.',
          original_query: userQuery
        }
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    // Use timeout to allow state to update before submitting
    setTimeout(() => {
        const form = document.getElementById('chat-form') as HTMLFormElement;
        if (form) form.requestSubmit();
    }, 0);
  };

  return (
    <>
      <header className="bg-surface/80 dark:bg-surface-dim/80 backdrop-blur-xl border-b border-outline-variant/30 shadow-sm fixed top-0 w-full z-50 flex flex-col pt-2">
        <div className="max-w-[1280px] w-full mx-auto px-margin flex items-center justify-between h-16 px-4 md:px-0">
          <div className="flex items-center gap-sm">
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 -ml-2 rounded-full hover:bg-surface-variant/50 transition-colors text-on-surface-variant flex items-center justify-center"
              aria-label="Open history sidebar"
            >
              <span className="material-symbols-outlined text-[24px]">menu</span>
            </button>
            <span className="material-symbols-outlined text-primary dark:text-primary-fixed-dim text-headline-md ml-1" style={{fontVariationSettings: "'FILL' 1"}}>verified_user</span>
            <h1 className="text-headline-md font-headline-md font-bold text-primary dark:text-primary-fixed-dim truncate">
              HDFC Mutual Fund Assistant
            </h1>
          </div>
          <div className="flex items-center gap-md">
            <div className="hidden md:flex items-center bg-surface-container text-on-surface-variant px-sm py-xs rounded-full border border-outline-variant/30 text-label-md font-label-md shadow-sm">
              <span className="material-symbols-outlined text-[16px] mr-1 text-tertiary-container" style={{fontVariationSettings: "'FILL' 1"}}>security</span>
              Facts-only. No investment advice.
            </div>
            <button 
              onClick={() => setMessages([])} 
              className="text-primary font-bold text-label-md font-label-md hover:bg-primary-container/20 transition-colors px-md py-sm rounded-full active:scale-95 duration-150"
            >
              Reset
            </button>
          </div>
        </div>
        <div className="md:hidden bg-surface-container text-on-surface-variant px-sm py-xs flex justify-center items-center text-label-md font-label-md border-t border-outline-variant/30">
          <span className="material-symbols-outlined text-[14px] mr-1 text-tertiary-container" style={{fontVariationSettings: "'FILL' 1"}}>security</span>
          Facts-only. No investment advice.
        </div>
      </header>

      {/* Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-on-background/20 backdrop-blur-sm z-[60] transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar Panel */}
      <div 
        className={`fixed top-0 left-0 h-full w-[300px] max-w-[80vw] bg-surface border-r border-outline-variant/30 shadow-xl z-[70] transform transition-transform duration-300 ease-in-out flex flex-col ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-outline-variant/30">
          <h2 className="text-headline-md font-headline-md font-bold text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary" style={{fontVariationSettings: "'FILL' 1"}}>history</span>
            History
          </h2>
          <button 
            onClick={() => setIsSidebarOpen(false)}
            className="p-2 rounded-full hover:bg-surface-variant/50 transition-colors text-on-surface-variant"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
          {messages.filter(m => m.role === 'user').length === 0 ? (
            <div className="text-center text-on-surface-variant mt-8 text-body-md">
              No questions asked yet.
            </div>
          ) : (
            messages.filter(m => m.role === 'user').map((msg, idx) => (
              <button 
                key={idx} 
                onClick={() => {
                  const element = document.getElementById(`msg-${idx}`);
                  if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    setIsSidebarOpen(false);
                  }
                }}
                className="w-full text-left p-3 bg-surface-container-low rounded-xl border border-outline-variant/30 text-body-sm text-on-surface shadow-sm hover:bg-surface-variant hover:border-primary/50 transition-all active:scale-95 cursor-pointer"
              >
                {msg.content}
              </button>
            ))
          )}
        </div>
        <div className="p-4 border-t border-outline-variant/30">
            <button 
              onClick={() => { setMessages([]); setIsSidebarOpen(false); }} 
              className="w-full text-error font-bold text-label-md font-label-md hover:bg-error-container/20 transition-colors px-md py-sm rounded-full flex justify-center items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">delete</span>
              Clear Conversation
            </button>
        </div>
      </div>

      <main className="flex flex-col w-full max-w-[800px] mx-auto mt-[100px] mb-[130px] md:mb-[100px] px-4 md:px-0 scroll-smooth" id="chat-container">
        
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center py-xl animate-fade-in-up">
            <div className="w-16 h-16 rounded-full bg-primary-container flex items-center justify-center mb-md shadow-sm border border-outline-variant/30">
              <span className="material-symbols-outlined text-on-primary-container text-headline-lg" style={{fontVariationSettings: "'FILL' 1"}}>query_stats</span>
            </div>
            <h2 className="text-headline-md font-headline-md text-on-surface mb-sm text-center">Hello. I am the HDFC Mutual Fund Assistant.</h2>
            <p className="text-body-md font-body-md text-on-surface-variant text-center max-w-lg mb-lg">
                I provide factual information directly from official scheme documents. How can I assist you today?
            </p>
            <div className="flex flex-wrap justify-center gap-sm max-w-2xl w-full">
              <button onClick={() => handleExampleClick("What is the minimum SIP for HDFC Mid Cap?")} className="bg-surface border border-outline-variant/50 text-secondary font-body-sm text-body-sm px-4 py-2 rounded-full hover:border-primary hover:text-primary transition-all shadow-sm hover:shadow-md">
                  What is the minimum SIP for HDFC Mid Cap?
              </button>
              <button onClick={() => handleExampleClick("What is the lock-in period for ELSS?")} className="bg-surface border border-outline-variant/50 text-secondary font-body-sm text-body-sm px-4 py-2 rounded-full hover:border-primary hover:text-primary transition-all shadow-sm hover:shadow-md">
                  What is the lock-in period for ELSS?
              </button>
              <button onClick={() => handleExampleClick("HDFC Top 100 exit load")} className="bg-surface border border-outline-variant/50 text-secondary font-body-sm text-body-sm px-4 py-2 rounded-full hover:border-primary hover:text-primary transition-all shadow-sm hover:shadow-md">
                  HDFC Top 100 exit load
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            id={msg.role === 'user' ? `msg-${messages.filter((m, i) => i <= idx && m.role === 'user').length - 1}` : undefined}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} mb-lg animate-fade-in-up`}
          >
            <div className={`max-w-[85%] md:max-w-[${msg.role === 'user' ? '70%' : '75%'}]`}>
              {msg.role === 'user' ? (
                <div className="bg-primary text-on-primary rounded-2xl rounded-tr-sm px-md py-sm shadow-sm">
                  <p className="text-body-md font-body-md whitespace-pre-wrap">{msg.content}</p>
                </div>
              ) : (
                msg.response ? <MessageCard response={msg.response} /> : (
                  <div className="bg-surface border border-outline-variant/30 rounded-2xl rounded-tl-sm px-md py-sm shadow-sm">
                    <p className="text-body-md font-body-md text-on-surface mb-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                )
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-lg animate-fade-in-up">
            <div className="max-w-[85%] md:max-w-[75%]">
              <div className="bg-surface border border-outline-variant/30 rounded-2xl rounded-tl-sm px-md py-sm shadow-sm flex items-center h-[52px]">
                <div className="flex items-center gap-1 text-primary">
                  <svg height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <circle className="typing-dot" cx="4" cy="12" r="3"></circle>
                    <circle className="typing-dot" cx="12" cy="12" r="3"></circle>
                    <circle className="typing-dot" cx="20" cy="12" r="3"></circle>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
        <div className="h-4"></div>
      </main>

      <div className="fixed bottom-0 w-full z-40 bg-surface/90 dark:bg-inverse-surface/90 backdrop-blur-xl border-t border-outline-variant/30 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] pb-safe-bottom">
        <div className="max-w-[800px] mx-auto px-4 py-3 md:py-4">
          <form id="chat-form" onSubmit={handleSubmit} className="relative flex items-end gap-sm bg-surface-container-lowest border border-outline-variant/50 rounded-2xl shadow-sm focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all p-2">
            <textarea 
              className="w-full bg-transparent border-none focus:ring-0 focus:outline-none resize-none text-body-md font-body-md text-on-surface placeholder-on-surface-variant/50 py-2 pl-2 pr-12 min-h-[44px] max-h-[120px] overflow-y-auto"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a factual question..."
              rows={1}
              disabled={isLoading}
            />
            <button type="submit" disabled={!query.trim() || isLoading} className="absolute right-3 bottom-3 w-10 h-10 flex items-center justify-center bg-primary text-on-primary rounded-xl hover:bg-surface-tint transition-colors shadow-sm active:scale-95 disabled:opacity-50">
              <span className="material-symbols-outlined text-[20px]" style={{fontVariationSettings: "'FILL' 1"}}>send</span>
            </button>
          </form>
          <div className="text-center mt-2">
            <p className="text-[10px] font-label-md text-outline">Responses are generated based on official fund documents. Always verify independently.</p>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
