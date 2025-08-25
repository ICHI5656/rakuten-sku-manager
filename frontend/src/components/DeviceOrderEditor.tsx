import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Button,
  Divider,
  Chip,
  Alert
} from '@mui/material';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';

interface DeviceOrderEditorProps {
  devices: string[];
  newDevices: string[];
  onOrderChange: (orderedDevices: string[], insertPosition: number) => void;
  onCancel: () => void;
}

const DeviceOrderEditor: React.FC<DeviceOrderEditorProps> = ({
  devices,
  newDevices,
  onOrderChange,
  onCancel
}) => {
  const [orderedDevices, setOrderedDevices] = useState<string[]>(devices);
  const [insertPosition, setInsertPosition] = useState<number>(0);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  useEffect(() => {
    setOrderedDevices(devices);
  }, [devices]);

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null) return;
    
    if (draggedIndex !== index) {
      const newOrder = [...orderedDevices];
      const draggedItem = newOrder[draggedIndex];
      newOrder.splice(draggedIndex, 1);
      newOrder.splice(index, 0, draggedItem);
      setOrderedDevices(newOrder);
      setDraggedIndex(index);
    }
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const moveDevice = (index: number, direction: 'up' | 'down') => {
    const newOrder = [...orderedDevices];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (newIndex >= 0 && newIndex < orderedDevices.length) {
      [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];
      setOrderedDevices(newOrder);
    }
  };

  const handleInsertHere = (index: number) => {
    setInsertPosition(index);
  };

  const handleConfirm = () => {
    onOrderChange(orderedDevices, insertPosition);
  };

  // 最終的な並び順を生成（新機種を挿入位置に追加）
  const getFinalOrder = () => {
    const result = [...orderedDevices];
    result.splice(insertPosition, 0, ...newDevices);
    return result;
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        機種リストの並び順を調整
      </Typography>
      
      <Alert severity="info" sx={{ mb: 2 }}>
        ドラッグ&ドロップまたは矢印ボタンで既存機種の順番を変更し、
        新機種を挿入したい位置の「ここに挿入」ボタンをクリックしてください。
      </Alert>

      <Box sx={{ display: 'flex', gap: 2 }}>
        {/* 既存機種リスト */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            既存機種の並び順
          </Typography>
          <List sx={{ 
            backgroundColor: '#f5f5f5', 
            borderRadius: 1,
            maxHeight: 400,
            overflow: 'auto'
          }}>
            {orderedDevices.map((device, index) => (
              <React.Fragment key={device}>
                {/* 挿入位置ボタン */}
                <ListItem sx={{ py: 0.5 }}>
                  <Button
                    fullWidth
                    variant={insertPosition === index ? "contained" : "outlined"}
                    color={insertPosition === index ? "success" : "inherit"}
                    size="small"
                    startIcon={<AddCircleIcon />}
                    onClick={() => handleInsertHere(index)}
                    sx={{ height: 24 }}
                  >
                    {insertPosition === index ? '新機種をここに挿入' : 'ここに挿入'}
                  </Button>
                </ListItem>
                
                {/* 機種アイテム */}
                <ListItem
                  draggable
                  onDragStart={() => handleDragStart(index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragEnd={handleDragEnd}
                  sx={{
                    cursor: 'move',
                    backgroundColor: draggedIndex === index ? '#e3f2fd' : 'white',
                    mb: 0.5,
                    mx: 1,
                    borderRadius: 1,
                    '&:hover': {
                      backgroundColor: '#f5f5f5'
                    }
                  }}
                >
                  <ListItemIcon>
                    <DragIndicatorIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={device}
                    secondary={`#${index + 1}`}
                  />
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => moveDevice(index, 'up')}
                      disabled={index === 0}
                    >
                      <ArrowUpwardIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => moveDevice(index, 'down')}
                      disabled={index === orderedDevices.length - 1}
                    >
                      <ArrowDownwardIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </ListItem>
              </React.Fragment>
            ))}
            
            {/* 最後の挿入位置 */}
            <ListItem sx={{ py: 0.5 }}>
              <Button
                fullWidth
                variant={insertPosition === orderedDevices.length ? "contained" : "outlined"}
                color={insertPosition === orderedDevices.length ? "success" : "inherit"}
                size="small"
                startIcon={<AddCircleIcon />}
                onClick={() => handleInsertHere(orderedDevices.length)}
                sx={{ height: 24 }}
              >
                {insertPosition === orderedDevices.length ? '新機種を末尾に挿入' : '末尾に挿入'}
              </Button>
            </ListItem>
          </List>
        </Box>

        {/* プレビュー */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            最終的な並び順（プレビュー）
          </Typography>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: '#f8f8f8',
            maxHeight: 400,
            overflow: 'auto'
          }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              バリエーション2選択肢定義の値:
            </Typography>
            <Box sx={{ 
              p: 1, 
              backgroundColor: 'white', 
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              wordBreak: 'break-all',
              mb: 2
            }}>
              {getFinalOrder().join('|')}
            </Box>
            
            <Divider sx={{ my: 1 }} />
            
            <Typography variant="caption" color="text.secondary" gutterBottom>
              機種リスト:
            </Typography>
            {getFinalOrder().map((device, index) => {
              const isNew = newDevices.includes(device);
              return (
                <Chip
                  key={`${device}-${index}`}
                  label={`${index + 1}. ${device}`}
                  size="small"
                  color={isNew ? "success" : "default"}
                  sx={{ 
                    m: 0.5,
                    fontWeight: isNew ? 'bold' : 'normal'
                  }}
                />
              );
            })}
          </Paper>
          
          {/* 新機種の表示 */}
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              追加される新機種
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {newDevices.map(device => (
                <Chip
                  key={device}
                  label={device}
                  color="success"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        </Box>
      </Box>

      {/* アクションボタン */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 3 }}>
        <Button
          variant="outlined"
          onClick={onCancel}
          startIcon={<CancelIcon />}
        >
          キャンセル
        </Button>
        <Button
          variant="contained"
          onClick={handleConfirm}
          startIcon={<CheckIcon />}
        >
          この順番で確定
        </Button>
      </Box>
    </Paper>
  );
};

export default DeviceOrderEditor;