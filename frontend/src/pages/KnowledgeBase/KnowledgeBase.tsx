import React, { useEffect, useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  getKnowledgeBaseStatusApi,
  syncKnowledgeBaseApi,
  rebuildKBIndexApi,
  getFailedFilesApi
} from '../../services/api';
import {
  Database,
  RefreshCw,
  Cpu,
  AlertTriangle,
  FileText,
  Layers,
  CheckCircle,
  Clock,
  Search,
  HardDrive
} from 'lucide-react';

interface KBStatus {
  total_files: number;
  indexed_files: number;
  failed_files: number;
  total_chunks: number;
  last_sync: string | null;
  last_sync_status: string;
  faiss_vector_count: number;
  vector_dim: number;
  index_status: string;
}

interface FailedFile {
  google_drive_file_id: string;
  title: string;
  topic: string;
  error_message: string;
  status: string;
}

export const KnowledgeBasePage: React.FC = () => {
  const { authToken } = useApp();
  const [status, setStatus] = useState<KBStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [syncing, setSyncing] = useState<boolean>(false);
  const [rebuilding, setRebuilding] = useState<boolean>(false);
  const [failedFiles, setFailedFiles] = useState<FailedFile[]>([]);
  const [showFailedModal, setShowFailedModal] = useState<boolean>(false);
  const [errorAlert, setErrorAlert] = useState<string | null>(null);
  const [successAlert, setSuccessAlert] = useState<string | null>(null);

  const fetchStatus = async () => {
    if (!authToken) return;
    setLoading(true);
    setErrorAlert(null);
    try {
      const data = await getKnowledgeBaseStatusApi(authToken);
      setStatus(data);
    } catch (err: any) {
      setErrorAlert(err.message || 'Failed to connect to Knowledge Base backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [authToken]);

  const handleSync = async () => {
    if (!authToken || syncing) return;
    setSyncing(true);
    setErrorAlert(null);
    setSuccessAlert(null);
    try {
      const res = await syncKnowledgeBaseApi(authToken);
      if (res.success) {
        setSuccessAlert(`Sync completed! Indexed: ${res.indexed_files}, Skipped: ${res.skipped_files}, Failed: ${res.failed_files}`);
        fetchStatus();
      } else {
        setErrorAlert(res.message || res.error || 'Knowledge base sync failed.');
      }
    } catch (err: any) {
      setErrorAlert(err.message || 'Error executing Google Drive sync.');
    } finally {
      setSyncing(false);
    }
  };

  const handleRebuild = async () => {
    if (!authToken || rebuilding) return;
    setRebuilding(true);
    setErrorAlert(null);
    setSuccessAlert(null);
    try {
      const res = await rebuildKBIndexApi(authToken);
      if (res.success) {
        setSuccessAlert(`FAISS vector search index successfully rebuilt with ${res.reindexed_chunks} chunks.`);
        fetchStatus();
      }
    } catch (err: any) {
      setErrorAlert(err.message || 'Failed to rebuild search index.');
    } finally {
      setRebuilding(false);
    }
  };

  const handleFetchFailed = async () => {
    if (!authToken) return;
    try {
      const res = await getFailedFilesApi(authToken);
      setFailedFiles(res.failed_files || []);
      setShowFailedModal(true);
    } catch (err: any) {
      setErrorAlert('Failed to fetch failed document log.');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 p-6 rounded-2xl backdrop-blur-xl">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-tr from-cyan-500/20 to-blue-600/20 text-cyan-400 border border-cyan-500/30 rounded-xl">
            <HardDrive className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">GrowthOS Knowledge Base</h1>
            <p className="text-slate-400 text-sm">
              Local FAISS Semantic Vector Index & Google Drive Resource Management (0 OpenAI Embedding Cost)
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleSync}
            disabled={syncing || loading}
            className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium rounded-xl shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Scanning Drive...' : 'Sync Google Drive'}</span>
          </button>

          <button
            onClick={handleRebuild}
            disabled={rebuilding || loading}
            className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium rounded-xl transition-all disabled:opacity-50"
          >
            <Cpu className={`w-4 h-4 ${rebuilding ? 'animate-spin' : ''}`} />
            <span>{rebuilding ? 'Rebuilding Index...' : 'Rebuild Search Index'}</span>
          </button>
        </div>
      </div>

      {/* Alerts */}
      {errorAlert && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 flex items-start space-x-3 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Knowledge Base Error</span>
            {errorAlert}
          </div>
        </div>
      )}

      {successAlert && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 flex items-start space-x-3 text-sm">
          <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Operation Completed</span>
            {successAlert}
          </div>
        </div>
      )}

      {/* Real Metric Counters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Documents</span>
            <FileText className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-white">{loading ? '...' : status?.total_files ?? 0}</div>
          <p className="text-xs text-slate-500 mt-1">Files discovered in Drive KB</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Indexed Documents</span>
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-emerald-400">{loading ? '...' : status?.indexed_files ?? 0}</div>
          <p className="text-xs text-slate-500 mt-1">Parsed & vector indexed</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Chunks</span>
            <Layers className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-purple-400">{loading ? '...' : status?.total_chunks ?? 0}</div>
          <p className="text-xs text-slate-500 mt-1">384-dim text chunks</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Parse Failures</span>
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <div className="text-3xl font-bold text-rose-400">{loading ? '...' : status?.failed_files ?? 0}</div>
            {status && status.failed_files > 0 && (
              <button
                onClick={handleFetchFailed}
                className="text-xs text-rose-400 hover:text-rose-300 underline font-medium"
              >
                View Failed
              </button>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1">Failed file extractions</p>
        </div>
      </div>

      {/* Vector Index & Telemetry Card */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <Search className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-semibold text-white">Local FAISS Vector Index Telemetry</h2>
          </div>
          <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium rounded-full">
            {status?.index_status || 'Checking...'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="p-4 bg-slate-800/40 rounded-xl">
            <span className="text-slate-400 text-xs block mb-1">Embedding Architecture</span>
            <span className="text-white font-mono font-medium">SentenceTransformers (all-MiniLM-L6-v2)</span>
          </div>

          <div className="p-4 bg-slate-800/40 rounded-xl">
            <span className="text-slate-400 text-xs block mb-1">FAISS Vector Count</span>
            <span className="text-cyan-400 font-mono font-bold">{status?.faiss_vector_count ?? 0} vectors</span>
          </div>

          <div className="p-4 bg-slate-800/40 rounded-xl">
            <span className="text-slate-400 text-xs block mb-1">Last Ingestion Run</span>
            <span className="text-slate-300 font-mono text-xs">
              {status?.last_sync ? new Date(status.last_sync).toLocaleString() : 'Never Synced'}
            </span>
          </div>
        </div>
      </div>

      {/* Failed Files Modal */}
      {showFailedModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-rose-400" />
                <span>Failed Document Log ({failedFiles.length})</span>
              </h3>
              <button
                onClick={() => setShowFailedModal(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                Close
              </button>
            </div>

            {failedFiles.length === 0 ? (
              <p className="text-slate-400 text-sm">No failed document parse records found.</p>
            ) : (
              <div className="space-y-3">
                {failedFiles.map((file, idx) => (
                  <div key={idx} className="p-4 bg-rose-500/5 border border-rose-500/20 rounded-xl space-y-1">
                    <div className="flex justify-between items-center text-sm font-semibold text-white">
                      <span>{file.title}</span>
                      <span className="text-xs text-slate-400 font-mono">{file.topic}</span>
                    </div>
                    <p className="text-xs text-rose-300 font-mono">{file.error_message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
