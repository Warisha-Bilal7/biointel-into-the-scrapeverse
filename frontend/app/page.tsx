'use client';

import { useState } from 'react';

const sources = [
  {
    name: 'Clinical Data',
    status: 'Healthy',
    confidence: 98,
    color: 'green',
  },
  {
    name: 'Drug Database',
    status: 'Healthy',
    confidence: 96,
    color: 'green',
  },
  {
    name: 'Research Source',
    status: 'Drift Detected',
    confidence: 42,
    color: 'red',
  },
];

const events = [
  {
    time: '10:00',
    icon: '🟢',
    text: 'Scrape completed',
  },
  {
    time: '10:01',
    icon: '🟢',
    text: 'Payload validated',
  },
  {
    time: '10:15',
    icon: '🟡',
    text: 'Structural variation noticed',
  },
  {
    time: '10:16',
    icon: '🔴',
    text: 'AI drift detected',
  },
  {
    time: '10:17',
    icon: '⚙️',
    text: 'Self-healing review triggered',
  },
];

export default function Home() {
  const [selectedSource, setSelectedSource] = useState('Research Source');

  return (
    <main className="min-h-screen bg-[#07111f] text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-[#091625]">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-500/15 text-2xl">
                🧬
              </div>

              <div>
                <h1 className="text-xl font-bold tracking-tight">
                  BioIntel Guardian
                </h1>
                <p className="text-xs text-slate-400">
                  Biomedical Data Integrity Monitor
                </p>
              </div>
            </div>
          </div>

          <div className="hidden items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400 md:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            System Monitoring Active
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Hero */}
        <section className="mb-8">
          <p className="mb-2 text-sm font-medium text-cyan-400">
            AI-POWERED DATA INTEGRITY
          </p>

          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
            Biomedical Data Health Dashboard
          </h2>

          <p className="mt-3 max-w-2xl text-slate-400">
            Monitor scraper reliability, detect structural and semantic drift,
            and prevent unreliable biomedical data from reaching researchers.
          </p>
        </section>

        {/* Overall Health */}
        <section className="mb-8 rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 to-transparent p-6">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
            <div>
              <p className="text-sm text-slate-400">OVERALL SYSTEM HEALTH</p>

              <div className="mt-2 flex items-center gap-3">
                <span className="text-3xl">🟢</span>
                <h3 className="text-2xl font-bold text-emerald-400">HEALTHY</h3>
              </div>

              <p className="mt-2 text-slate-300">
                AI integrity monitoring is active across all connected sources.
              </p>
            </div>

            <div className="rounded-2xl bg-[#07111f]/70 px-8 py-5 text-center">
              <p className="text-sm text-slate-400">DATA CONFIDENCE</p>
              <p className="mt-1 text-4xl font-bold text-white">97%</p>
            </div>
          </div>
        </section>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Sources */}
          <section className="rounded-2xl border border-slate-800 bg-[#0b1726] p-6 lg:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold">Monitored Sources</h3>
                <p className="mt-1 text-sm text-slate-400">
                  Live integrity assessment of incoming data.
                </p>
              </div>

              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                3 Sources
              </span>
            </div>

            <div className="space-y-4">
              {sources.map((source) => (
                <button
                  key={source.name}
                  onClick={() => setSelectedSource(source.name)}
                  className={`w-full rounded-xl border p-5 text-left transition ${
                    selectedSource === source.name
                      ? 'border-cyan-500/60 bg-cyan-500/5'
                      : 'border-slate-800 bg-[#09131f] hover:border-slate-600'
                  }`}
                >
                  <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                      <h4 className="font-semibold text-white">
                        {source.name}
                      </h4>

                      <div className="mt-2 flex items-center gap-2 text-sm">
                        <span>{source.color === 'green' ? '🟢' : '🔴'}</span>

                        <span
                          className={
                            source.color === 'green'
                              ? 'text-emerald-400'
                              : 'text-red-400'
                          }
                        >
                          {source.status}
                        </span>
                      </div>
                    </div>

                    <div className="min-w-[180px]">
                      <div className="mb-2 flex justify-between text-sm">
                        <span className="text-slate-400">Confidence</span>
                        <span className="font-semibold">
                          {source.confidence}%
                        </span>
                      </div>

                      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                        <div
                          className={`h-full rounded-full ${
                            source.color === 'green'
                              ? 'bg-emerald-400'
                              : 'bg-red-500'
                          }`}
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
          <aside className="rounded-2xl border border-red-500/30 bg-red-500/[0.06] p-6">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-red-500/15 text-xl">
                🚨
              </div>

              <div>
                <p className="text-xs font-medium text-red-400">
                  AI DRIFT ALERT
                </p>
                <h3 className="font-bold">SCRAPER DRIFT DETECTED</h3>
              </div>
            </div>

            <div className="mt-6 rounded-xl border border-red-500/20 bg-[#09131f] p-4">
              <p className="text-sm text-slate-400">Affected source</p>
              <p className="mt-1 font-semibold text-white">{selectedSource}</p>
            </div>

            <div className="mt-5">
              <p className="mb-3 text-sm font-medium text-slate-300">
                Detected anomalies
              </p>

              <ul className="space-y-3 text-sm text-slate-400">
                <li className="flex gap-2">
                  <span className="text-red-400">•</span>
                  Structural distribution shift
                </li>
                <li className="flex gap-2">
                  <span className="text-red-400">•</span>
                  Semantic deviation detected
                </li>
                <li className="flex gap-2">
                  <span className="text-red-400">•</span>
                  Missing expected fields
                </li>
              </ul>
            </div>

            <div className="mt-6 border-t border-red-500/20 pt-5">
              <p className="text-sm text-slate-400">Data confidence</p>
              <p className="mt-1 text-3xl font-bold text-red-400">42%</p>
            </div>
          </aside>
        </div>

        {/* Timeline */}
        <section className="mt-8 rounded-2xl border border-slate-800 bg-[#0b1726] p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold">Integrity Event Timeline</h3>
            <p className="mt-1 text-sm text-slate-400">
              Real-time monitoring events from the scraper integrity layer.
            </p>
          </div>

          <div className="space-y-1">
            {events.map((event, index) => (
              <div
                key={`${event.time}-${index}`}
                className="flex items-center gap-5 rounded-xl px-4 py-4 hover:bg-slate-800/40"
              >
                <span className="w-12 font-mono text-sm text-slate-500">
                  {event.time}
                </span>

                <span className="text-lg">{event.icon}</span>

                <span className="text-sm text-slate-300">{event.text}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Footer pitch */}
        <section className="mt-8 rounded-2xl border border-cyan-500/15 bg-cyan-500/[0.04] p-6 text-center">
          <p className="text-sm leading-7 text-slate-300">
            <span className="font-semibold text-cyan-400">
              BioIntel Guardian
            </span>{' '}
            is an AI-powered integrity layer that detects when biomedical web
            scrapers silently drift, helping ensure researchers receive
            trustworthy data rather than corrupted extractions.
          </p>
        </section>
      </div>
    </main>
  );
}
