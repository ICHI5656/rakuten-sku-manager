import axios from 'axios';
import { ProcessRequest, ProcessResponse, UploadResponse } from '../types';

const API_BASE = '/api';

export const uploadCSV = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const processCSV = async (request: ProcessRequest): Promise<ProcessResponse> => {
  const response = await axios.post(`${API_BASE}/process`, request);
  return response.data;
};

export const getDevices = async (fileId: string): Promise<string[]> => {
  const response = await axios.get(`${API_BASE}/devices/${fileId}`);
  return response.data.devices;
};

export const downloadFile = (filename: string): void => {
  window.open(`${API_BASE}/download/${filename}`, '_blank');
};

export const getSystemStatus = async () => {
  const response = await axios.get(`${API_BASE}/status`);
  return response.data;
};

export const cleanupOldFiles = async () => {
  const response = await axios.delete(`${API_BASE}/cleanup`);
  return response.data;
};

// Batch processing APIs
export const uploadBatchCSV = async (formData: FormData) => {
  const response = await axios.post(`${API_BASE}/batch-upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const processBatchCSV = async (
  batchId: string,
  devicesToAdd: string[],
  devicesToRemove: string[],
  outputFormat: string = 'single',
  applyToAll: boolean = true
) => {
  const formData = new FormData();
  formData.append('batch_id', batchId);
  formData.append('devices_to_add', JSON.stringify(devicesToAdd));
  formData.append('devices_to_remove', JSON.stringify(devicesToRemove));
  formData.append('output_format', outputFormat);
  formData.append('apply_to_all', applyToAll.toString());
  
  const response = await axios.post(`${API_BASE}/batch-process`, formData);
  return response.data;
};

export const getBatchStatus = async (batchId: string) => {
  const response = await axios.get(`${API_BASE}/batch-status/${batchId}`);
  return response.data;
};

export const downloadBatchResults = async (batchId: string): Promise<Blob> => {
  const response = await fetch(`${API_BASE}/batch-download/${batchId}`);
  
  if (!response.ok) {
    throw new Error('バッチ結果のダウンロードに失敗しました');
  }
  
  return response.blob();
};