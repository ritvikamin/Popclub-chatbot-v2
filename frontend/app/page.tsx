'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{ source: string; text: string; score: number }>;
}

function ChipIcon() {
  return (
    <svg viewBox="0 0 32 24" width="26" height="20" fill="none">
      <rect x="0.5" y="0.5" width="31" height="23" rx="4" stroke="#e4c463" strokeWidth="1" fill="#e4c463" fillOpacity="0.12" />
      <path
        d="M8 0.5V23.5M24 0.5V23.5M0.5 8H10M22 8H31.5M0.5 16H10M22 16H31.5M10 8V16M22 8V16"
        stroke="#e4c463"
        strokeWidth="0.75"
      />
    </svg>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Welcome to POPclub Copilot. Ask about the UPI platform, card benefits, rewards rules, or the team — I\u2019ll pull answers straight from the source docs.',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    const updatedMessages: Message[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, history: updatedMessages.slice(0, -1) }),
      });

      if (!response.ok) throw new Error('Network failure');
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, citations: data.citations },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Ledger entry failed to post. The core engine backend did not respond.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  let entryCount = 0;

  return (
    <div className="wrap">
      <aside className="sidebar">
        <div className="card">
          <div className="card-glow" />
          <div className="card-top">
            <ChipIcon />
            <span className="eyebrow">Member</span>
          </div>
          <p className="card-title">POPclub</p>
          <p className="card-sub">-------------</p>
          <div className="live-row">
            <span className="dot" />
            <span className="eyebrow live-text">Live</span>
          </div>
        </div>

        <div className="config">
          <h3 className="eyebrow config-heading">Issued Configuration</h3>
          <div className="config-row">
            <span className="config-key">Model</span>
            <span className="config-val">Gemini 2.5 Flash</span>
          </div>
          <div className="config-row">
            <span className="config-key">Index</span>
            <span className="config-val">ChromaDB · Persistent</span>
          </div>
          <div className="config-row">
            <span className="config-key">Context</span>
            <span className="config-val">Top-3 chunks</span>
          </div>
        </div>

        <div className="sidebar-footer">Version 002 · ENTERPRISE BUILD</div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <h1 className="brand">POPclub Chatbot</h1>
            <p className="tagline">grounded on your UPI &amp; rewards docs</p>
          </div>
          <div className="status">
            <span className="dot" />
            Online
          </div>
        </header>

        <section className="log">
          <div className="log-inner">
            {messages.map((msg, idx) => {
              if (msg.role === 'assistant') entryCount += 1;
              const isUser = msg.role === 'user';

              return (
                <div key={idx} className={isUser ? 'row row-user' : 'row row-assistant'}>
                  {isUser ? (
                    <div className="bubble-user">{msg.content}</div>
                  ) : (
                    <div className="entry">
                      <div className="entry-marker">{entryCount}</div>
                      <div className="entry-body">
                        <p className="entry-text">{msg.content}</p>
                        {msg.citations && msg.citations.length > 0 && (
                          <div className="stubs">
                            <span className="eyebrow">Sourced from</span>
                            <div className="stub-row">
                              {msg.citations.map((cit, cIdx) => (
                                <div key={cIdx} title={cit.text} className="stub">
                                  <span className="stub-source">{cit.source}</span>
                                  <span className="stub-score">{(cit.score * 100).toFixed(0)}%</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {isLoading && (
              <div className="row row-assistant">
                <div className="loading">
                  <span className="bounce" style={{ animationDelay: '-0.3s' }} />
                  <span className="bounce" style={{ animationDelay: '-0.15s' }} />
                  <span className="bounce" />
                  posting entry to the ledger
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </section>

        <footer className="composer">
          <form onSubmit={sendMessage} className="composer-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about UPI, cards, rewards, or the team…"
              disabled={isLoading}
              className="composer-input"
            />
            <button
              type="submit"
              aria-label="Send message"
              disabled={isLoading || !input.trim()}
              className="composer-send"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#12172b" strokeWidth="2.5">
                <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </form>
          <p className="fine-print">every answer is grounded — nothing here is guessed</p>
        </footer>
      </main>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        * {
          box-sizing: border-box;
        }
        html,
        body {
          margin: 0;
          padding: 0;
          background: #12172b;
          color: #edeae1;
          font-family: 'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif;
        }
      `}</style>

      <style jsx>{`
        .wrap {
          display: flex;
          height: 100vh;
          background: #12172b;
          color: #edeae1;
          overflow: hidden;
        }

        .sidebar {
          width: 288px;
          flex-shrink: 0;
          padding: 24px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        .card {
          position: relative;
          overflow: hidden;
          border-radius: 16px;
          padding: 20px;
          background: linear-gradient(135deg, #232c52, #1b2242);
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        .card-glow {
          position: absolute;
          top: -24px;
          right: -24px;
          height: 96px;
          width: 96px;
          border-radius: 999px;
          background: rgba(201, 162, 39, 0.1);
        }
        .card-top {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 22px;
        }
        .card-title {
          font-family: 'Fraunces', ui-serif, serif;
          font-size: 21px;
          letter-spacing: -0.01em;
          color: #edeae1;
          margin: 0 0 4px;
          line-height: 1;
        }
        .card-sub {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: #8890a6;
          letter-spacing: 0.05em;
          margin: 0 0 18px;
        }
        .live-row {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .live-text {
          color: #4fd1c5;
        }
        .dot {
          height: 6px;
          width: 6px;
          border-radius: 999px;
          background: #4fd1c5;
          flex-shrink: 0;
        }

        .eyebrow {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #8890a6;
        }

        .config {
          margin-top: 24px;
        }
        .config-heading {
          padding: 0 4px;
          margin-bottom: 12px;
          display: block;
        }
        .config-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          padding-bottom: 10px;
          margin-bottom: 10px;
        }
        .config-key {
          font-size: 11px;
          color: #8890a6;
        }
        .config-val {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          color: #edeae1;
          text-align: right;
        }

        .sidebar-footer {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: rgba(136, 144, 166, 0.7);
          letter-spacing: 0.05em;
          border-top: 1px solid rgba(255, 255, 255, 0.05);
          padding-top: 16px;
        }

        .main {
          flex: 1;
          display: flex;
          flex-direction: column;
          height: 100%;
          min-width: 0;
        }

        .header {
          height: 64px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 32px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          background: rgba(18, 23, 43, 0.8);
        }
        .brand {
          font-family: 'Fraunces', ui-serif, serif;
          font-size: 19px;
          margin: 0;
          color: #edeae1;
          letter-spacing: -0.01em;
        }
        .tagline {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          color: #8890a6;
          margin: 2px 0 0;
        }
        .status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #4fd1c5;
        }

        .log {
          flex: 1;
          overflow-y: auto;
          padding: 40px 48px;
        }
        .log-inner {
          max-width: 720px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .row {
          display: flex;
          width: 100%;
        }
        .row-user {
          justify-content: flex-end;
        }
        .row-assistant {
          justify-content: flex-start;
        }

        .bubble-user {
          max-width: 80%;
          border-radius: 12px;
          border-top-right-radius: 3px;
          border: 1px solid rgba(201, 162, 39, 0.4);
          background: #232c52;
          padding: 12px 16px;
          font-size: 14px;
          line-height: 1.6;
          color: #edeae1;
        }

        .entry {
          max-width: 80%;
          display: flex;
          align-items: flex-start;
          gap: 10px;
        }
        .entry-marker {
          margin-top: 14px;
          flex-shrink: 0;
          height: 22px;
          width: 22px;
          border-radius: 999px;
          border: 1px solid rgba(201, 162, 39, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: #e4c463;
        }
        .entry-body {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
          gap: 10px;
          background: #1b2242;
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-top-left-radius: 3px;
          border-radius: 12px;
          padding: 12px 16px;
        }
        .entry-text {
          margin: 0;
          font-size: 14px;
          line-height: 1.6;
          color: #edeae1;
          white-space: pre-line;
          word-break: break-word;
        }

        .stubs {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .stub-row {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .stub {
          display: flex;
          align-items: center;
          gap: 8px;
          border-radius: 0 6px 6px 0;
          background: #12172b;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-left: none;
          padding: 6px 10px 6px 12px;
          font-size: 11px;
          cursor: help;
          background-image: radial-gradient(circle, #1b2242 1.5px, transparent 1.6px);
          background-size: 6px 8px;
          background-repeat: repeat-y;
          background-position: left center;
        }
        .stub-source {
          font-family: 'IBM Plex Mono', monospace;
          color: #edeae1;
          max-width: 130px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .stub-score {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: #4fd1c5;
        }

        .loading {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 4px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          color: #8890a6;
        }
        .bounce {
          height: 6px;
          width: 6px;
          border-radius: 999px;
          background: #c9a227;
          display: inline-block;
          animation: bounce 1s infinite;
        }
        @keyframes bounce {
          0%,
          100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-4px);
          }
        }

        .composer {
          flex-shrink: 0;
          padding: 12px 40px 24px;
        }
        .composer-form {
          max-width: 720px;
          margin: 0 auto;
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .composer-input {
          flex: 1;
          background: #1b2242;
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #edeae1;
          border-radius: 12px;
          padding: 14px 16px;
          font-size: 14px;
          font-family: inherit;
          outline: none;
          transition: border-color 0.15s ease;
        }
        .composer-input::placeholder {
          color: #8890a6;
        }
        .composer-input:focus {
          border-color: rgba(201, 162, 39, 0.5);
          box-shadow: 0 0 0 2px rgba(201, 162, 39, 0.3);
        }
        .composer-send {
          flex-shrink: 0;
          height: 44px;
          width: 44px;
          border-radius: 999px;
          border: none;
          background: #c9a227;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: transform 0.1s ease, opacity 0.15s ease;
        }
        .composer-send:active {
          transform: scale(0.9);
        }
        .composer-send:disabled {
          opacity: 0.3;
          cursor: default;
        }
        .composer-send:focus-visible {
          outline: 2px solid #e4c463;
          outline-offset: 2px;
        }

        .fine-print {
          text-align: center;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: rgba(136, 144, 166, 0.7);
          letter-spacing: 0.03em;
          margin: 12px 0 0;
        }

        @media (max-width: 768px) {
          .sidebar {
            display: none;
          }
          .log {
            padding: 24px 16px;
          }
          .composer {
            padding: 12px 16px 20px;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .bounce {
            animation: none;
          }
        }
      `}</style>
    </div>
  );
}