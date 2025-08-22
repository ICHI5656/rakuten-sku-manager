import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  TextField,
  Button,
  Paper,
  Grid,
  Chip,
  IconButton,
  Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface DeviceManagerProps {
  devices: string[];
  onNext: (devicesToAdd: string[], devicesToRemove: string[]) => void;
  onBack: () => void;
}

const DeviceManager: React.FC<DeviceManagerProps> = ({ devices, onNext, onBack }) => {
  const [devicesToRemove, setDevicesToRemove] = useState<string[]>([]);
  const [devicesToAdd, setDevicesToAdd] = useState<string[]>([]);
  const [newDevice, setNewDevice] = useState('');

  const handleToggleRemove = (device: string) => {
    setDevicesToRemove(prev =>
      prev.includes(device)
        ? prev.filter(d => d !== device)
        : [...prev, device]
    );
  };

  const handleAddDevice = () => {
    if (newDevice.trim()) {
      // カンマ区切りで複数機種を処理
      const devices = newDevice.split(',').map(d => d.trim()).filter(d => d);
      const uniqueNewDevices = devices.filter(d => !devicesToAdd.includes(d));
      
      if (uniqueNewDevices.length > 0) {
        setDevicesToAdd(prev => [...prev, ...uniqueNewDevices]);
        setNewDevice('');
      }
    }
  };

  const handleRemoveNewDevice = (device: string) => {
    setDevicesToAdd(prev => prev.filter(d => d !== device));
  };

  const handleNext = () => {
    onNext(devicesToAdd, devicesToRemove);
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              既存の機種一覧
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              削除する機種にチェックを入れてください
            </Typography>
            
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {devices.map((device) => (
                <ListItem
                  key={device}
                  dense
                  button
                  onClick={() => handleToggleRemove(device)}
                  sx={{
                    backgroundColor: devicesToRemove.includes(device) 
                      ? 'error.light' 
                      : 'transparent',
                    '&:hover': {
                      backgroundColor: devicesToRemove.includes(device)
                        ? 'error.light'
                        : 'action.hover'
                    }
                  }}
                >
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={devicesToRemove.includes(device)}
                      tabIndex={-1}
                      disableRipple
                    />
                  </ListItemIcon>
                  <ListItemText 
                    primary={device}
                    primaryTypographyProps={{
                      style: {
                        textDecoration: devicesToRemove.includes(device) 
                          ? 'line-through' 
                          : 'none'
                      }
                    }}
                  />
                  {devicesToRemove.includes(device) && (
                    <DeleteIcon color="error" fontSize="small" />
                  )}
                </ListItem>
              ))}
            </List>
            
            {devicesToRemove.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Chip 
                  label={`${devicesToRemove.length} 機種を削除`} 
                  color="error" 
                  size="small"
                />
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              新機種追加
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              追加する機種名を入力してください（複数の場合はカンマ区切り）
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                size="small"
                value={newDevice}
                onChange={(e) => setNewDevice(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleAddDevice();
                  }
                }}
                placeholder="例: iPhone 15 Pro, Galaxy S24, Pixel 8"
                helperText="複数機種を追加する場合: test1, test2, test3"
              />
              <Button
                variant="contained"
                onClick={handleAddDevice}
                startIcon={<AddIcon />}
                disabled={!newDevice.trim()}
              >
                追加
              </Button>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom>
              追加予定の機種:
            </Typography>
            
            {devicesToAdd.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                まだ追加する機種がありません
              </Typography>
            ) : (
              <List>
                {devicesToAdd.map((device) => (
                  <ListItem
                    key={device}
                    secondaryAction={
                      <IconButton 
                        edge="end" 
                        onClick={() => handleRemoveNewDevice(device)}
                        size="small"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      <AddIcon color="success" />
                    </ListItemIcon>
                    <ListItemText primary={device} />
                  </ListItem>
                ))}
              </List>
            )}
            
            {devicesToAdd.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Chip 
                  label={`${devicesToAdd.length} 機種を追加`} 
                  color="success" 
                  size="small"
                />
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button
          variant="outlined"
          onClick={onBack}
          startIcon={<ArrowBackIcon />}
        >
          戻る
        </Button>
        <Button
          variant="contained"
          onClick={handleNext}
          endIcon={<ArrowForwardIcon />}
        >
          次へ
        </Button>
      </Box>
    </Box>
  );
};

export default DeviceManager;