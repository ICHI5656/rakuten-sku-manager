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
  Chip,
  Alert,
  Grid,
  Divider,
  Tooltip
} from '@mui/material';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import DeleteIcon from '@mui/icons-material/Delete';
import RestoreIcon from '@mui/icons-material/Restore';
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';
import NewReleasesIcon from '@mui/icons-material/NewReleases';

interface DeviceListOrganizerProps {
  existingDevices: string[];
  newDevices: string[];
  onConfirm: (finalDeviceOrder: string[]) => void;
  onCancel: () => void;
}

interface DeviceItem {
  name: string;
  isNew: boolean;
  originalIndex: number;
}

const DeviceListOrganizer: React.FC<DeviceListOrganizerProps> = ({
  existingDevices,
  newDevices,
  onConfirm,
  onCancel
}) => {
  const [deviceList, setDeviceList] = useState<DeviceItem[]>([]);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [removedDevices, setRemovedDevices] = useState<string[]>([]);

  useEffect(() => {
    // 初期リストの作成：既存機種をそのままの順序で、新機種を末尾に追加
    const initialList: DeviceItem[] = [
      ...existingDevices.map((device, index) => ({
        name: device,
        isNew: false,
        originalIndex: index
      })),
      ...newDevices.map((device, index) => ({
        name: device,
        isNew: true,
        originalIndex: existingDevices.length + index
      }))
    ];
    setDeviceList(initialList);
  }, [existingDevices, newDevices]);

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null) return;
    
    if (draggedIndex !== index) {
      const newList = [...deviceList];
      const draggedItem = newList[draggedIndex];
      newList.splice(draggedIndex, 1);
      newList.splice(index, 0, draggedItem);
      setDeviceList(newList);
      setDraggedIndex(index);
    }
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const moveDevice = (index: number, direction: 'up' | 'down') => {
    const newList = [...deviceList];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (newIndex >= 0 && newIndex < deviceList.length) {
      [newList[index], newList[newIndex]] = [newList[newIndex], newList[index]];
      setDeviceList(newList);
    }
  };

  const toggleRemoveDevice = (deviceName: string) => {
    if (removedDevices.includes(deviceName)) {
      setRemovedDevices(prev => prev.filter(d => d !== deviceName));
    } else {
      setRemovedDevices(prev => [...prev, deviceName]);
    }
  };

  const resetOrder = () => {
    const initialList: DeviceItem[] = [
      ...existingDevices.map((device, index) => ({
        name: device,
        isNew: false,
        originalIndex: index
      })),
      ...newDevices.map((device, index) => ({
        name: device,
        isNew: true,
        originalIndex: existingDevices.length + index
      }))
    ];
    setDeviceList(initialList);
    setRemovedDevices([]);
  };

  const handleConfirm = () => {
    // 削除されていない機種のみを最終リストとして返す
    const finalOrder = deviceList
      .filter(device => !removedDevices.includes(device.name))
      .map(device => device.name);
    onConfirm(finalOrder);
  };

  // 統計情報の計算
  const stats = {
    total: deviceList.length,
    existing: deviceList.filter(d => !d.isNew).length,
    new: deviceList.filter(d => d.isNew).length,
    removed: removedDevices.length,
    final: deviceList.length - removedDevices.length
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        機種リストの完全カスタマイズ
      </Typography>
      
      <Alert severity="info" sx={{ mb: 2 }}>
        既存機種と新機種を自由に並び替えてください。各新機種を個別に好きな位置に配置できます。
        ドラッグ&ドロップまたは矢印ボタンで順番を変更できます。
      </Alert>

      <Grid container spacing={2}>
        {/* 統計情報 */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Chip label={`合計: ${stats.total}機種`} />
            <Chip label={`既存: ${stats.existing}機種`} color="default" />
            <Chip label={`新規: ${stats.new}機種`} color="success" />
            {stats.removed > 0 && (
              <Chip label={`削除予定: ${stats.removed}機種`} color="error" />
            )}
            <Chip label={`最終: ${stats.final}機種`} color="primary" variant="filled" />
          </Box>
        </Grid>

        {/* メインリスト */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ backgroundColor: '#f5f5f5', p: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1">
                機種リスト（ドラッグ&ドロップで並び替え）
              </Typography>
              <Button
                size="small"
                onClick={resetOrder}
                startIcon={<RestoreIcon />}
              >
                初期順序に戻す
              </Button>
            </Box>
            
            <List sx={{ maxHeight: 500, overflow: 'auto' }}>
              {deviceList.map((device, index) => {
                const isRemoved = removedDevices.includes(device.name);
                return (
                  <ListItem
                    key={`${device.name}-${index}`}
                    draggable={!isRemoved}
                    onDragStart={() => !isRemoved && handleDragStart(index)}
                    onDragOver={(e) => !isRemoved && handleDragOver(e, index)}
                    onDragEnd={handleDragEnd}
                    sx={{
                      cursor: isRemoved ? 'default' : 'move',
                      backgroundColor: isRemoved ? '#ffebee' : (draggedIndex === index ? '#e3f2fd' : 'white'),
                      opacity: isRemoved ? 0.5 : 1,
                      mb: 0.5,
                      borderRadius: 1,
                      border: device.isNew ? '2px solid #4caf50' : '1px solid #e0e0e0',
                      '&:hover': {
                        backgroundColor: isRemoved ? '#ffebee' : '#f5f5f5'
                      }
                    }}
                  >
                    <ListItemIcon>
                      {!isRemoved && <DragIndicatorIcon />}
                    </ListItemIcon>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                      <Typography variant="body2" sx={{ minWidth: 30 }}>
                        #{index + 1}
                      </Typography>
                      
                      {device.isNew && (
                        <Tooltip title="新機種">
                          <NewReleasesIcon color="success" fontSize="small" />
                        </Tooltip>
                      )}
                      
                      <ListItemText 
                        primary={device.name}
                        secondary={device.isNew ? '新機種' : '既存機種'}
                        sx={{
                          textDecoration: isRemoved ? 'line-through' : 'none'
                        }}
                      />
                    </Box>
                    
                    <Box>
                      {!isRemoved && (
                        <>
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
                            disabled={index === deviceList.length - 1}
                          >
                            <ArrowDownwardIcon fontSize="small" />
                          </IconButton>
                        </>
                      )}
                      <IconButton
                        size="small"
                        onClick={() => toggleRemoveDevice(device.name)}
                        color={isRemoved ? "default" : "error"}
                      >
                        {isRemoved ? <RestoreIcon fontSize="small" /> : <DeleteIcon fontSize="small" />}
                      </IconButton>
                    </Box>
                  </ListItem>
                );
              })}
            </List>
          </Paper>
        </Grid>

        {/* プレビューパネル */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, position: 'sticky', top: 20 }}>
            <Typography variant="subtitle1" gutterBottom>
              最終的な機種リスト
            </Typography>
            
            <Divider sx={{ my: 1 }} />
            
            <Typography variant="caption" color="text.secondary">
              バリエーション2選択肢定義の値:
            </Typography>
            <Box sx={{ 
              p: 1, 
              backgroundColor: '#f5f5f5', 
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              wordBreak: 'break-all',
              maxHeight: 150,
              overflow: 'auto',
              mb: 2
            }}>
              {deviceList
                .filter(device => !removedDevices.includes(device.name))
                .map(device => device.name)
                .join('|')}
            </Box>
            
            <Typography variant="caption" color="text.secondary">
              配置された新機種の位置:
            </Typography>
            <Box sx={{ mt: 1, mb: 2 }}>
              {newDevices.map(newDevice => {
                const position = deviceList
                  .filter(device => !removedDevices.includes(device.name))
                  .findIndex(device => device.name === newDevice);
                
                if (position === -1) {
                  return (
                    <Chip
                      key={newDevice}
                      label={`${newDevice}: 削除済み`}
                      size="small"
                      color="error"
                      sx={{ m: 0.5 }}
                    />
                  );
                }
                
                return (
                  <Chip
                    key={newDevice}
                    label={`${newDevice}: ${position + 1}番目`}
                    size="small"
                    color="success"
                    sx={{ m: 0.5 }}
                  />
                );
              })}
            </Box>
            
            <Typography variant="caption" color="text.secondary">
              並び順の変更例:
            </Typography>
            <Box sx={{ 
              p: 1, 
              backgroundColor: '#e8f5e9',
              borderRadius: 1,
              fontSize: '0.75rem',
              mb: 2
            }}>
              • test4を先頭に配置<br/>
              • test2を中間に配置<br/>
              • test3を末尾に配置<br/>
              など、自由に調整可能
            </Box>
          </Paper>
        </Grid>
      </Grid>

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
          disabled={stats.final === 0}
        >
          この順番で確定（{stats.final}機種）
        </Button>
      </Box>
    </Paper>
  );
};

export default DeviceListOrganizer;