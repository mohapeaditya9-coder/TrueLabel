import React, { useEffect, useState } from 'react';
import { checkBackendHealth } from '../api/client';
import { Activity, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function HealthStatus() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await checkBackendHealth();
      setHealthData(data);
    } catch (err) {
      setError(err.message || 'Connection failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 max-w-lg mx-auto">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-600" />
          <h2 className="font-semibold text-slate-800 text-lg">Backend Health Status</h2>
        </div>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors border border-slate-200"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading && (
        <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg text-slate-500 text-sm">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-600" />
          Connecting to backend at http://localhost:8000/health...
        </div>
      )}

      {error && !loading && (
        <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-500 mt-0.5" />
          <div>
            <p className="font-medium">Backend Offline or Unreachable</p>
            <p className="text-xs text-red-600 mt-1">{error}</p>
          </div>
        </div>
      )}

      {healthData && !loading && (
        <div className="flex items-start gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-sm">
          <CheckCircle className="w-5 h-5 flex-shrink-0 text-emerald-600 mt-0.5" />
          <div>
            <p className="font-semibold text-emerald-900">
              Backend Connected ({healthData.status.toUpperCase()})
            </p>
            <div className="mt-2 space-y-1 text-xs text-emerald-700">
              <p><span className="font-medium">Service:</span> {healthData.service}</p>
              <p><span className="font-medium">Version:</span> {healthData.version}</p>
              <p><span className="font-medium">Endpoint:</span> /health</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
