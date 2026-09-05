import React, { useState } from 'react';
import { CheckCircle2, Copy, Check, Clock, FileText, Database, ArrowLeft, RefreshCw, Cpu } from 'lucide-react';
import { getImageUrl } from '../api/client';

export default function ScanResultCard({ scanData, onReset }) {
  const [copied, setCopied] = useState(false);

  if (!scanData) return null;

  const copyScanId = () => {
    navigator.clipboard.writeText(scanData.scan_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const imageUrl = getImageUrl(scanData.image_filename);
  const formattedSize = (scanData.file_size / 1024).toFixed(1) + ' KB';
  const uploadTime = scanData.uploaded_at ? new Date(scanData.uploaded_at).toLocaleString() : 'Just now';

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 to-slate-900 text-white p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Phase 1 Complete
              </span>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Status: {scanData.status.toUpperCase()}
              </span>
            </div>
            <h3 className="text-xl font-bold tracking-tight">Label Uploaded & Stored</h3>
          </div>

          <button
            onClick={onReset}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/20 transition-colors border border-white/10 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            Upload Another Image
          </button>
        </div>
      </div>

      <div className="p-6 md:p-8 space-y-6">
        {/* Processing State Notice */}
        <div className="p-4 rounded-xl bg-indigo-50/80 border border-indigo-200 flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
            <Cpu className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-indigo-950 flex items-center gap-2">
              Processing...
              <span className="text-xs font-normal text-indigo-700">(Queued for OCR Extraction)</span>
            </h4>
            <p className="text-xs text-indigo-800 mt-1 leading-relaxed">
              Image verified, hashed, and stored in <code className="bg-indigo-100 px-1 py-0.5 rounded text-indigo-900 font-mono">/uploads/{scanData.image_filename}</code>.
              Database record registered with status <span className="font-semibold text-indigo-900 font-mono">"pending"</span>.
              OCR text & bounding box extraction will connect to this scan ID in Phase 2.
            </p>
          </div>
        </div>

        {/* Scan ID Box */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="min-w-0">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-0.5">
              Assigned Scan ID
            </span>
            <span className="font-mono text-sm sm:text-base font-bold text-slate-800 break-all select-all">
              {scanData.scan_id}
            </span>
          </div>
          <button
            onClick={copyScanId}
            className="flex items-center justify-center gap-1.5 px-4 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg text-xs font-medium shadow-xs transition-colors flex-shrink-0 cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-emerald-600" />
                <span className="text-emerald-700 font-semibold">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 text-slate-500" />
                <span>Copy ID</span>
              </>
            )}
          </button>
        </div>

        {/* Image Preview and Metadata Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Stored Image Thumbnail */}
          <div className="md:col-span-1">
            <h5 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5" />
              Stored Label Image
            </h5>
            <div className="aspect-square w-full rounded-xl border border-slate-200 bg-slate-100 overflow-hidden flex items-center justify-center p-2 shadow-xs">
              <img
                src={imageUrl}
                alt="Uploaded Commodity Label"
                className="w-full h-full object-contain rounded-lg"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            </div>
            <p className="text-[11px] text-slate-400 text-center mt-1 truncate">
              {scanData.image_filename}
            </p>
          </div>

          {/* Metadata Cards */}
          <div className="md:col-span-2 space-y-3">
            <h5 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" />
              Database Record Details
            </h5>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-400 block mb-0.5">Original File</span>
                <span className="font-medium text-slate-800 truncate block" title={scanData.original_filename}>
                  {scanData.original_filename}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-400 block mb-0.5">File Size</span>
                <span className="font-medium text-slate-800">{formattedSize}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-400 block mb-0.5">Uploaded Timestamp</span>
                <span className="font-medium text-slate-800">{uploadTime}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-400 block mb-0.5">MIME Format</span>
                <span className="font-medium text-slate-800 uppercase">{scanData.mime_type}</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
              <span className="text-slate-400 block mb-1">Server File Path</span>
              <code className="text-[11px] text-slate-700 bg-white p-1.5 rounded border border-slate-200 block truncate select-all font-mono">
                {scanData.image_path}
              </code>
            </div>

            {scanData.file_hash && (
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                <span className="text-slate-400 block mb-1">SHA-256 Checksum</span>
                <code className="text-[11px] text-slate-700 bg-white p-1.5 rounded border border-slate-200 block truncate select-all font-mono">
                  {scanData.file_hash}
                </code>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
