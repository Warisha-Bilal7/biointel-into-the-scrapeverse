'use client';

import { useState, useEffect } from 'react';

const sources = [
  {
    name: 'Clinical Data',
    status: 'Healthy',
    confidence: 98,
  },
  {
    name: 'Drug Database',
    status: 'Healthy',
    confidence: 96,
  },
  {
    name: 'Research Source',
    status: 'Drift Detected',
    confidence: 42,
  },
];

const events = [
  {
    time: '10:00',
    icon: 'scrape',
    text: 'Scrape completed',
  },
  {
    time: '10:01',
    icon: 'scrape',
    text: 'Payload validated',
  },
  {
    time: '10:15',
    icon: 'variation',
    text: 'Structural variation noticed',
  },
  {
    time: '10:16',
    icon: 'drift',
    text: 'AI drift detected',
  },
  {
    time: '10:17',
    icon: 'heal',
    text: 'Self-healing review triggered',
  },
];

export default function Home() {
  const [selectedSource, setSelectedSource] = useState('Research Source');

  useEffect(() => {
    const styleSheet = document.createElement('style');
    styleSheet.innerText = `@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&family=Fira+Sans:wght@400;500;600&display=swap');
    `;
    document.head.appendChild(styleSheet);
    return () => {
      document.head.removeChild(styleSheet);
    };
  }, []);

  return (
    <>
      <section className="mb-8 rounded-2xl p-8 md:p-12 bg-card border border-border/30">
        <p className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          AI-POWERED DATA INTEGRITY
        </p>

        <h2 className="text-4xl md:text-5xl font-semibold tracking-tight leading-tight mb-6">
          Biomedical Data Health Dashboard
        </h2>

        <p className="text-muted-foreground max-w-2xl text-lg">
          Monitor scraper reliability, detect structural and semantic drift,
          and prevent unreliable biomedical data from reaching researchers.
        </p>
      </section>

      {/* Overall Health */}
      <section className="mb-8 rounded-2xl p-6 md:p-8 border-t" style={{ borderColor: 'rgba(15, 107, 94, 0.3)' }}>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              OVERALL SYSTEM HEALTH
            </p>

            <div className="mt-3 flex items-center gap-3">
              <svg className="w-6 h-6 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.57l-6.18 3.21L7 14.18 2 9.27l6.91-1.02L12 2z"/>
              </svg>
              <h3 className="text-2xl font-semibold text-emerald-400">
                HEALTHY
              </h3>
            </div>

            <p className="mt-2 text-sm text-slate-400">
              AI integrity monitoring is active across all connected sources.
            </p>
          </div>

          <div className="rounded-2xl p-6 md:p-8 text-center" style={{ background: 'rgba(15, 107, 94, 0.15)' }}>
            <p className="text-xs text-slate-400 uppercase tracking-wider">DATA CONFIDENCE</p>
            <p className="mt-2 text-4xl font-bold text-white">97%</p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Sources */}
        <section className="lg:col-span-2 rounded-2xl p-6 md:p-8 bg-card border border-border/30">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">Monitored Sources</h3>
              <p className="mt-1 text-sm text-slate-400/50">
                Live integrity assessment of incoming data.
              </p>
            </div>

            <span className="rounded-full bg-slate-400/20 px-3 py-1 text-xs text-slate-400/60">
              3 Sources
            </span>
          </div>

          <div className="space-y-4">
            {sources.map((source) => (
              <button
                key={source.name}
                onClick={() => setSelectedSource(source.name)}
                className={`w-full rounded-2xl p-5 text-left cursor-pointer transition-colors duration-200 ${
                  selectedSource === source.name
                    ? 'bg-primary/10 border-primary/40 border'
                    : 'hover:bg-slate-700 hover:border-slate-600/50'
                }`}
                style={{
                  background:
                    selectedSource === source.name
                      ? 'rgba(15, 107, 94, 0.1)'
                      : 'rgba(10, 14, 23, 0.5)',
                  border: selectedSource === source.name ? '1px rgba(15, 107, 94, 0.4)' : '1px rgba(255,255,255,0.05)',
                }}
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <h4 className="font-semibold text-white">
                      {source.name}
                    </h4>

                    <div className="mt-2 flex items-center gap-2 text-sm">
                      <svg className="w-3.5 h-3.5 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-12S17.52 2 12 2zm5.5 13.5l-2.5-2.5a1 1 0 0 0-1.42 1.42L14.17 15H10v2h4.17l1.95 1.95a1 1 0 0 0 1.42-1.42L17 16.5V13h2v3.5z"/>
                      </svg>

                      <span
                        className={
                          source.status === 'Healthy'
                            ? 'text-emerald-400'
                            : 'text-rose-400'
                        }
                      >
                        {source.status}
                      </span>
                    </div>
                  </div>

                  <div className="min-w-[180px]">
                    <div className="mb-2 flex justify-between text-sm">
                      <span className="text-slate-400/50">Confidence</span>
                      <span className="font-semibold text-white">{source.confidence}%</span>
                    </div>

                    <div className="h-3 overflow-hidden rounded-full bg-slate-800/50">
                      <div
                        className={`h-full rounded-full ${source.status === 'Healthy' ? 'bg-emerald-500' : 'bg-rose-500'}`}
                        style={{ width: `${source.confidence}%` }}
                      />
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Alert */}
        <aside className="rounded-2xl p-6 md:p-8 bg-card border border-border/30" style={{ borderColor: 'rgba(239, 68, 68, 0.2)' }}>
          <div className="flex items-center gap-3 mb-5">
            <div
              className="flex h-10 w-10 items-center justify-center rounded-md"
              style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)' }}
            >
              <svg className="w-5 h-5 text-rose-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-12S17.52 2 12 2zm1 15h-2v-2h2v2zM12 7l1 4h6l1-4H14l-2 4H5l2-4H12z"/>
              </svg>
            </div>

            <div>
              <p className="text-xs font-medium text-rose-400 uppercase tracking-wider">
                AI DRIFT ALERT
              </p>
              <h3 className="font-semibold text-white">SCRAPER DRIFT DETECTED</h3>
            </div>
          </div>

          <div className="rounded-xl p-4 mb-6" style={{ background: 'rgba(239, 68, 68, 0.08)' }}>
            <p className="text-xs font-medium text-slate-400/60">Affected source</p>
            <p className="mt-1 font-semibold text-white">{selectedSource}</p>
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-slate-400/50">
              Detected anomalies
            </p>

            <ul className="space-y-2 text-sm text-slate-400/50">
              <li className="flex gap-2">
                <span className="text-rose-400">•</span>
                Structural distribution shift
              </li>
              <li className="flex gap-2">
                <span className="text-rose-400">•</span>
                Semantic deviation detected
              </li>
              <li className="flex gap-2">
                <span className="text-rose-400">•</span>
                Missing expected fields
              </li>
            </ul>
          </div>

          <div className="mt-5 pt-5 border-t" style={{ borderColor: 'rgba(239, 68, 68, 0.2)' }}>
            <p className="text-xs font-medium text-slate-400/50">Data confidence</p>
            <p className="mt-1 text-3xl font-bold text-rose-400">42%</p>
          </div>
        </aside>
      </div>

      {/* Timeline */}
      <section className="mt-8 rounded-2xl p-6 md:p-8 bg-card border border-border/30">
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-white">Integrity Event Timeline</h3>
          <p className="mt-1 text-sm text-slate-400/50">
            Real-time monitoring events from the scraper integrity layer.
          </p>
        </div>

        <div className="space-y-3">
          {events.map((event, index) => (
            <div
              key={`${event.time}-${index}`}
              className="flex items-center gap-4 px-4 py-3 rounded-2xl hover:bg-slate-700 transition-colors"
              style={{
                borderLeft:
                  event.icon === 'drift'
                    ? '4px solid rgba(239, 68, 68, 0.5)'
                    : event.icon === 'variation'
                    ? '4px solid rgba(245, 158, 11, 0.5)'
                    : '4px solid rgba(46, 204, 113, 0.5)',
              }}
            >
              <span className="w-10 font-mono text-slate-400/60 text-sm">
                {event.time}
              </span>

              <span className="text-lg">
                {event.icon === 'scrape' && (
                  <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-12S17.52 2 12 2zm5.5 13.5l-2.5-2.5a1 1 0 0 0-1.42 1.42L14.17 15H10v2h4.17l1.95 1.95a1 1 0 0 0 1.42-1.42L17 16.5V13h2v3.5z"/>
                  </svg>
                )}
                {event.icon === 'variation' && (
                  <svg className="w-5 h-5 text-amber-500" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 12h.01L16 16v.01L8 8v.01zM12 4l.01 16v.01L4 12h.01v.01zm0 4l.01 8h16v.01L12 4v.01zM8.5 13l1.5 3h3l1.5-3H8.5zM15.5 13l-1.5 3h-3l-1.5-3h3z"/>
                  </svg>
                )}
                {event.icon === 'drift' && (
                  <svg className="w-5 h-5 text-rose-400" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm0 2c3.3 0 6 2.7 6 6s-2.7 6-6 6S6 15.3 6 12 8.7 6 12 6zM12 7l1 4h6l1-4H14l-2 4H5l2-4H12z"/>
                  </svg>
                )}
                {event.icon === 'heal' && (
                  <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-12S17.52 2 12 2zm0 8a8 8 0 1 0 0 16A8 8 0 0 1 12 4zm-1 6h2v2h-2v-2zm-4-4h2v2H8v-2zm8 4h2v2h-2v-2zM5 12h2a3 3 0 0 1 3 3v2a3 3 0 0 1-6v-2zm6.5-1.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
                  </svg>
                )}
              </span>

              <span className="text-slate-400/70 text-sm">{event.text}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Footer pitch */}
      <section className="mt-8 rounded-2xl p-6 bg-card border border-border/30 text-center">
        <p className="text-slate-400/60 leading-relaxed">
          <span className="font-semibold text-slate-400/80">
            BioIntel Guardian
          </span>{' '}
          is an AI-powered integrity layer that detects when biomedical web
          scrapers silently drift, helping ensure researchers receive
          trustworthy data rather than corrupted extractions.
        </p>
      </section>
    </>
  );
}
