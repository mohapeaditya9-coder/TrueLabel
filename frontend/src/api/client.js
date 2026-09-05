const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error('Failed to reach backend:', err);
    throw err;
  }
}

/**
 * Uploads an image file to the backend with progress tracking.
 * @param {File} file 
 * @param {Function} onProgress (percent: number) => void
 * @returns {Promise<Object>} ScanUploadResponse
 */
export function uploadLabelImage(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.open('POST', `${API_BASE_URL}/api/scan/upload`, true);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          reject(new Error('Invalid JSON response from server'));
        }
      } else {
        let errorMessage = `Upload failed with status ${xhr.status}`;
        try {
          const errorData = JSON.parse(xhr.responseText);
          if (errorData.detail) errorMessage = errorData.detail;
        } catch (_) {}
        reject(new Error(errorMessage));
      }
    };

    xhr.onerror = () => {
      reject(new Error('Network error during file upload'));
    };

    xhr.send(formData);
  });
}

/**
 * Fetches status of a scan by scan_id
 * @param {string} scanId 
 */
export async function getScanStatus(scanId) {
  const res = await fetch(`${API_BASE_URL}/api/scan/${scanId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch scan details: ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Helper to build the static URL for uploaded image
 * @param {string} filename 
 */
export function getImageUrl(filename) {
  if (!filename) return '';
  return `${API_BASE_URL}/uploads/${filename}`;
}
