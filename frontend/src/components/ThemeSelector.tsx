import React, { useState } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  Typography,
  Grid,
  Paper
} from '@mui/material';
import PaletteIcon from '@mui/icons-material/Palette';
import CheckIcon from '@mui/icons-material/Check';

interface ThemeSelectorProps {
  onThemeChange: (primaryColor: string, secondaryColor: string) => void;
}

interface ThemeOption {
  name: string;
  primary: string;
  secondary: string;
}

const themeOptions: ThemeOption[] = [
  { name: '楽天レッド（デフォルト）', primary: '#bf0000', secondary: '#333333' },
  { name: 'オーシャンブルー', primary: '#0066cc', secondary: '#004499' },
  { name: 'ナチュラルグリーン', primary: '#2e7d32', secondary: '#1b5e20' },
  { name: 'サンセットオレンジ', primary: '#ff6f00', secondary: '#e65100' },
  { name: 'ロイヤルパープル', primary: '#6a1b9a', secondary: '#4a148c' },
  { name: 'モダングレー', primary: '#424242', secondary: '#212121' },
  { name: 'ピンクベリー', primary: '#e91e63', secondary: '#c2185b' },
  { name: 'ターコイズ', primary: '#00acc1', secondary: '#00838f' },
  { name: 'アースブラウン', primary: '#6d4c41', secondary: '#4e342e' },
  { name: 'ゴールデンイエロー', primary: '#ffc107', secondary: '#f57c00' }
];

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ onThemeChange }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedTheme, setSelectedTheme] = useState(themeOptions[0]);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleThemeSelect = (theme: ThemeOption) => {
    setSelectedTheme(theme);
    onThemeChange(theme.primary, theme.secondary);
    handleClose();
    
    // ローカルストレージに保存
    localStorage.setItem('selectedTheme', JSON.stringify(theme));
  };

  // コンポーネントマウント時にローカルストレージから読み込み
  React.useEffect(() => {
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
      const theme = JSON.parse(savedTheme);
      setSelectedTheme(theme);
      onThemeChange(theme.primary, theme.secondary);
    }
  }, [onThemeChange]);

  return (
    <>
      <Tooltip title="テーマカラーを変更">
        <IconButton
          onClick={handleClick}
          sx={{
            position: 'fixed',
            top: 16,
            right: 16,
            zIndex: 1000,
            backgroundColor: selectedTheme.primary,
            color: 'white',
            '&:hover': {
              backgroundColor: selectedTheme.secondary,
            }
          }}
        >
          <PaletteIcon />
        </IconButton>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 500
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            テーマカラーを選択
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            アプリケーション全体のカラーテーマを変更できます
          </Typography>
        </Box>
        
        <Grid container spacing={1} sx={{ p: 2, pt: 0 }}>
          {themeOptions.map((theme) => (
            <Grid item xs={12} key={theme.name}>
              <MenuItem
                onClick={() => handleThemeSelect(theme)}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                  position: 'relative'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Paper
                    sx={{
                      width: 40,
                      height: 40,
                      mr: 2,
                      background: `linear-gradient(135deg, ${theme.primary} 50%, ${theme.secondary} 50%)`,
                      border: '2px solid',
                      borderColor: selectedTheme.name === theme.name ? theme.primary : 'transparent'
                    }}
                  />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body1">
                      {theme.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Primary: {theme.primary}, Secondary: {theme.secondary}
                    </Typography>
                  </Box>
                  {selectedTheme.name === theme.name && (
                    <CheckIcon color="primary" sx={{ ml: 1 }} />
                  )}
                </Box>
              </MenuItem>
            </Grid>
          ))}
        </Grid>
        
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            選択したテーマは自動的に保存されます
          </Typography>
        </Box>
      </Menu>
    </>
  );
};

export default ThemeSelector;