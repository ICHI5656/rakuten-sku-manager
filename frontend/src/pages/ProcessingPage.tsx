import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Button,
  Stack
} from '@mui/material';
import {
  Upload as UploadIcon,
  SettingsApplications as ProcessIcon,
  Download as DownloadIcon,
  BatchPrediction as BatchIcon,
  CloudUpload as CloudUploadIcon,
  Transform as TransformIcon,
  GetApp as GetAppIcon,
  Groups as GroupsIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index } = props;
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );
}

export default function ProcessingPage() {
  const [activeTab, setActiveTab] = useState(0);
  const navigate = useNavigate();

  const processCards = [
    {
      title: '単一ファイル処理',
      description: 'CSV単体のSKU処理',
      icon: <UploadIcon fontSize="large" />,
      color: '#1976d2',
      path: '/',
      features: ['SKU自動採番', 'デバイス管理', '即時処理']
    },
    {
      title: 'バッチ処理',
      description: '複数CSV一括処理',
      icon: <BatchIcon fontSize="large" />,
      color: '#9c27b0',
      path: '/batch',
      features: ['複数ファイル対応', '並列処理', 'ZIP出力']
    },
    {
      title: 'ファイルアップロード',
      description: 'ドラッグ&ドロップ対応',
      icon: <CloudUploadIcon fontSize="large" />,
      color: '#2e7d32',
      path: '/upload',
      features: ['ドラッグ&ドロップ', 'エンコード自動検出', 'プレビュー']
    },
    {
      title: '処理オプション',
      description: 'カスタム処理設定',
      icon: <ProcessIcon fontSize="large" />,
      color: '#ed6c02',
      path: '/process-options',
      features: ['デバイス配置', '出力形式選択', 'ブランド選択']
    }
  ];

  const quickActions = [
    {
      label: 'CSVテンプレートダウンロード',
      icon: <GetAppIcon />,
      action: () => window.open('/api/product-attributes/template-csv', '_blank')
    },
    {
      label: 'デバイスDB管理',
      icon: <TransformIcon />,
      action: () => navigate('/database')
    },
    {
      label: 'バッチ処理を開始',
      icon: <BatchIcon />,
      action: () => navigate('/batch')
    }
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        処理管理センター
      </Typography>

      <Paper sx={{ mb: 2 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="処理タイプ選択" />
          <Tab label="クイックアクション" />
          <Tab label="処理履歴" />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={2}>
          {processCards.map((card, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  }
                }}
              >
                <CardActionArea onClick={() => navigate(card.path)} sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box 
                        sx={{ 
                          p: 1.5, 
                          borderRadius: 2,
                          backgroundColor: `${card.color}15`,
                          color: card.color,
                          mr: 2
                        }}
                      >
                        {card.icon}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" component="div">
                          {card.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {card.description}
                        </Typography>
                      </Box>
                    </Box>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
                      {card.features.map((feature, idx) => (
                        <Chip
                          key={idx}
                          label={feature}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.75rem' }}
                        />
                      ))}
                    </Stack>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={2}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} sm={4} key={index}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={action.icon}
                onClick={action.action}
                sx={{ 
                  py: 2,
                  justifyContent: 'flex-start',
                  textTransform: 'none'
                }}
              >
                {action.label}
              </Button>
            </Grid>
          ))}
        </Grid>
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            処理統計
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    0
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    本日の処理
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    0
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    成功
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    0
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    処理中
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="error.main">
                    0
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    エラー
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
          処理履歴はまだありません
        </Typography>
      </TabPanel>
    </Box>
  );
}