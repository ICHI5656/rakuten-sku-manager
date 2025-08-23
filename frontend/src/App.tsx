import React, { useState } from 'react';
import { 
  Container, 
  Paper, 
  Typography, 
  Box, 
  Stepper, 
  Step, 
  StepLabel,
  Alert
} from '@mui/material';
import FileUpload from './components/FileUpload';
import DeviceManager from './components/DeviceManager';
import ProcessOptions from './components/ProcessOptions';
import ResultDownload from './components/ResultDownload';
import { ProcessRequest, ProcessResponse } from './types';
import { processCSV } from './services/api';

const steps = ['CSVアップロード', '機種管理', '処理オプション', 'ダウンロード'];

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [fileId, setFileId] = useState<string>('');
  const [devices, setDevices] = useState<string[]>([]);
  const [productDevices, setProductDevices] = useState<Record<string, string[]>>({});
  const [selectedDevices, setSelectedDevices] = useState<{
    toAdd: string[],
    toRemove: string[]
  }>({ toAdd: [], toRemove: [] });
  const [processResult, setProcessResult] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string>('');

  const handleFileUpload = (uploadedFileId: string, deviceList: string[], productDeviceMap?: Record<string, string[]>) => {
    setFileId(uploadedFileId);
    setDevices(deviceList);
    if (productDeviceMap) {
      setProductDevices(productDeviceMap);
    }
    setActiveStep(1);
  };

  const handleDeviceSelection = (devicesToAdd: string[], devicesToRemove: string[]) => {
    setSelectedDevices({ toAdd: devicesToAdd, toRemove: devicesToRemove });
    setActiveStep(2);
  };

  const handleProcess = async (outputFormat: string) => {
    try {
      setError('');
      const request: ProcessRequest = {
        file_id: fileId,
        devices_to_add: selectedDevices.toAdd,
        devices_to_remove: selectedDevices.toRemove,
        output_format: outputFormat
      };
      
      const result = await processCSV(request);
      setProcessResult(result);
      setActiveStep(3);
    } catch (err: any) {
      setError(err.message || '処理中にエラーが発生しました');
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    setFileId('');
    setDevices([]);
    setProductDevices({});
    setSelectedDevices({ toAdd: [], toRemove: [] });
    setProcessResult(null);
    setError('');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          楽天SKU管理システム
        </Typography>
        
        <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          楽天RMS CSV処理 - 機種追加・削除・SKU自動採番
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Box sx={{ mt: 3 }}>
          {activeStep === 0 && (
            <FileUpload onUploadSuccess={handleFileUpload} />
          )}
          
          {activeStep === 1 && (
            <DeviceManager 
              devices={devices}
              productDevices={productDevices}
              onNext={handleDeviceSelection}
              onBack={() => setActiveStep(0)}
            />
          )}
          
          {activeStep === 2 && (
            <ProcessOptions
              onProcess={handleProcess}
              onBack={() => setActiveStep(1)}
              selectedDevices={selectedDevices}
            />
          )}
          
          {activeStep === 3 && processResult && (
            <ResultDownload
              result={processResult}
              onReset={handleReset}
            />
          )}
        </Box>
      </Paper>
    </Container>
  );
}

export default App;