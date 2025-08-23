import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Alert,
  Chip
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { ProcessResponse } from '../types';

interface ResultDownloadProps {
  result: ProcessResponse;
  onReset: () => void;
}

const ResultDownload: React.FC<ResultDownloadProps> = ({ result, onReset }) => {
  const handleDownload = (filename: string) => {
    window.open(`/api/download/${filename}`, '_blank');
  };

  const handleDownloadAll = () => {
    result.output_files.forEach(filename => {
      setTimeout(() => handleDownload(filename), 500);
    });
  };

  return (
    <Box>
      <Alert 
        severity="success" 
        icon={<CheckCircleIcon />}
        sx={{ mb: 3 }}
      >
        <Typography variant="h6">処理完了</Typography>
        <Typography variant="body2">
          CSVファイルの処理が正常に完了しました
        </Typography>
      </Alert>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          処理結果
        </Typography>
        
        <List>
          <ListItem>
            <ListItemText 
              primary="処理行数" 
              secondary={`${result.total_rows} 行`}
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="生成SKU数" 
              secondary={`${result.sku_count} SKU`}
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="出力ファイル数" 
              secondary={
                <Chip 
                  label={`${result.output_files.length} ファイル`} 
                  color="primary" 
                  size="small"
                />
              }
            />
          </ListItem>
        </List>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            ダウンロード
          </Typography>
          {result.output_files.length > 1 && (
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadAll}
              size="small"
            >
              すべてダウンロード
            </Button>
          )}
        </Box>
        
        <List>
          {result.output_files.map((filename, index) => (
            <ListItem key={filename}>
              <ListItemText 
                primary={filename}
                secondary={`ファイル ${index + 1} / ${result.output_files.length}`}
              />
              <ListItemSecondaryAction>
                <IconButton 
                  edge="end" 
                  onClick={() => handleDownload(filename)}
                  color="primary"
                >
                  <DownloadIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          ダウンロードしたCSVファイルは楽天RMSに直接アップロード可能です。
          文字コードはShift-JIS、改行コードはCRLFに設定されています。
        </Typography>
      </Alert>

      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="outlined"
          onClick={onReset}
          startIcon={<RestartAltIcon />}
          size="large"
        >
          新しいファイルを処理
        </Button>
      </Box>
    </Box>
  );
};

export default ResultDownload;