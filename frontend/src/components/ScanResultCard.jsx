import React, { useState, useEffect } from 'react';
import {
  CheckCircle2, Copy, Check, Clock, FileText, Database,
  ArrowLeft, RefreshCw, Cpu, AlignLeft, Layers, ExternalLink, AlertCircle
} from 'lucide-react';
import { getImageUrl } from '../api/client';

export default function ScanResultCard({ scanData, onReset }) {
  const [copied, setCopied] = useState(false);
  const [ocrData, setOcrData] = useState(null);
  const [loadingOcr, setLoadingOcr] = useState(false);
  const [ocrError, setOcrError] = useState(null);
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'blocks' | 'json'

  const fetchOcrResults = async (scanId) => {
    try {
      setLoadingOcr(true);
      setOcrError(null);
      const res = await fetch(`http://localhost:8000/api/scan/${scanId}/raw-text`);
      if (res.ok) {
        const data = await res.json();
        setOcrData(data);
      } else {
        setOcrError('Failed to fetch OCR text details');
      }
    } catch (err) {
      setOcrError(err.message || 'Error connecting to OCR endpoint');
    } finally {
      setLoadingOcr(false);
    }
  };

  useEffect(() => {
    if (scanData?.scan_id) {
      fetchOcrResults(scanData.scan_id);
    }
  }, [scanData?.scan_id]);

  if (!scanData) return null;

  const copyScanId = () => {
    navigator.clipboard.writeText(scanData.scan_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const imageUrl = getImageUrl(scanData.image_filename);
  const formattedSize = (scanData.file_size / 1024).toFixed(1) + ' KB';
  const uploadTime = scanData.uploaded_at ? new Date(scanData.uploaded_at).toLocaleString() : 'Just now';
  const isProcessed = scanData.status === 'processed' || ocrData?.status === 'processed';

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-900 text-white p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                Phase 2: OCR Extractor
              </span>
              {isProcessed ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  OCR Complete ({ocrData?.total_blocks || 0} blocks)
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  Status: {scanData.status.toUpperCase()}
                </span>
              )}
            </div>
            <h3 className="text-xl font-bold tracking-tight">Label OCR Extraction View</h3>
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
        {/* Scan ID Header */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="min-w-0">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block mb-0.5">
              Assigned Scan ID
            </span>
            <span className="font-mono text-sm sm:text-base font-bold text-slate-800 break-all select-all">
              {scanData.scan_id}
            </span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={copyScanId}
              className="flex items-center justify-center gap-1.5 px-3.5 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg text-xs font-medium shadow-xs transition-colors cursor-pointer"
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
            <a
              href={`http://localhost:8000/api/scan/${scanData.scan_id}/raw-text`}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-medium transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Raw API
            </a>
          </div>
        </div>

        {/* 2-Column Grid: Image on Left, OCR Extraction Tabs on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Column 1: Image & Metadata (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 overflow-hidden shadow-xs">
              <div className="px-4 py-2.5 bg-slate-100/80 border-b border-slate-200 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-indigo-600" />
                  Scanned Product Label
                </span>
                <span className="text-[11px] text-slate-400 font-mono">
                  {scanData.image_filename}
                </span>
              </div>
              <div className="aspect-4/3 w-full bg-slate-900/5 flex items-center justify-center p-3">
                <img
                  src={imageUrl}
                  alt="Scanned Label"
                  className="max-h-72 w-auto object-contain rounded shadow-xs"
                />
              </div>
            </div>

            {/* Quick Metadata */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-400 block text-[11px]">Filename</span>
                <span className="font-medium text-slate-800 truncate block" title={scanData.original_filename}>
                  {scanData.original_filename}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-400 block text-[11px]">File Size</span>
                <span className="font-medium text-slate-800">{formattedSize}</span>
              </div>
            </div>
          </div>

          {/* Column 2: OCR Extracted Text & Bounding Boxes (7 cols) */}
          <div className="lg:col-span-7 flex flex-col">
            <div className="border border-slate-200 rounded-xl overflow-hidden flex-1 flex flex-col bg-white shadow-xs">
              {/* Tab Navigation */}
              <div className="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-200">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setActiveTab('text')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
                      activeTab === 'text'
                        ? 'bg-white text-indigo-600 shadow-xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <AlignLeft className="w-3.5 h-3.5" />
                    Reconstructed Text
                  </button>
                  <button
                    onClick={() => setActiveTab('blocks')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
                      activeTab === 'blocks'
                        ? 'bg-white text-indigo-600 shadow-xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <Layers className="w-3.5 h-3.5" />
                    OCR Blocks ({ocrData?.total_blocks || 0})
                  </button>
                  <button
                    onClick={() => setActiveTab('json')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
                      activeTab === 'json'
                        ? 'bg-white text-indigo-600 shadow-xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    JSON
                  </button>
                </div>

                <span className="text-[11px] font-medium text-slate-400">
                  EasyOCR Engine
                </span>
              </div>

              {/* Tab Content */}
              <div className="p-4 flex-1 min-h-[300px] overflow-auto max-h-[420px]">
                {loadingOcr && (
                  <div className="flex flex-col items-center justify-center py-12 text-slate-400 text-sm">
                    <RefreshCw className="w-6 h-6 animate-spin text-indigo-600 mb-2" />
                    <span>Extracting text blocks with EasyOCR...</span>
                  </div>
                )}

                {ocrError && (
                  <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <div>{ocrError}</div>
                  </div>
                )}

                {!loadingOcr && !ocrError && ocrData && (
                  <>
                    {/* Reconstructed Text Tab */}
                    {activeTab === 'text' && (
                      <div className="space-y-3">
                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 font-mono text-xs text-slate-800 whitespace-pre-wrap leading-relaxed select-all">
                          {ocrData.full_text || 'No text extracted.'}
                        </div>
                        <p className="text-[11px] text-slate-400">
                          Reconstructed raw text lines in detection order. Ready for Field Classifier (Phase 3).
                        </p>
                      </div>
                    )}

                    {/* Bounding Box Blocks Tab */}
                    {activeTab === 'blocks' && (
                      <div className="space-y-2.5">
                        {ocrData.blocks?.map((block, idx) => (
                          <div
                            key={idx}
                            className="p-3 rounded-lg border border-slate-200 bg-slate-50/70 hover:bg-slate-50 transition-colors text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-slate-900 font-mono">
                                #{idx + 1}: "{block.text}"
                              </span>
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  block.confidence > 0.8
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : block.confidence > 0.5
                                    ? 'bg-amber-100 text-amber-800'
                                    : 'bg-red-100 text-red-800'
                                }`}
                              >
                                {(block.confidence * 100).toFixed(1)}% conf
                              </span>
                            </div>
                            <div className="text-[11px] font-mono text-slate-500 truncate">
                              BBox: {JSON.stringify(block.bounding_box)}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Raw JSON Tab */}
                    {activeTab === 'json' && (
                      <pre className="bg-slate-900 text-slate-100 rounded-xl p-4 text-[11px] font-mono overflow-auto max-h-[380px]">
                        {JSON.stringify(ocrData, null, 2)}
                      </pre>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
