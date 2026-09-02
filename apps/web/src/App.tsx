import React, { useState, useRef, useEffect } from 'react';
import { AssistantClient } from './api/client';
import type { QueryRequest, FactualResponse, TerminalState } from './api/client';
import { MessageCard } from './components/Message';

const apiClient = new AssistantClient();

const TOPICS = [
  "Expense Ratio",
  "Exit Load",
  "Minimum SIP",
  "Minimum Lumpsum",
  "Benchmark",
  "Riskometer",
  "Fund Manager",
  "Inception Date",
  "Lock-in Period",
  "Investment Objective",
  "Plans & Options",
  "1-Year Performance",
  "Factsheet",
  "Account Statement",
  "Capital Gains",
  "KYC Procedure"
];

const FUNDS = [
  "All Funds",
  "HDFC Mid Cap Fund - Direct Growth",
  "HDFC Flexi Cap Fund - Direct Growth",
  "HDFC Small Cap Fund - Direct Growth",
  "HDFC Large and Mid Cap Fund - Direct Growth",
  "HDFC Large Cap Fund - Direct Growth",
  "HDFC Multi Cap Fund - Direct Growth",
  "HDFC Focused Fund - Direct Growth",
  "HDFC Value Fund - Direct Growth",
  "HDFC ELSS Tax Saver Fund - Direct Growth",
  "HDFC MNC Fund - Direct Growth",
  "HDFC Business Cycle Fund - Direct Growth",
  "HDFC Defence Fund - Direct Growth",
  "HDFC Consumption Fund - Direct Growth",
  "HDFC Transportation and Logistics Fund - Direct Growth",
  "HDFC Technology Fund - Direct Growth",
  "HDFC Pharma and Healthcare Fund - Direct Growth",
  "HDFC Manufacturing Fund - Direct Growth",
  "HDFC Infrastructure Fund - Direct Growth",
  "HDFC Innovation Fund - Direct Growth",
  "HDFC Children's Fund - Direct Growth",
  "HDFC NIFTY 50 Index Fund - Direct Growth",
  "HDFC NIFTY Next 50 Index Fund - Direct Growth",
  "HDFC NIFTY 100 Index Fund - Direct Growth",
  "HDFC NIFTY 100 Equal Weight Index Fund - Direct Growth",
  "HDFC NIFTY50 Equal Weight Index Fund - Direct Growth",
  "HDFC NIFTY Midcap 150 Index Fund - Direct Growth",
  "HDFC Nifty Smallcap 250 Index Fund - Direct Growth",
  "HDFC Nifty LargeMidcap 250 Index Fund - Direct Growth",
  "HDFC NIFTY200 Momentum 30 Index Fund - Direct Growth",
  "HDFC NIFTY100 Low Volatility 30 Index Fund - Direct Growth",
  "HDFC Nifty100 Quality 30 Index Fund - Direct Growth",
  "HDFC Nifty Top 20 Equal Weight Index Fund - Direct Growth",
  "HDFC Balanced Advantage Fund - Direct Growth",
  "HDFC Multi Asset Allocation Fund - Direct Growth",
  "HDFC Gold ETF Fund of Fund - Direct Growth"
];

