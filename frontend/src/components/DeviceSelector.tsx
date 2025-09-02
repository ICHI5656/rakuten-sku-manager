import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  TextField,
  Box,
  Typography,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

interface DeviceInfo {
  id: number;
  brand: string;
  device_name: string;
  attribute_value: string;
  size_category?: string;
  usage_count: number;
}

interface DeviceSelectorProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (selectedDevices: string[], deviceInfo?: DeviceInfo[]) => void;
  existingDevices: string[];
}

const DeviceSelector: React.FC<DeviceSelectorProps> = ({
  open,
  onClose,
  onConfirm,
  existingDevices = []
}) => {
  const [allDevices, setAllDevices] = useState<DeviceInfo[]>([]);
  const [displayedDevices, setDisplayedDevices] = useState<DeviceInfo[]>([]);
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ダイアログが開いたときにデータを取得
  useEffect(() => {
    if (open) {
      console.log('DeviceSelector opened with existingDevices:', existingDevices);
      console.log('Number of existing devices:', existingDevices.length);
      const huaweiExisting = existingDevices.filter(d => 
        d.toLowerCase().includes('huawei') || d.toUpperCase().includes('HUAWEI')
      );
      if (huaweiExisting.length > 0) {
        console.log('HUAWEI devices in existingDevices:', huaweiExisting);
      }
      loadDevices();
    } else {
      // ダイアログが閉じたときにリセット
      setSelectedDevices(new Set());
      setSearchTerm('');
    }
  }, [open]);

  // 検索条件が変わったときにフィルタリング
  useEffect(() => {
    if (!allDevices || allDevices.length === 0) {
      setDisplayedDevices([]);
      return;
    }

    let filtered = [...allDevices];
    
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      console.log(`Searching for: "${searchTerm}" (lowercase: "${search}")`);
      
      filtered = filtered.filter(d => {
        const deviceNameMatch = d.device_name && d.device_name.toLowerCase().includes(search);
        const brandMatch = d.brand && d.brand.toLowerCase().includes(search);
        const attrMatch = d.attribute_value && d.attribute_value.toLowerCase().includes(search);
        
        // HUAWEIの特別なデバッグ
        if (search.includes('huawei') && d.brand && d.brand.toUpperCase() === 'HUAWEI') {
          console.log(`HUAWEI device check: ${d.device_name}, brand="${d.brand}", brandMatch=${brandMatch}`);
        }
        
        return deviceNameMatch || brandMatch || attrMatch;
      });
      
      console.log(`Filtered results: ${filtered.length} devices`);
      if (search.includes('huawei')) {
        const huaweiCount = filtered.filter(d => d.brand && d.brand.toUpperCase() === 'HUAWEI').length;
        console.log(`HUAWEI devices in filtered results: ${huaweiCount}`);
      }
    }
    
    setDisplayedDevices(filtered);
  }, [allDevices, searchTerm]);

  const loadDevices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // APIからデータを取得
      const response = await fetch('/api/product-attributes/devices');
      
      if (!response.ok) {
        throw new Error(`エラー: ${response.status}`);
      }
      
      const data = await response.json();
      
      // データが配列であることを確認
      if (Array.isArray(data)) {
        console.log(`${data.length}件の機種を取得しました`);
        
        // HUAWEIデバイスの確認
        const huaweiDevices = data.filter(d => d.brand && d.brand.toUpperCase().includes('HUAWEI'));
        console.log(`HUAWEI devices found: ${huaweiDevices.length}`);
        if (huaweiDevices.length > 0) {
          console.log('Sample HUAWEI devices:', huaweiDevices.slice(0, 3).map(d => ({
            name: d.device_name,
            brand: d.brand
          })));
        }
        
        setAllDevices(data);
        setDisplayedDevices(data);
      } else {
        throw new Error('不正なデータ形式');
      }
    } catch (err) {
      console.error('機種取得エラー:', err);
      setError('機種データの取得に失敗しました');
      setAllDevices([]);
      setDisplayedDevices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (deviceName: string) => {
    const newSet = new Set(selectedDevices);
    if (newSet.has(deviceName)) {
      newSet.delete(deviceName);
    } else {
      newSet.add(deviceName);
    }
    setSelectedDevices(newSet);
  };

  const handleConfirm = () => {
    const selected = Array.from(selectedDevices);
    console.log('選択された機種:', selected);
    
    // 選択されたデバイスの詳細情報を取得
    const selectedDeviceInfo = displayedDevices.filter(d => 
      selectedDevices.has(d.device_name)
    );
    console.log('選択されたデバイス情報:', selectedDeviceInfo);
    
    onConfirm(selected, selectedDeviceInfo);
    onClose();
  };

  const isDeviceExisting = (deviceName: string): boolean => {
    const exists = existingDevices.includes(deviceName);
    if (deviceName.toLowerCase().includes('huawei') || deviceName.toUpperCase().includes('HUAWEI')) {
      console.log(`Checking if "${deviceName}" is existing: ${exists}`, 'existingDevices:', existingDevices);
    }
    return exists;
  };

  const getSelectableCount = (): number => {
    return displayedDevices.filter(d => !isDeviceExisting(d.device_name)).length;
  };

  const handleSelectAll = () => {
    const selectableDevices = displayedDevices
      .filter(d => !isDeviceExisting(d.device_name))
      .map(d => d.device_name);
    
    if (selectedDevices.size === selectableDevices.length) {
      // 全選択解除
      setSelectedDevices(new Set());
    } else {
      // 全選択
      setSelectedDevices(new Set(selectableDevices));
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            データベースから機種を選択
          </Typography>
          {selectedDevices.size > 0 && (
            <Chip
              label={`${selectedDevices.size}個選択中`}
              color="primary"
              size="small"
            />
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        {/* 検索ボックス */}
        <Box mb={2}>
          <TextField
            fullWidth
            variant="outlined"
            size="small"
            placeholder="機種名、ブランド名で検索..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2" color="text.secondary">
              {loading ? '読み込み中...' : 
               error ? 'エラーが発生しました' :
               `${displayedDevices.length}件の機種`}
            </Typography>
            {!loading && !error && displayedDevices.length > 0 && (
              <Button size="small" onClick={handleSelectAll}>
                {selectedDevices.size === getSelectableCount() && getSelectableCount() > 0
                  ? 'すべて解除' 
                  : 'すべて選択'}
              </Button>
            )}
          </Box>
        </Box>

        {/* エラー表示 */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
            <Button size="small" onClick={loadDevices} sx={{ ml: 2 }}>
              再試行
            </Button>
          </Alert>
        )}

        {/* コンテンツ */}
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ maxHeight: '400px', overflow: 'auto', border: '1px solid #e0e0e0', borderRadius: 1 }}>
            <List dense>
              {displayedDevices.length > 0 ? (
                displayedDevices.map((device) => {
                  const isSelected = selectedDevices.has(device.device_name);
                  const isExisting = isDeviceExisting(device.device_name);
                  
                  return (
                    <ListItem
                      key={`${device.id}-${device.device_name}`}
                      button
                      onClick={() => !isExisting && handleToggle(device.device_name)}
                      disabled={isExisting}
                      sx={{
                        borderBottom: '1px solid #f0f0f0',
                        opacity: isExisting ? 0.5 : 1,
                      }}
                    >
                      <ListItemIcon>
                        <Checkbox
                          edge="start"
                          checked={isSelected}
                          disabled={isExisting}
                          tabIndex={-1}
                          disableRipple
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="body2" component="span">
                              {device.device_name}
                            </Typography>
                            {isExisting && (
                              <Typography variant="caption" color="error" sx={{ ml: 1 }}>
                                (追加済み)
                              </Typography>
                            )}
                          </Box>
                        }
                        secondary={
                          <Typography variant="caption" color="text.secondary">
                            {device.brand} | {device.attribute_value}
                            {device.usage_count > 0 && ` | 使用回数: ${device.usage_count}`}
                          </Typography>
                        }
                      />
                    </ListItem>
                  );
                })
              ) : (
                <ListItem>
                  <ListItemText
                    primary={
                      <Typography variant="body2" color="text.secondary" align="center">
                        機種が見つかりません
                      </Typography>
                    }
                  />
                </ListItem>
              )}
            </List>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          キャンセル
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          color="primary"
          disabled={selectedDevices.size === 0}
          startIcon={<AddIcon />}
        >
          選択した機種を追加 ({selectedDevices.size})
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeviceSelector;