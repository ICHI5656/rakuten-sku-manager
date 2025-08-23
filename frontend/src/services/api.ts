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