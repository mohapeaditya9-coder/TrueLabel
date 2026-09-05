import React, { useState, useEffect } from 'react';
import ImageUploader from '../components/ImageUploader';
import ScanResultCard from '../components/ScanResultCard';
import HealthStatus from '../components/HealthStatus';
import { ShieldCheck, History, Upload, Sparkles, CheckCircle2 } from 'lucide-react';

export default function HomePage() {
  const [activeScan, setActiveScan] = useState(null);
  const [recentScans, setRecentScans] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const fetchRecentScans = async () => {
    try {
      setLoadingHistory(true);
      const res = await fetch('http://localhost:8000/api/scan/?limit=5');
      if (res.ok) {
        const data = await res.json();
        setRecentScans(data);
      }
    } catch (_) {
      // ignore history fetch error if backend not ready
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchRecentScans();
  }, [activeScan]);

  const handleUploadSuccess = (scanResponse) => {
    setActiveScan(scanResponse);
  };

  const handleReset = () => {
    setActiveScan(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between text-slate-800">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-700 flex items-center justify-center text-white shadow-xs">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold text-slate-900 tracking-tight">
                  LMPC Compliance Scanner
                </h1>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                  SIH26034
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Legal Metrology (Packaged Commodities) Rules, 2011 Automated Verification
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Phase 1 Active
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full space-y-8">
        {/* Phase Header Info */}
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Commodity Label Compliance Scan
          </h2>
          <p className="text-sm text-slate-600 mt-2">
            Upload an image of a packaged commodity label to initiate validation against mandatory
            declarations under Rule 6 of the Legal Metrology Rules, 2011.
          </p>
        </div>

        {/* Upload or Result Card */}
        <div>
          {!activeScan ? (
            <ImageUploader onUploadSuccess={handleUploadSuccess} />
          ) : (
            <ScanResultCard scanData={activeScan} onReset={handleReset} />
          )}
        </div>

        {/* Recent Uploads Audit Strip */}
        {recentScans.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-slate-500" />
                <h3 className="text-sm font-bold text-slate-800">Recent Uploads (Database Records)</h3>
              </div>
              <span className="text-xs text-slate-400">Total stored: {recentScans.length}</span>
            </div>

            <div className="divide-y divide-slate-100">
              {recentScans.map((scan) => (
                <div
                  key={scan.scan_id}
                  onClick={() => setActiveScan(scan)}
                  className="py-3 flex items-center justify-between hover:bg-slate-50/80 px-2 rounded-lg cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0 text-xs font-mono font-bold">
                      #{scan.id}
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-800 truncate">
                        {scan.original_filename}
                      </p>
                      <p className="text-[11px] text-slate-400 font-mono truncate">
                        {scan.scan_id}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-500 hidden sm:inline">
                      {(scan.file_size / 1024).toFixed(1)} KB
                    </span>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                      {scan.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Backend Connectivity Status Widget */}
        <HealthStatus />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500 bg-white">
        Smart India Hackathon • SIH26034 • Legal Metrology (Packaged Commodities) Rules, 2011 Scanner
      </footer>
    </div>
  );
}
