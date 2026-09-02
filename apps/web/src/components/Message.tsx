import React, { useState, useEffect } from 'react';
import type { FactualResponse } from '../api/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export const MessageCard: React.FC<{ 
  response: FactualResponse, 
  onChipClick?: (chip: string) => void,
  onFeedback?: (isPositive: boolean) => void 
}> = ({ response, onChipClick, onFeedback }) => {
  const { status, answer, citation, error, follow_up_chips } = response;

  const [displayedAnswer, setDisplayedAnswer] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<boolean | null>(null);

  useEffect(() => {
    if (status === 'FACTUAL_ANSWER' && answer) {
      setIsTyping(true);
      let currentIndex = 0;
      const interval = setInterval(() => {
        setDisplayedAnswer(answer.slice(0, currentIndex + 1));
        currentIndex++;
        if (currentIndex === answer.length) {
          clearInterval(interval);
          setIsTyping(false);
        }
      }, 15); // Adjust typing speed here
      return () => clearInterval(interval);
    }
  }, [answer, status]);

  if (status === 'FACTUAL_ANSWER') {
    return (
      <div className="bg-surface border border-outline-variant/30 rounded-2xl rounded-tl-sm px-md py-sm shadow-sm flex flex-col gap-2">
        <div className="text-body-md font-body-md text-on-surface whitespace-pre-wrap markdown-body">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({node, ...props}) => <div className="overflow-x-auto my-3"><table className="min-w-full divide-y divide-outline-variant/30 border border-outline-variant/30 rounded-lg shadow-sm" {...props} /></div>,
              thead: ({node, ...props}) => <thead className="bg-surface-container-low" {...props} />,
              th: ({node, ...props}) => <th className="px-3 py-2 text-left text-xs font-bold text-on-surface uppercase tracking-wider border-b border-outline-variant/30" {...props} />,
              td: ({node, ...props}) => <td className="px-3 py-2 whitespace-nowrap text-sm text-on-surface-variant border-t border-outline-variant/20" {...props} />,
            }}
          >
            {displayedAnswer}
          </ReactMarkdown>
          {isTyping && <span className="inline-block w-1.5 h-4 ml-1 bg-primary align-middle animate-pulse rounded-full"></span>}
        </div>

        {!isTyping && citation?.url && (
          <div className="mt-xs pt-sm border-t border-outline-variant/20 flex flex-wrap justify-between items-center gap-x-4 gap-y-1 text-label-md font-label-md text-outline">
            <a href={citation.url} target="_blank" rel="noreferrer" className="flex items-center gap-xs hover:text-primary transition-colors">
              <span className="material-symbols-outlined text-[12px]">description</span>
              Source ({(() => {
                try {
                  return new URL(citation.url).hostname.replace('www.', '');
                } catch {
                  return 'Official Source';
                }
              })()})
            </a>
            
            <div className="flex items-center gap-1">
              <button 
                onClick={() => { setFeedbackSent(true); onFeedback?.(true); }}
                disabled={feedbackSent !== null}
                className={`p-1 rounded-full flex items-center justify-center transition-colors ${feedbackSent === true ? 'text-primary bg-primary-container/50' : 'hover:bg-surface-variant text-outline hover:text-primary disabled:opacity-50'}`}
                title="Helpful"
              >
                <span className="material-symbols-outlined text-[16px]" style={{fontVariationSettings: "'FILL' " + (feedbackSent === true ? "1" : "0")}}>thumb_up</span>
              </button>
              <button 
                onClick={() => { setFeedbackSent(false); onFeedback?.(false); }}
                disabled={feedbackSent !== null}
                className={`p-1 rounded-full flex items-center justify-center transition-colors ${feedbackSent === false ? 'text-error bg-error-container/50' : 'hover:bg-surface-variant text-outline hover:text-error disabled:opacity-50'}`}
                title="Not Helpful"
              >
                <span className="material-symbols-outlined text-[16px]" style={{fontVariationSettings: "'FILL' " + (feedbackSent === false ? "1" : "0")}}>thumb_down</span>
              </button>
            </div>
          </div>
        )}

        {!isTyping && follow_up_chips && follow_up_chips.length > 0 && (
          <div className="mt-xs flex flex-wrap gap-2">
            {follow_up_chips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => onChipClick?.(chip)}
                className="text-xs bg-primary-container/40 hover:bg-primary-container text-on-primary-container border border-primary/20 hover:border-primary/40 px-3 py-1.5 rounded-full transition-all font-medium shadow-sm active:scale-95 flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-[14px]">search</span>
                {chip}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  const isRefusal = status === 'POLICY_REFUSAL';
  const iconName = isRefusal ? 'warning' : 'error';

  return (
    <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-2xl rounded-tl-sm px-md py-sm shadow-sm">
      <div className="flex items-start gap-sm">
        <span className="material-symbols-outlined text-amber-700 dark:text-amber-500 mt-1" style={{fontVariationSettings: "'FILL' 1"}}>
          {iconName}
        </span>
        <div>
          <p className="text-body-md font-body-md text-amber-900 dark:text-amber-200 font-bold">
            {isRefusal ? "Policy Refusal" :
              (status === 'SOURCE_CONFLICT' ? "Source Conflict" :
              (status === 'INSUFFICIENT_EVIDENCE' ? "Unsupported Query" :
              (status === 'AMBIGUOUS_SCHEME' ? "Ambiguous Scheme" :
              (status === 'TEMPORARILY_UNAVAILABLE' ? "Service Unavailable" : "System Error"))))}
          </p>
          <p className="text-body-sm font-body-sm text-amber-800 dark:text-amber-300/80 mt-1">
            {error?.reason || "I cannot provide an answer to this query based on the current factual constraints."}
          </p>
          {(response as any).original_query && (
            <button
              onClick={() => {
                const form = document.getElementById('chat-form') as HTMLFormElement;
                const input = form.querySelector('textarea') || form.querySelector('input[type="text"]');
                if (input) {
                  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
                  setter?.call(input, (response as any).original_query);
                  input.dispatchEvent(new Event('input', { bubbles: true }));
                  setTimeout(() => form.requestSubmit(), 0);
                }
              }}
              className="mt-2 text-xs font-bold px-3 py-1 rounded bg-amber-200 dark:bg-amber-800 hover:bg-amber-300 dark:hover:bg-amber-700 transition-colors"
            >
              Retry Request
            </button>
          )}

          {follow_up_chips && follow_up_chips.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {follow_up_chips.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => onChipClick?.(chip)}
                  className="text-xs bg-surface/50 hover:bg-surface text-amber-900 dark:text-amber-100 border border-amber-300/50 hover:border-amber-400 px-3 py-1.5 rounded-full transition-all font-medium shadow-sm active:scale-95 flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[14px]">search</span>
                  {chip}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