function App() {
  const [query, setQuery] = useState('');
  const [selectedFund, setSelectedFund] = useState('All Funds');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'system', content: string, response?: FactualResponse }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const submitQuery = async (text: string) => {
    if (!text.trim() || isLoading) return;
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setIsLoading(true);

    try {
      const idempotencyKey = `idem_${Date.now()}`;
      const req: QueryRequest = {
        query: text,
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
          error: { reason: error.message || 'Service temporarily unavailable.' },
          original_query: text
        } as any
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    let finalUserQuery = query.trim();
    if (!finalUserQuery) return;

    // Automatically append the selected fund if not present in the query
    const fundKeyword = selectedFund.split(' ')[1] || 'hdfc';
    if (selectedFund !== 'All Funds' && !finalUserQuery.toLowerCase().includes(fundKeyword.toLowerCase())) {
        finalUserQuery = `${finalUserQuery} for ${selectedFund}`;
    }
    submitQuery(finalUserQuery);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTopicClick = (topic: string) => {
    const q = selectedFund !== 'All Funds'
        ? `What is the ${topic.toLowerCase()} for ${selectedFund}?`
        : `Tell me about ${topic.toLowerCase()}`;
    submitQuery(q);
    if (window.innerWidth < 1024) {
      setIsRightSidebarOpen(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    setTimeout(() => {
        const form = document.getElementById('chat-form') as HTMLFormElement;
        if (form) form.requestSubmit();
    }, 0);
  };

  return (
    <>
      <header className="bg-surface/80 dark:bg-surface-dim/80 backdrop-blur-xl border-b border-outline-variant/30 shadow-sm fixed top-0 w-full z-50 flex flex-col pt-2">
        <div className="w-full mx-auto px-margin flex items-center justify-between h-16 px-4 md:px-0 lg:pr-[300px]">
          <div className="flex items-center gap-sm md:ml-4">
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
              Facts-only. No advice.
            </div>
            <button
              onClick={() => setMessages([])}
              className="text-primary font-bold text-label-md font-label-md hover:bg-primary-container/20 transition-colors px-md py-sm rounded-full active:scale-95 duration-150"
            >
              Reset
            </button>
            <button
              onClick={() => setIsRightSidebarOpen(true)}
              className="lg:hidden p-2 rounded-full hover:bg-surface-variant/50 transition-colors text-on-surface-variant flex items-center justify-center"
              aria-label="Open topics sidebar"
            >
              <span className="material-symbols-outlined text-[24px]">info</span>
            </button>
          </div>
        </div>
        <div className="md:hidden bg-surface-container text-on-surface-variant px-sm py-xs flex justify-center items-center text-label-md font-label-md border-t border-outline-variant/30">
          <span className="material-symbols-outlined text-[14px] mr-1 text-tertiary-container" style={{fontVariationSettings: "'FILL' 1"}}>security</span>
          Facts-only. No investment advice.
        </div>
      </header>

      {/* Overlays */}
      {(isSidebarOpen || isRightSidebarOpen) && (
        <div
          className="fixed inset-0 bg-on-background/20 backdrop-blur-sm z-[60] lg:hidden transition-opacity"
          onClick={() => { setIsSidebarOpen(false); setIsRightSidebarOpen(false); }}
        />
      )}

      {/* Left Sidebar Panel (History) */}
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

      {/* Right Sidebar Panel (Context & Topics) */}
      <div
        className={`fixed top-0 lg:top-[72px] right-0 h-full lg:h-[calc(100vh-72px)] w-[300px] max-w-[80vw] bg-surface border-l border-outline-variant/30 shadow-xl lg:shadow-none z-[70] lg:z-[45] transform transition-transform duration-300 ease-in-out flex flex-col ${
          isRightSidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-4 border-b border-outline-variant/30 flex justify-between items-center lg:hidden bg-surface">
          <h3 className="font-headline-md font-bold text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary" style={{fontVariationSettings: "'FILL' 1"}}>info</span>
            Ask About
          </h3>
          <button onClick={() => setIsRightSidebarOpen(false)} className="p-2 rounded-full hover:bg-surface-variant/50">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="p-4 flex flex-col gap-6 overflow-y-auto pb-24 lg:pb-4">
          <div className="bg-surface-container-low p-4 rounded-xl border border-outline-variant/30">
            <label className="text-label-md font-bold text-on-surface-variant mb-2 block uppercase tracking-wider flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px]">account_balance</span>
                Fund Context
            </label>
            <select
              value={selectedFund}
              onChange={(e) => setSelectedFund(e.target.value)}
              className="w-full bg-surface border border-outline-variant/50 rounded-lg p-2 text-body-sm text-on-surface focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
            >
              {FUNDS.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
            <p className="text-[11px] text-outline mt-2 leading-tight">Your questions will automatically apply to this fund.</p>
          </div>

          <div>
            <label className="text-label-md font-bold text-on-surface-variant mb-3 block uppercase tracking-wider flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px]">explore</span>
                Suggested Topics
            </label>
            <div className="flex flex-col gap-2">
              {TOPICS.map(topic => (
                <button
                  key={topic}
                  onClick={() => handleTopicClick(topic)}
                  className="text-left px-3 py-2.5 rounded-lg bg-surface-container hover:bg-primary-container/20 hover:text-primary-fixed-variant transition-colors text-body-sm border border-transparent hover:border-primary/30 active:scale-95 shadow-sm"
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <main className="flex flex-col w-full max-w-[800px] mx-auto mt-[100px] mb-[130px] md:mb-[100px] px-4 md:px-0 lg:pr-[300px] lg:max-w-[1100px] scroll-smooth" id="chat-container">

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

      <div className="fixed bottom-0 w-full lg:w-[calc(100%-300px)] z-40 bg-surface/90 dark:bg-inverse-surface/90 backdrop-blur-xl border-t border-outline-variant/30 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] pb-safe-bottom">
        <div className="max-w-[800px] mx-auto px-4 py-3 md:py-4 lg:ml-[max(0px,calc(50vw-400px-150px))]">
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
