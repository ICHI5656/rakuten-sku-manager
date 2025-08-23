import React, { useState } from 'react';
import {
  Box,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  Paper,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';

interface ProcessOptionsProps {
  onProcess: (outputFormat: string) => Promise<void>;
  onBack: () => void;
  selectedDevices: {
    toAdd: string[];
    toRemove: string[];
  };
}

const ProcessOptions: React.FC<ProcessOptionsProps> = ({ 
  onProcess, 
  onBack, 
  selectedDevices 
}) => {
  const [outputFormat, setOutputFormat] = useState('single');
  const [processing, setProcessing] = useState(false);

  const handleProcess = async () => {
    setProcessing(true);
    try {
      await onProcess(outputFormat);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          処理内容の確認
        </Typography>
        
        <List>
          {selectedDevices.toAdd.length > 0 && (
            <ListItem>
              <ListItemText
                primary="追加する機種"
                secondary={
                  <Box sx={{ mt: 1 }}>
                    {selectedDevices.toAdd.map(device => (
                      <Chip 
                        key={device} 
                        label={device} 
                        color="success" 
                        size="small" 
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                }
              />
            </ListItem>
          )}
          
          {selectedDevices.toRemove.length > 0 && (
            <ListItem>
              <ListItemText
                primary="削除する機種"
                secondary={
                  <Box sx={{ mt: 1 }}>
                    {selectedDevices.toRemove.map(device => (
                      <Chip 
                        key={device} 
                        label={device} 
                        color="error" 
                        size="small" 
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                }
              />
            </ListItem>
          )}
          
          {selectedDevices.toAdd.length === 0 && selectedDevices.toRemove.length === 0 && (
            <ListItem>
              <ListItemText
                primary="変更なし"
                secondary="機種の追加・削除は行いません"
              />
            </ListItem>
          )}
        </List>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          出力形式の選択
        </Typography>
        
        <RadioGroup
          value={outputFormat}
          onChange={(e) => setOutputFormat(e.target.value)}
        >
          <FormControlLabel 
            value="single" 
            control={<Radio />} 
            label={
              <Box>
                <Typography variant="body1">1ファイルに統合</Typography>
                <Typography variant="caption" color="text.secondary">
                  すべての商品を1つのCSVファイルに出力
                </Typography>
              </Box>
            }
          />
          
          <FormControlLabel 
            value="per_product" 
            control={<Radio />} 
            label={
              <Box>
                <Typography variant="body1">商品ごとに分割</Typography>
                <Typography variant="caption" color="text.secondary">
                  各商品を個別のCSVファイルに出力
                </Typography>
              </Box>
            }
          />
          
          <FormControlLabel 
            value="split_60k" 
            control={<Radio />} 
            label={
              <Box>
                <Typography variant="body1">6万行ごとに自動分割</Typography>
                <Typography variant="caption" color="text.secondary">
                  大量データを楽天RMS制限に合わせて分割
                </Typography>
              </Box>
            }
          />
        </RadioGroup>
      </Paper>

      <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
        <Typography variant="body2">
          処理内容:
        </Typography>
        <List dense>
          <ListItem>
            <ListItemText primary="• SKU番号の自動採番 (sku_a000001形式)" />
          </ListItem>
          <ListItem>
            <ListItemText primary="• バリエーション展開（全組み合わせ生成）" />
          </ListItem>
          <ListItem>
            <ListItemText primary="• 楽天RMS制約チェック（最大40選択肢、400SKU）" />
          </ListItem>
          <ListItem>
            <ListItemText primary="• Shift-JISエンコーディング、CRLF改行" />
          </ListItem>
        </List>
      </Alert>

      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          onClick={onBack}
          startIcon={<ArrowBackIcon />}
          disabled={processing}
        >
          戻る
        </Button>
        
        <Button
          variant="contained"
          onClick={handleProcess}
          startIcon={processing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          disabled={processing}
        >
          {processing ? '処理中...' : '処理開始'}
        </Button>
      </Box>
    </Box>
  );
};

export default ProcessOptions;