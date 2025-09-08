import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Select,
  MenuItem,
  InputLabel,
  TextField,
  Switch,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Save as SaveIcon,
  RestartAlt as ResetIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Transform as TransformIcon
} from '@mui/icons-material';

export default function ProcessOptionsPage() {
  const [options, setOptions] = useState({
    processMode: 'auto',
    devicePosition: 'end',
    afterDevice: '',
    outputFormat: 'single',
    resetDevices: false,
    skipValidation: false,
    preserveParent: true,
    autoSplit: true,
    splitSize: 60000,
    encoding: 'shift_jis',
    deviceBrand: ''
  });

  const handleChange = (field: string, value: any) => {
    setOptions(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const presets = [
    {
      name: '標準処理',
      icon: <CheckIcon />,
      description: 'デフォルト設定で処理',
      settings: {
        processMode: 'auto',
        devicePosition: 'end',
        outputFormat: 'single'
      }
    },
    {
      name: '高速処理',
      icon: <SpeedIcon />,
      description: '検証スキップで高速化',
      settings: {
        processMode: 'same_devices',
        skipValidation: true,
        outputFormat: 'single'
      }
    },
    {
      name: '大容量対応',
      icon: <StorageIcon />,
      description: '自動分割で大量データ処理',
      settings: {
        autoSplit: true,
        splitSize: 60000,
        outputFormat: 'split_60k'
      }
    },
    {
      name: 'カスタマイズ',
      icon: <TransformIcon />,
      description: '詳細設定を個別に調整',
      settings: null
    }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        処理オプション設定
      </Typography>

      {/* プリセット選択 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          プリセット選択
        </Typography>
        <Grid container spacing={2}>
          {presets.map((preset, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': {
                    boxShadow: 3,
                    transform: 'translateY(-2px)'
                  }
                }}
                onClick={() => {
                  if (preset.settings) {
                    setOptions(prev => ({
                      ...prev,
                      ...preset.settings
                    }));
                  }
                }}
              >
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ color: 'primary.main', mb: 1 }}>
                    {preset.icon}
                  </Box>
                  <Typography variant="subtitle1" gutterBottom>
                    {preset.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {preset.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {/* 処理モード設定 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              処理モード
            </Typography>
            <FormControl component="fieldset" sx={{ width: '100%' }}>
              <RadioGroup
                value={options.processMode}
                onChange={(e) => handleChange('processMode', e.target.value)}
              >
                <FormControlLabel
                  value="auto"
                  control={<Radio />}
                  label={
                    <Box>
                      <Typography>自動検出</Typography>
                      <Typography variant="caption" color="text.secondary">
                        ファイル内容から最適な処理方法を自動選択
                      </Typography>
                    </Box>
                  }
                />
                <FormControlLabel
                  value="same_devices"
                  control={<Radio />}
                  label={
                    <Box>
                      <Typography>同一デバイス処理</Typography>
                      <Typography variant="caption" color="text.secondary">
                        すべてのファイルで同じデバイスを使用
                      </Typography>
                    </Box>
                  }
                />
                <FormControlLabel
                  value="different_devices"
                  control={<Radio />}
                  label={
                    <Box>
                      <Typography>個別デバイス処理</Typography>
                      <Typography variant="caption" color="text.secondary">
                        ファイルごとに異なるデバイスを処理
                      </Typography>
                    </Box>
                  }
                />
              </RadioGroup>
            </FormControl>
          </Paper>
        </Grid>

        {/* デバイス配置設定 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              デバイス配置
            </Typography>
            <Stack spacing={2}>
              <FormControl fullWidth size="small">
                <InputLabel>配置位置</InputLabel>
                <Select
                  value={options.devicePosition}
                  label="配置位置"
                  onChange={(e) => handleChange('devicePosition', e.target.value)}
                >
                  <MenuItem value="start">先頭に追加</MenuItem>
                  <MenuItem value="end">末尾に追加</MenuItem>
                  <MenuItem value="after">特定デバイスの後</MenuItem>
                  <MenuItem value="custom">カスタム配置</MenuItem>
                </Select>
              </FormControl>

              {options.devicePosition === 'after' && (
                <TextField
                  fullWidth
                  size="small"
                  label="基準デバイス"
                  placeholder="例: iPhone 16 Pro Max"
                  value={options.afterDevice}
                  onChange={(e) => handleChange('afterDevice', e.target.value)}
                />
              )}

              <FormControl fullWidth size="small">
                <InputLabel>ブランド選択</InputLabel>
                <Select
                  value={options.deviceBrand}
                  label="ブランド選択"
                  onChange={(e) => handleChange('deviceBrand', e.target.value)}
                >
                  <MenuItem value="">すべて</MenuItem>
                  <MenuItem value="iPhone">iPhone</MenuItem>
                  <MenuItem value="Xperia">Xperia</MenuItem>
                  <MenuItem value="AQUOS">AQUOS</MenuItem>
                  <MenuItem value="Galaxy">Galaxy</MenuItem>
                  <MenuItem value="Pixel">Google Pixel</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={options.resetDevices}
                    onChange={(e) => handleChange('resetDevices', e.target.checked)}
                  />
                }
                label="既存デバイスをリセット"
              />
            </Stack>
          </Paper>
        </Grid>

        {/* 出力設定 */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              出力設定
            </Typography>
            <Stack spacing={2}>
              <FormControl fullWidth size="small">
                <InputLabel>出力形式</InputLabel>
                <Select
                  value={options.outputFormat}
                  label="出力形式"
                  onChange={(e) => handleChange('outputFormat', e.target.value)}
                >
                  <MenuItem value="single">単一ファイル</MenuItem>
                  <MenuItem value="per_product">商品ごと</MenuItem>
                  <MenuItem value="split_60k">60,000行で分割</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth size="small">
                <InputLabel>文字エンコード</InputLabel>
                <Select
                  value={options.encoding}
                  label="文字エンコード"
                  onChange={(e) => handleChange('encoding', e.target.value)}
                >
                  <MenuItem value="shift_jis">Shift-JIS (楽天推奨)</MenuItem>
                  <MenuItem value="utf8">UTF-8</MenuItem>
                  <MenuItem value="utf8_bom">UTF-8 with BOM</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={options.autoSplit}
                    onChange={(e) => handleChange('autoSplit', e.target.checked)}
                  />
                }
                label="大容量ファイル自動分割"
              />

              {options.autoSplit && (
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="分割サイズ (行数)"
                  value={options.splitSize}
                  onChange={(e) => handleChange('splitSize', parseInt(e.target.value))}
                />
              )}
            </Stack>
          </Paper>
        </Grid>

        {/* 詳細オプション */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              詳細オプション
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <Switch
                    checked={options.skipValidation}
                    onChange={(e) => handleChange('skipValidation', e.target.checked)}
                  />
                </ListItemIcon>
                <ListItemText
                  primary="検証スキップ"
                  secondary="ファイル検証を省略して高速化"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Switch
                    checked={options.preserveParent}
                    onChange={(e) => handleChange('preserveParent', e.target.checked)}
                  />
                </ListItemIcon>
                <ListItemText
                  primary="親商品関係を維持"
                  secondary="親商品とSKUの関係を保持"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* 現在の設定サマリー */}
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          現在の設定
        </Typography>
        <Grid container spacing={1}>
          <Grid item>
            <Chip label={`処理モード: ${options.processMode}`} size="small" />
          </Grid>
          <Grid item>
            <Chip label={`デバイス配置: ${options.devicePosition}`} size="small" />
          </Grid>
          <Grid item>
            <Chip label={`出力形式: ${options.outputFormat}`} size="small" />
          </Grid>
          <Grid item>
            <Chip label={`エンコード: ${options.encoding}`} size="small" />
          </Grid>
          {options.autoSplit && (
            <Grid item>
              <Chip label={`自動分割: ${options.splitSize}行`} size="small" color="primary" />
            </Grid>
          )}
          {options.skipValidation && (
            <Grid item>
              <Chip label="検証スキップ" size="small" color="warning" />
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* アクションボタン */}
      <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          size="large"
        >
          設定を保存
        </Button>
        <Button
          variant="outlined"
          startIcon={<ResetIcon />}
          onClick={() => setOptions({
            processMode: 'auto',
            devicePosition: 'end',
            afterDevice: '',
            outputFormat: 'single',
            resetDevices: false,
            skipValidation: false,
            preserveParent: true,
            autoSplit: true,
            splitSize: 60000,
            encoding: 'shift_jis',
            deviceBrand: ''
          })}
        >
          デフォルトに戻す
        </Button>
      </Stack>

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          これらの設定は次回の処理から適用されます。既に処理中のファイルには影響しません。
        </Typography>
      </Alert>
    </Box>
  );
}