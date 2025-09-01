import React, { useState, Fragment } from 'react';
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
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
  AlertTitle
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import EditIcon from '@mui/icons-material/Edit';
import SwapVertIcon from '@mui/icons-material/SwapVert';
import DeviceOrderEditor from './DeviceOrderEditor';
import DeviceListOrganizer from './DeviceListOrganizer';

interface DeviceManagerProps {
  devices: string[];
  productDevices?: Record<string, string[]>;
  onNext: (
    devicesToAdd: string[], 
    devicesToRemove: string[], 
    position?: 'start' | 'end' | 'after' | 'custom' | 'final_order', 
    afterDevice?: string,
    customDeviceOrder?: string[],
    insertIndex?: number,
    deviceBrand?: string,
    deviceAttributes?: Array<{device: string, attribute_value?: string, size_category?: string}>
  ) => void;
  onBack: () => void;
}

const DeviceManager: React.FC<DeviceManagerProps> = ({ devices, productDevices, onNext, onBack }) => {
  const [devicesToRemove, setDevicesToRemove] = useState<string[]>([]);
  const [devicesToAdd, setDevicesToAdd] = useState<string[]>([]);
  const [newDevice, setNewDevice] = useState('');
  const [addPosition, setAddPosition] = useState<'start' | 'end' | 'after'>('start');
  const [afterDevice, setAfterDevice] = useState<string>('');
  const [insertIndex, setInsertIndex] = useState<number>(0);
  const [showOrderPreview, setShowOrderPreview] = useState(false);
  const [showOrderEditor, setShowOrderEditor] = useState(false);
  const [customDeviceOrder, setCustomDeviceOrder] = useState<string[] | null>(null);
  const [showListOrganizer, setShowListOrganizer] = useState(false);
  const [finalDeviceOrder, setFinalDeviceOrder] = useState<string[] | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<{productId: string, devices: string[]} | null>(null);
  
  // Database integration states
  const [showDatabaseDialog, setShowDatabaseDialog] = useState(false);
  const [pendingDevice, setPendingDevice] = useState('');
  const [deviceBrand, setDeviceBrand] = useState('');
  const [deviceAttributeValue, setDeviceAttributeValue] = useState('');
  const [deviceSizeCategory, setDeviceSizeCategory] = useState('');
  const [isSavingToDatabase, setIsSavingToDatabase] = useState(false);
  const [deviceAttributesMap, setDeviceAttributesMap] = useState<Map<string, {attribute_value: string, size_category: string}>>(new Map());
  
  // Debug log
  console.log('DeviceManager received devices:', JSON.stringify(devices, null, 2));
  console.log('DeviceManager received productDevices:', productDevices);
  
  // 順序確認用のデバッグログ
  if (devices && devices.length > 0) {
    console.log('Device order in DeviceManager:');
    devices.forEach((device, index) => {
      console.log(`  ${index + 1}. ${device}`);
    });
    // 配列の最初と最後を確認
    console.log('First device:', devices[0]);
    console.log('Last device:', devices[devices.length - 1]);
  }
  // console.log('Number of products:', productDevices ? Object.keys(productDevices).length : 0);
  // console.log('[DEBUG] devices prop:', devices);
  // console.log('[DEBUG] devices length:', devices ? devices.length : 0);
  // console.log('[DEBUG] devices type:', typeof devices);
  // console.log('[DEBUG] Is devices an array?', Array.isArray(devices));
  
  // 商品間の機種の違いを検出
  const deviceDifferences: Record<string, string[]> = {};
  if (productDevices && Object.keys(productDevices).length > 1) {
    const productIds = Object.keys(productDevices);
    const allDeviceSets = productIds.map(id => new Set(productDevices[id]));
    
    productIds.forEach((productId, index) => {
      const thisSet = allDeviceSets[index];
      const otherSets = allDeviceSets.filter((_, i) => i !== index);
      
      // この商品だけにある機種
      const uniqueDevices = Array.from(thisSet).filter(device => 
        !otherSets.some(otherSet => otherSet.has(device))
      );
      
      if (uniqueDevices.length > 0) {
        deviceDifferences[productId] = uniqueDevices;
      }
    });
    
    console.log('Device differences:', deviceDifferences);
  }

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
      
      // 単一デバイスの場合、データベース登録ダイアログを表示
      if (devices.length === 1) {
        const deviceName = devices[0];
        setPendingDevice(deviceName);
        
        // デバイス名からブランドを推測
        const lowerName = deviceName.toLowerCase();
        let suggestedBrand = 'その他';
        if (lowerName.includes('iphone')) suggestedBrand = 'iPhone';
        else if (lowerName.includes('xperia') || lowerName.includes('so-')) suggestedBrand = 'Xperia';
        else if (lowerName.includes('aquos') || lowerName.includes('sh-')) suggestedBrand = 'AQUOS';
        else if (lowerName.includes('galaxy')) suggestedBrand = 'Galaxy';
        else if (lowerName.includes('arrows')) suggestedBrand = 'ARROWS';
        else if (lowerName.includes('huawei') || lowerName.includes('p30') || lowerName.includes('p40')) suggestedBrand = 'Huawei';
        else if (lowerName.includes('pixel')) suggestedBrand = 'Pixel';
        else if (lowerName.includes('oppo')) suggestedBrand = 'OPPO';
        else if (lowerName.includes('xiaomi') || lowerName.includes('mi ') || lowerName.includes('redmi')) suggestedBrand = 'Xiaomi';
        
        setDeviceBrand(suggestedBrand);
        setDeviceAttributeValue(deviceName); // デフォルトで機種名と同じ
        setShowDatabaseDialog(true);
      } else {
        // 複数デバイスの場合は直接追加
        const uniqueNewDevices = devices.filter(d => !devicesToAdd.includes(d));
        if (uniqueNewDevices.length > 0) {
          setDevicesToAdd(prev => [...prev, ...uniqueNewDevices]);
          setNewDevice('');
        }
      }
    }
  };
  
  const handleDatabaseSave = async () => {
    console.log('handleDatabaseSave called with:', {
      pendingDevice,
      deviceBrand,
      deviceAttributeValue,
      deviceSizeCategory
    });
    
    if (!pendingDevice || !deviceBrand || !deviceAttributeValue) {
      alert('デバイス名、ブランド、属性値は必須項目です');
      return;
    }
    
    setIsSavingToDatabase(true);
    try {
      // データベースに保存
      const requestBody = {
        brand: deviceBrand,
        device_name: pendingDevice,
        attribute_value: deviceAttributeValue,
        size_category: deviceSizeCategory || '',  // 空の場合は空文字列
        usage_count: 0
      };
      console.log('Sending request to API:', requestBody);
      
      const response = await fetch('/api/product-attributes/devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const error = await response.json();
        console.error('API error response:', error);
        throw new Error(error.detail || 'データベース保存に失敗しました');
      }
      
      const savedDevice = await response.json();
      console.log('Device saved successfully:', savedDevice);
      
      // 成功したらデバイスを追加
      if (!devicesToAdd.includes(pendingDevice)) {
        setDevicesToAdd([...devicesToAdd, pendingDevice]);
        // デバイスの属性情報を保存
        const newMap = new Map(deviceAttributesMap);
        newMap.set(pendingDevice, {
          attribute_value: deviceAttributeValue,
          size_category: deviceSizeCategory
        });
        setDeviceAttributesMap(newMap);
      }
      
      // ダイアログを閉じてリセット
      setShowDatabaseDialog(false);
      setPendingDevice('');
      setDeviceBrand('');
      setDeviceAttributeValue('');
      setDeviceSizeCategory('');
      setNewDevice('');
    } catch (error: any) {
      console.error('Error in handleDatabaseSave:', error);
      alert(`エラー: ${error.message}`);
    } finally {
      setIsSavingToDatabase(false);
    }
  };
  
  const handleSkipDatabase = () => {
    // データベース保存をスキップして直接追加
    if (pendingDevice && !devicesToAdd.includes(pendingDevice)) {
      setDevicesToAdd([...devicesToAdd, pendingDevice]);
    }
    setShowDatabaseDialog(false);
    setPendingDevice('');
    setDeviceBrand('');
    setDeviceAttributeValue('');
    setDeviceSizeCategory('');
    setNewDevice('');
  };

  const handleRemoveNewDevice = (device: string) => {
    setDevicesToAdd(prev => prev.filter(d => d !== device));
  };

  const handleNext = () => {
    console.log('[DEBUG] handleNext called with:');
    console.log('  devices:', devices);
    console.log('  devicesToAdd:', devicesToAdd);
    console.log('  devicesToRemove:', devicesToRemove);
    console.log('  addPosition:', addPosition);
    console.log('  afterDevice:', afterDevice);
    
    // deviceAttributesMapから配列形式に変換
    const deviceAttributesArray = devicesToAdd.map(device => {
      const attrs = deviceAttributesMap.get(device);
      return {
        device: device,
        attribute_value: attrs?.attribute_value || device,  // フォールバック
        size_category: attrs?.size_category || ''
      };
    });
    
    console.log('[DEBUG] deviceAttributesArray:', deviceAttributesArray);
    
    if (finalDeviceOrder) {
      // 完全カスタマイズモードの場合
      const existingSet = new Set(devices);
      const newDevicesInOrder = finalDeviceOrder.filter(d => !existingSet.has(d));
      const removedDevices = devices.filter(d => !finalDeviceOrder.includes(d));
      
      onNext(newDevicesInOrder, removedDevices, 'final_order', undefined, finalDeviceOrder, undefined, deviceBrand, deviceAttributesArray);
    } else if (customDeviceOrder) {
      onNext(devicesToAdd, devicesToRemove, 'custom', undefined, customDeviceOrder, insertIndex, deviceBrand, deviceAttributesArray);
    } else {
      onNext(devicesToAdd, devicesToRemove, addPosition, afterDevice, undefined, undefined, deviceBrand, deviceAttributesArray);
    }
  };

  // 機種リストでグループ化する処理
  const groupProductsByDevices = () => {
    if (!productDevices) return {};
    
    const groups: { [key: string]: { devices: string[], products: string[] } } = {};
    
    Object.entries(productDevices).forEach(([productId, deviceList]) => {
      // 機種リストを文字列化（順序を保持したまま比較用のキーを作成）
      const deviceKey = deviceList.join('|');
      
      if (!groups[deviceKey]) {
        // グローバルな機種リスト（devices）の順序に従ってソート
        const sortedDevices = devices ? 
          [...deviceList].sort((a, b) => {
            const indexA = devices.indexOf(a);
            const indexB = devices.indexOf(b);
            // デバイスが見つからない場合は元の順序を保持
            if (indexA === -1) return 1;
            if (indexB === -1) return -1;
            return indexA - indexB;
          }) : deviceList;
        
        groups[deviceKey] = {
          devices: sortedDevices,
          products: []
        };
      }
      groups[deviceKey].products.push(productId);
    });
    
    return groups;
  };

  const deviceGroups = groupProductsByDevices();
  const hasMultipleGroups = Object.keys(deviceGroups).length > 1;

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              既存の機種一覧
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              削除する機種にチェックを入れてください
            </Typography>
            
            <Box sx={{ 
              flex: 1,
              maxHeight: devices && devices.length > 20 ? '800px' : 'none',
              overflow: devices && devices.length > 20 ? 'auto' : 'visible',
              minHeight: '300px'
            }}>
              {/* 商品ごとに異なる機種がある場合のみ別窓表示 */}
              {productDevices && Object.keys(productDevices).length > 1 && hasMultipleGroups ? (
                // 商品ごとの機種を別窓で表示する方式
                <Box>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <AlertTitle>商品ごとに異なる機種セットが検出されました</AlertTitle>
                    商品グループごとに機種リストが異なります。下記から確認してください。
                  </Alert>
                  
                  {Object.entries(deviceGroups).map(([deviceKey, group], groupIndex) => {
                    const hasMultipleProducts = group.products.length > 1;
                    
                    return (
                      <Paper key={groupIndex} elevation={2} sx={{ p: 2, mb: 2 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          {hasMultipleProducts 
                            ? `📦 ${group.products.length}個の商品が同じ機種セット`
                            : `📦 商品: ${group.products[0]}`
                          }
                        </Typography>
                        
                        {hasMultipleProducts && (
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            商品: {group.products.slice(0, 3).join(', ')}
                            {group.products.length > 3 && ` 他${group.products.length - 3}個`}
                          </Typography>
                        )}
                        
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip label={`${group.devices.length}機種`} size="small" color="primary" />
                          <Button 
                            size="small" 
                            variant="outlined"
                            onClick={() => setSelectedProduct({
                              productId: group.products.join(', '),
                              devices: group.devices
                            })}
                          >
                            この機種リストを確認
                          </Button>
                        </Box>
                      </Paper>
                    );
                  })}
                  
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    全機種統合リスト (削除選択用)
                  </Typography>
                  
                  <List>
                    {devices.map((device, index) => (
                      <ListItem
                        key={`${device}-${index}`}
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
                          primary={`${index + 1}. ${device}`}
                          secondary={
                            deviceDifferences[Object.keys(deviceDifferences).find(pid => 
                              deviceDifferences[pid].includes(device)
                            ) || '']
                              ? '⚠️ 一部の商品のみ'
                              : null
                          }
                        />
                        {devicesToRemove.includes(device) && (
                          <DeleteIcon color="error" fontSize="small" />
                        )}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              ) : devices && devices.length > 0 ? (
                // 通常のシンプルな機種リスト表示（すべて同じ機種セットの場合）
                <List>
                  {devices.map((device, index) => (
                    <ListItem
                      key={`${device}-${index}`}
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
                        secondary={devicesToRemove.includes(device) ? '削除予定' : ''}
                      />
                      {devicesToRemove.includes(device) && (
                        <DeleteIcon color="error" fontSize="small" />
                      )}
                    </ListItem>
                  ))}
                </List>
              ) : null}
            </Box>
            
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
          <Paper sx={{ p: 2, minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              新機種追加
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              追加する機種名を入力してください（複数の場合はカンマ区切り）
            </Typography>
            
            {/* カスタマイズ状態の表示 */}
            {finalDeviceOrder && (
              <Alert severity="success" sx={{ mb: 2 }}>
                完全カスタマイズモードが有効です。機種の配置が完全にカスタマイズされます。
                <br />
                <Typography variant="caption">
                  最終的な機種数: {finalDeviceOrder.length}機種
                </Typography>
              </Alert>
            )}
            
            {/* 位置選択 - より視覚的に */}
            <Box sx={{ mt: 2, mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                  追加位置の選択
                </Typography>
                <Button
                  size="small"
                  variant="contained"
                  color="success"
                  onClick={() => setShowListOrganizer(true)}
                  startIcon={<SwapVertIcon />}
                  sx={{ mr: 1 }}
                  disabled={devicesToAdd.length === 0}
                >
                  完全カスタマイズ
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setShowOrderEditor(true)}
                  startIcon={<EditIcon />}
                  sx={{ mr: 1 }}
                >
                  挿入位置指定
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setShowOrderPreview(!showOrderPreview)}
                  endIcon={<ArrowDropDownIcon />}
                >
                  プレビュー
                </Button>
              </Box>
              
              {/* プレビュー表示 */}
              {showOrderPreview && (
                <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    現在の機種リスト順序（パイプ区切りで保存されます）
                  </Typography>
                  <Box sx={{ 
                    display: 'flex', 
                    flexWrap: 'wrap', 
                    gap: 0.5,
                    mt: 1,
                    p: 1,
                    backgroundColor: 'white',
                    borderRadius: 1,
                    maxHeight: 200,
                    overflow: 'auto'
                  }}>
                    {devices.map((device, index) => {
                      const isInsertPoint = 
                        (addPosition === 'start' && index === 0) ||
                        (addPosition === 'end' && index === devices.length - 1) ||
                        (addPosition === 'after' && devices[index - 1] === afterDevice);
                      
                      return (
                        <Fragment key={device}>
                          {isInsertPoint && index === 0 && addPosition === 'start' && (
                            <Box sx={{ 
                              display: 'flex', 
                              alignItems: 'center',
                              px: 1,
                              backgroundColor: '#4caf50',
                              color: 'white',
                              borderRadius: 1
                            }}>
                              <ArrowDropDownIcon sx={{ transform: 'rotate(-90deg)' }} />
                              新機種をここに挿入
                            </Box>
                          )}
                          
                          <Chip
                            label={device}
                            size="small"
                            variant={device === afterDevice ? "filled" : "outlined"}
                            color={device === afterDevice ? "primary" : "default"}
                            sx={{ m: 0.5 }}
                          />
                          
                          {isInsertPoint && addPosition === 'after' && (
                            <Box sx={{ 
                              display: 'flex', 
                              alignItems: 'center',
                              px: 1,
                              backgroundColor: '#4caf50',
                              color: 'white',
                              borderRadius: 1
                            }}>
                              <ArrowDropDownIcon sx={{ transform: 'rotate(-90deg)' }} />
                              新機種
                            </Box>
                          )}
                        </Fragment>
                      );
                    })}
                    {addPosition === 'end' && (
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        px: 1,
                        backgroundColor: '#4caf50',
                        color: 'white',
                        borderRadius: 1,
                        ml: 0.5
                      }}>
                        <ArrowDropDownIcon sx={{ transform: 'rotate(-90deg)' }} />
                        新機種をここに挿入
                      </Box>
                    )}
                  </Box>
                </Paper>
              )}
              
              <RadioGroup
                value={addPosition}
                onChange={(e) => {
                  const newPosition = e.target.value as 'start' | 'end' | 'after';
                  setAddPosition(newPosition);
                  if (newPosition !== 'after') {
                    setAfterDevice('');
                  }
                }}
              >
                <FormControlLabel 
                  value="start" 
                  control={<Radio size="small" />} 
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <span>リストの先頭に追加</span>
                      <Chip label="最初" size="small" sx={{ ml: 1 }} />
                    </Box>
                  }
                />
                <FormControlLabel 
                  value="end" 
                  control={<Radio size="small" />} 
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <span>リストの末尾に追加</span>
                      <Chip label="最後" size="small" sx={{ ml: 1 }} />
                    </Box>
                  }
                />
                <FormControlLabel 
                  value="after" 
                  control={<Radio size="small" />} 
                  label="特定機種の後に追加" 
                />
              </RadioGroup>
              
              {addPosition === 'after' && (
                <Box sx={{ mt: 1, pl: 3 }}>
                  {/* デバッグ情報 */}
                  {devices.length === 0 && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      既存の機種が見つかりません。CSVファイルに機種データが含まれているか確認してください。
                    </Alert>
                  )}
                  <FormControl fullWidth size="small">
                    <InputLabel>どの機種の後に追加</InputLabel>
                    <Select
                      value={afterDevice}
                      onChange={(e) => setAfterDevice(e.target.value)}
                      label="どの機種の後に追加"
                      disabled={devices.length === 0}
                    >
                      {devices.length > 0 ? (
                        devices.map((device, index) => (
                          <MenuItem key={device} value={device}>
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                              <span style={{ marginRight: 8 }}>#{index + 1}</span>
                              <span>{device}</span>
                            </Box>
                          </MenuItem>
                        ))
                      ) : (
                        <MenuItem value="" disabled>
                          機種が見つかりません
                        </MenuItem>
                      )}
                    </Select>
                  </FormControl>
                  {afterDevice && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      「{afterDevice}」の直後に新機種が挿入されます
                    </Typography>
                  )}
                </Box>
              )}
            </Box>
            
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

      {/* データベース登録ダイアログ */}
      <Dialog
        open={showDatabaseDialog}
        onClose={() => setShowDatabaseDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          新機種をデータベースに登録
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            機種「{pendingDevice}」をProduct Attributes 8データベースに登録します。
          </Alert>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="機種名"
              value={pendingDevice}
              disabled
              fullWidth
            />
            <FormControl fullWidth required>
              <InputLabel>ブランド</InputLabel>
              <Select
                value={deviceBrand}
                onChange={(e) => setDeviceBrand(e.target.value)}
                label="ブランド"
              >
                <MenuItem value="iPhone">iPhone</MenuItem>
                <MenuItem value="Xperia">Xperia</MenuItem>
                <MenuItem value="AQUOS">AQUOS</MenuItem>
                <MenuItem value="Galaxy">Galaxy</MenuItem>
                <MenuItem value="ARROWS">ARROWS</MenuItem>
                <MenuItem value="HUAWEI">HUAWEI</MenuItem>
                <MenuItem value="Pixel">Pixel</MenuItem>
                <MenuItem value="OPPO">OPPO</MenuItem>
                <MenuItem value="Xiaomi">Xiaomi</MenuItem>
                <MenuItem value="その他">その他</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="属性値 (Product Attribute 8)"
              value={deviceAttributeValue}
              onChange={(e) => setDeviceAttributeValue(e.target.value)}
              fullWidth
              required
              helperText="楽天RMSで表示される属性値"
            />
            <Autocomplete
              freeSolo
              options={['Sサイズ', 'Mサイズ', 'Lサイズ', 'XLサイズ', 'フリーサイズ', 'その他']}
              value={deviceSizeCategory}
              onChange={(_, newValue) => setDeviceSizeCategory(newValue || '')}
              onInputChange={(_, newInputValue) => setDeviceSizeCategory(newInputValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="サイズカテゴリ"
                  required
                  helperText="例: Sサイズ, Mサイズ, Lサイズ"
                />
              )}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSkipDatabase} color="inherit">
            スキップ
          </Button>
          <Button onClick={() => setShowDatabaseDialog(false)}>
            キャンセル
          </Button>
          <Button 
            onClick={handleDatabaseSave} 
            variant="contained" 
            disabled={isSavingToDatabase || !deviceBrand || !deviceAttributeValue}
          >
            データベースに保存して追加
          </Button>
        </DialogActions>
      </Dialog>

      {/* 完全カスタマイズモーダル */}
      <Dialog
        open={showListOrganizer}
        onClose={() => setShowListOrganizer(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
          <DeviceListOrganizer
            existingDevices={devices}
            newDevices={devicesToAdd}
            onConfirm={(finalOrder) => {
              setFinalDeviceOrder(finalOrder);
              setShowListOrganizer(false);
            }}
            onCancel={() => setShowListOrganizer(false)}
          />
        </DialogContent>
      </Dialog>

      {/* 順序エディタモーダル */}
      <Dialog
        open={showOrderEditor}
        onClose={() => setShowOrderEditor(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent>
          <DeviceOrderEditor
            devices={customDeviceOrder || devices}
            newDevices={devicesToAdd}
            onOrderChange={(orderedDevices, position) => {
              setCustomDeviceOrder(orderedDevices);
              setInsertIndex(position);
              setAddPosition('after');
              setShowOrderEditor(false);
            }}
            onCancel={() => setShowOrderEditor(false)}
          />
        </DialogContent>
      </Dialog>

      {/* 商品別機種表示モーダル */}
      <Dialog 
        open={selectedProduct !== null} 
        onClose={() => setSelectedProduct(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <OpenInNewIcon />
            <Typography variant="h6">
              {selectedProduct?.productId.includes(',') 
                ? '共通機種リスト' 
                : `${selectedProduct?.productId} の機種一覧`}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedProduct && (
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedProduct.productId.includes(',') 
                  ? `対象商品: ${selectedProduct.productId}` 
                  : `この商品に含まれる全機種`} ({selectedProduct.devices.length}機種)
              </Typography>
              
              <List>
                {selectedProduct.devices.map((device, index) => {
                  // グループ化された商品の場合はisUniqueを無効化
                  const isGrouped = selectedProduct.productId.includes(',');
                  const isUnique = !isGrouped && deviceDifferences[selectedProduct.productId]?.includes(device);
                  return (
                    <ListItem 
                      key={device}
                      sx={{
                        backgroundColor: isUnique ? 'warning.light' : 'transparent',
                        borderRadius: 1,
                        mb: 0.5
                      }}
                    >
                      <ListItemIcon>
                        <Typography variant="body2" color="text.secondary">
                          {index + 1}.
                        </Typography>
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1">
                              {device}
                            </Typography>
                            {isUnique && (
                              <Chip 
                                label="この商品のみ" 
                                size="small" 
                                color="warning"
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  );
                })}
              </List>
              
              {!selectedProduct.productId.includes(',') && deviceDifferences[selectedProduct.productId]?.length > 0 && (
                <Box sx={{ mt: 2, p: 2, backgroundColor: 'warning.light', borderRadius: 1 }}>
                  <Typography variant="subtitle2" color="warning.dark">
                    ⚠️ この商品固有の機種
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {deviceDifferences[selectedProduct.productId].join(', ')}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedProduct(null)}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DeviceManager;