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
  Alert
} from '@mui/material';
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
    insertIndex?: number
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
  
  // Debug log
  console.log('DeviceManager received productDevices:', productDevices);
  console.log('Number of products:', productDevices ? Object.keys(productDevices).length : 0);
  console.log('[DEBUG] devices prop:', devices);
  console.log('[DEBUG] devices length:', devices ? devices.length : 0);
  console.log('[DEBUG] devices type:', typeof devices);
  console.log('[DEBUG] Is devices an array?', Array.isArray(devices));
  
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
    console.log('[DEBUG] handleNext called with:');
    console.log('  devices:', devices);
    console.log('  devicesToAdd:', devicesToAdd);
    console.log('  devicesToRemove:', devicesToRemove);
    console.log('  addPosition:', addPosition);
    console.log('  afterDevice:', afterDevice);
    
    if (finalDeviceOrder) {
      // 完全カスタマイズモードの場合
      const existingSet = new Set(devices);
      const newDevicesInOrder = finalDeviceOrder.filter(d => !existingSet.has(d));
      const removedDevices = devices.filter(d => !finalDeviceOrder.includes(d));
      
      onNext(newDevicesInOrder, removedDevices, 'final_order', undefined, finalDeviceOrder, undefined);
    } else if (customDeviceOrder) {
      onNext(devicesToAdd, devicesToRemove, 'custom', undefined, customDeviceOrder, insertIndex);
    } else {
      onNext(devicesToAdd, devicesToRemove, addPosition, afterDevice);
    }
  };

  // 機種リストでグループ化する処理
  const groupProductsByDevices = () => {
    if (!productDevices) return {};
    
    const groups: { [key: string]: { devices: string[], products: string[] } } = {};
    
    Object.entries(productDevices).forEach(([productId, deviceList]) => {
      // 機種リストをソートして文字列化（比較用のキーを作成）
      const deviceKey = [...deviceList].sort().join('|');
      
      if (!groups[deviceKey]) {
        groups[deviceKey] = {
          devices: deviceList,
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
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              既存の機種一覧
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              削除する機種にチェックを入れてください
            </Typography>
            
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {/* 強制デバッグ表示 */}
              <Typography variant="body2" sx={{ 
                p: 1, 
                mb: 2, 
                backgroundColor: '#ffeb3b', 
                border: '2px solid #f57c00',
                borderRadius: 1
              }}>
                🐛 DEBUG: productDevices={productDevices ? 'EXISTS' : 'NULL'} | 
                keys={productDevices ? Object.keys(productDevices).length : 0} |
                devices={devices.length}
              </Typography>
              
              {/* 条件を緩和してテスト */}
              {productDevices && Object.keys(productDevices).length >= 1 ? (
                // 商品ごとの機種を別窓で表示する方式
                <Box>
                  <Typography variant="h6" sx={{ 
                    mb: 2,
                    p: 2,
                    backgroundColor: '#4caf50',
                    color: 'white',
                    textAlign: 'center',
                    borderRadius: 1
                  }}>
                    ✅ 複数商品が検出されました！
                    {hasMultipleGroups ? '機種リストが異なる商品グループがあります。' : '全商品が同じ機種リストを持っています。'}
                  </Typography>
                  
                  {Object.entries(deviceGroups).map(([deviceKey, group], groupIndex) => {
                    const isOnlyGroup = Object.keys(deviceGroups).length === 1;
                    const hasMultipleProducts = group.products.length > 1;
                    
                    return (
                      <Paper 
                        key={deviceKey} 
                        sx={{ 
                          p: 2, 
                          mb: 2,
                          border: isOnlyGroup ? '1px solid #e0e0e0' : '2px solid #2196f3',
                          backgroundColor: isOnlyGroup ? 'background.paper' : '#e3f2fd'
                        }}
                      >
                        <Box>
                          {/* グループヘッダー */}
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'bold' }}>
                              {isOnlyGroup ? '全商品共通の機種リスト' : `機種グループ ${groupIndex + 1}`}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {hasMultipleProducts 
                                ? `対象商品: ${group.products.join(', ')}` 
                                : `対象商品: ${group.products[0]}`}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              機種数: {group.devices.length}機種
                            </Typography>
                          </Box>
                          
                          {/* 機種一覧表示ボタン（グループに1つだけ） */}
                          <Button
                            variant="outlined"
                            fullWidth
                            startIcon={<OpenInNewIcon />}
                            onClick={() => setSelectedProduct({
                              productId: group.products.join(', '),
                              devices: group.devices
                            })}
                          >
                            この機種リストを確認 ({group.devices.length}機種)
                          </Button>
                        </Box>
                      </Paper>
                    );
                  })}
                  
                  {/* 全体の機種を統合表示 */}
                  <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
                    全機種統合リスト (削除選択用)
                  </Typography>
                </Box>
              ) : null}
              
              {/* 統合機種リスト または フォールバック */}
              <Box>
                {((productDevices && Object.keys(productDevices).length > 0) || !productDevices) && (
                // フォールバック: 全体の機種リスト
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
                )}
              </Box>
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
          <Paper sx={{ p: 2 }}>
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