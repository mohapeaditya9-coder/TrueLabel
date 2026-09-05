import React from 'react';
import HealthStatus from '../components/HealthStatus';
import { ShieldCheck } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
      <header className="bg-white border-b border-slate-200 py-4 px-6 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                LMPC Compliance Scanner
              </h1>
              <p className="text-xs text-slate-500">
                Smart India Hackathon (SIH26034) • Legal Metrology (Packaged Commodities) Rules, 2011
              </p>
            </div>
          </div>
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
            Phase 0: Skeleton Setup
          </span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 flex-1 w-full">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-slate-800 tracking-tight mb-3">
            Project Skeleton Verification
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto text-sm">
            End-to-end skeleton is active. This page verifies that the React Vite frontend
            is able to communicate with the FastAPI backend health endpoint.
          </p>
        </div>

        <HealthStatus />
      </main>

      <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-500 bg-white">
        SIH26034 Project Skeleton • Ready for Phase 1 (Image Upload & Storage)
      </footer>
    </div>
  );
}
