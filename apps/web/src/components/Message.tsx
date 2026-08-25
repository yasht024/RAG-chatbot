import React from 'react';
import type { FactualResponse } from '../api/client';

export const MessageCard: React.FC<{ response: FactualResponse }> = ({ response }) => {
  const { status, answer, citation, error } = response;

  if (status === 'FACTUAL_ANSWER') {
    return (
      <div className="bg-surface border border-outline-variant/30 rounded-2xl rounded-tl-sm px-md py-sm shadow-sm">
        <p className="text-body-md font-body-md text-on-surface mb-sm whitespace-pre-wrap">
          {answer}
        </p>

        {citation?.url && (
          <div className="mt-sm pt-sm border-t border-outline-variant/20 flex flex-wrap gap-x-4 gap-y-1 text-label-md font-label-md text-outline">
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
                const input = form.querySelector('textarea');
                if (input) {
                  const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
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
        </div>
      </div>
    </div>
  );
};
