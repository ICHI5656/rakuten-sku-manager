import React, { useState } from 'react';
import { 
  Container, 
  Paper, 
  Typography, 
  Box, 
  Stepper, 
  Step, 
  StepLabel,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import FileUpload from './components/FileUpload';
import BatchFileUpload from './components/BatchFileUpload';
import DeviceManager from './components/DeviceManager';
import ProcessOptions from './components/ProcessOptions';
import ResultDownload from './components/ResultDownload';
import BatchProcessor from './components/BatchProcessor';
import { ProcessRequest, ProcessResponse } from './types';
import { processCSV, processBatchCSV } from './services/api';

const steps = ['CSVアップロード', '機種管理', '処理オプション', 'ダウンロード'];
const batchSteps = ['ファイル選択', '機種管理', '一括処理', '結果確認'];

function App() {
  const [mode, setMode] = useState<'single' | 'batch'>('single');
  const [activeStep, setActiveStep] = useState(0);
  const [fileId, setFileId] = useState<string>('');
  const [batchId, setBatchId] = useState<string>('');
  const [batchFiles, setBatchFiles] = useState<any[]>([]);
  const [devices, setDevices] = useState<string[]>([]);
  const [productDevices, setProductDevices] = useState<Record<string, string[]>>({});
  const [selectedDevices, setSelectedDevices] = useState<{
    toAdd: string[],
    toRemove: string[],
    position?: 'start' | 'end' | 'after' | 'custom' | 'final_order',
    afterDevice?: string,
    customDeviceOrder?: string[],
    insertIndex?: number,
    deviceBrand?: string,
    deviceAttributes?: Array<{device: string, attribute_value?: string, size_category?: string}>
  }>({ toAdd: [], toRemove: [] });
  const [processResult, setProcessResult] = useState<ProcessResponse | null>(null);
  const [batchResult, setBatchResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [autoFillAltText, setAutoFillAltText] = useState<boolean>(true);

  const handleModeChange = (_event: React.SyntheticEvent, newMode: 'single' | 'batch') => {
    setMode(newMode);
    handleReset();
  };

  const handleFileUpload = (uploadedFileId: string, deviceList: string[], productDeviceMap?: Record<string, string[]>) => {
    setFileId(uploadedFileId);
    setDevices(deviceList);
    if (productDeviceMap) {
      setProductDevices(productDeviceMap);
    }
    setActiveStep(1);
  };

  const handleBatchUpload = (uploadedBatchId: string, files: any[], allDevices: string[], allProductDevices?: Record<string, string[]>) => {
    console.log('App.tsx handleBatchUpload - allDevices:', allDevices);
    console.log('App.tsx handleBatchUpload - allProductDevices:', allProductDevices);
    setBatchId(uploadedBatchId);
    setBatchFiles(files);
    setDevices(allDevices);
    if (allProductDevices) {
      setProductDevices(allProductDevices);
    }
    setActiveStep(1);
  };

  const handleDeviceSelection = (
    devicesToAdd: string[], 
    devicesToRemove: string[], 
    position?: 'start' | 'end' | 'after' | 'custom' | 'final_order', 
    afterDevice?: string,
    customDeviceOrder?: string[],
    insertIndex?: number,
    deviceBrand?: string,
    deviceAttributes?: Array<{device: string, attribute_value?: string, size_category?: string}>
  ) => {
    setSelectedDevices({ 
      toAdd: devicesToAdd, 
      toRemove: devicesToRemove,
      position: position,
      afterDevice: afterDevice,
      customDeviceOrder: customDeviceOrder,
      insertIndex: insertIndex,
      deviceBrand: deviceBrand,
      deviceAttributes: deviceAttributes
    });
    setActiveStep(2);
  };

  const handleProcess = async (outputFormat: string) => {
    try {
      setError('');
      
      if (mode === 'single') {
        const request: ProcessRequest = {
          file_id: fileId,
          devices_to_add: selectedDevices.toAdd,
          devices_to_remove: selectedDevices.toRemove,
          output_format: outputFormat,
          add_position: selectedDevices.position,
          after_device: selectedDevices.afterDevice,
          custom_device_order: selectedDevices.customDeviceOrder,
          insert_index: selectedDevices.insertIndex,
          device_brand: selectedDevices.deviceBrand,
          device_attributes: selectedDevices.deviceAttributes,
          auto_fill_alt_text: autoFillAltText
        };
        
        const result = await processCSV(request);
        setProcessResult(result);
      } else {
        // Batch processing
        const result = await processBatchCSV(
          batchId,
          selectedDevices.toAdd,
          selectedDevices.toRemove,
          outputFormat,
          true
        );
        setBatchResult(result);
      }
      
      setActiveStep(3);
    } catch (err: any) {
      setError(err.message || '処理中にエラーが発生しました');
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    setFileId('');
    setBatchId('');
    setBatchFiles([]);
    setDevices([]);
    setProductDevices({});
    setSelectedDevices({ toAdd: [], toRemove: [] });
    setProcessResult(null);
    setBatchResult(null);
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

        <Tabs 
          value={mode} 
          onChange={handleModeChange} 
          centered 
          sx={{ mb: 3 }}
        >
          <Tab label="シングルファイル処理" value="single" />
          <Tab label="バッチ処理" value="batch" />
        </Tabs>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {(mode === 'single' ? steps : batchSteps).map((label) => (
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
            <>
              {mode === 'single' ? (
                <FileUpload onUploadSuccess={handleFileUpload} />
              ) : (
                <BatchFileUpload onUploadSuccess={handleBatchUpload} />
              )}
            </>
          )}
          
          {activeStep === 1 && (
            <>
              {mode === 'single' ? (
                <DeviceManager 
                  devices={devices}
                  productDevices={productDevices}
                  autoFillAltText={autoFillAltText}
                  onAutoFillAltTextChange={setAutoFillAltText}
                  onNext={handleDeviceSelection}
                  onBack={() => setActiveStep(0)}
                />
              ) : (
                <BatchProcessor
                  batchId={batchId}
                  uploadedFiles={batchFiles}
                  allDevices={devices}
                  allProductDevices={productDevices}
                  onReset={handleReset}
                />
              )}
            </>
          )}
          
          {activeStep === 2 && mode === 'single' && (
            <ProcessOptions
              onProcess={handleProcess}
              onBack={() => setActiveStep(1)}
              selectedDevices={selectedDevices}
            />
          )}
          
          {activeStep === 3 && (
            <>
              {mode === 'single' && processResult && (
                <ResultDownload
                  result={processResult}
                  onReset={handleReset}
                />
              )}
              {mode === 'batch' && batchResult && (
                <Box>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    バッチ処理が完了しました
                  </Alert>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    処理済みファイル: {batchResult.successful_files}/{batchResult.total_files}
                  </Typography>
                  {batchResult.failed_files > 0 && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      {batchResult.failed_files}個のファイルで処理に失敗しました
                    </Alert>
                  )}
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                    <button onClick={handleReset}>新しい処理を開始</button>
                  </Box>
                </Box>
              )}
            </>
          )}
        </Box>
      </Paper>
    </Container>
  );
}

export default App;