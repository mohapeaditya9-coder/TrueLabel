import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, AlertTriangle, FileCheck, Loader2 } from 'lucide-react';
import { uploadLabelImage } from '../api/client';

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export default function ImageUploader({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    setError(null);
    if (!file) return false;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError(`Invalid file type (${file.type || 'unknown'}). Please upload a JPG, PNG, or WEBP image.`);
      return false;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError(`File is too large (${(file.size / (1024 * 1024)).toFixed(2)} MB). Maximum allowed size is ${MAX_FILE_SIZE_MB} MB.`);
      return false;
    }

    return true;
  };

  const handleFileSelection = (file) => {
    if (!validateFile(file)) {
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      const response = await uploadLabelImage(selectedFile, (progress) => {
        setUploadProgress(progress);
      });
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (err) {
      setError(err.message || 'Failed to upload label image.');
    } finally {
      setUploading(false);
    }
  };

  const resetSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setUploadProgress(0);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8">
      <div className="mb-6 text-center">
        <h3 className="text-xl font-bold text-slate-800 tracking-tight">Upload Packaged Commodity Label</h3>
        <p className="text-sm text-slate-500 mt-1">
          Upload front, back, or side display packaging images to check compliance under LMPC Rules, 2011.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3 text-red-700 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-500 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold">Upload Error: </span>
            {error}
          </div>
        </div>
      )}

      {/* Drag and Drop Zone */}
      {!selectedFile ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
            dragActive
              ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]'
              : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleChange}
            className="hidden"
          />
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4">
            <UploadCloud className="w-8 h-8" />
          </div>
          <p className="text-base font-semibold text-slate-700">
            Drag and drop your label image here, or{' '}
            <span className="text-indigo-600 underline">browse</span>
          </p>
          <p className="text-xs text-slate-400 mt-2">
            Supports JPG, PNG, and WEBP (Max 10MB)
          </p>
        </div>
      ) : (
        /* Selected Image Preview & Upload Controls */
        <div className="border border-slate-200 rounded-2xl p-6 bg-slate-50/50">
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <div className="w-36 h-36 rounded-xl border border-slate-200 bg-white overflow-hidden flex items-center justify-center flex-shrink-0 shadow-xs">
              <img
                src={previewUrl}
                alt="Label Preview"
                className="w-full h-full object-contain"
              />
            </div>

            <div className="flex-1 min-w-0 w-full">
              <div className="flex items-center gap-2 text-indigo-600 font-medium text-sm mb-1">
                <FileCheck className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{selectedFile.name}</span>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Type: {selectedFile.type}
              </p>

              {/* Progress Bar */}
              {uploading && (
                <div className="mb-4">
                  <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                    <span>Uploading image...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-200"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={handleUpload}
                  disabled={uploading}
                  className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold shadow-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  {uploading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Uploading ({uploadProgress}%)
                    </>
                  ) : (
                    'Start Scan'
                  )}
                </button>
                <button
                  type="button"
                  onClick={resetSelection}
                  disabled={uploading}
                  className="px-4 py-2.5 border border-slate-300 text-slate-700 hover:bg-slate-100 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 cursor-pointer"
                >
                  Change File
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
