import React, { useState, useMemo } from 'react'
import ReactDOM from 'react-dom/client'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import AppWithRouting from './AppWithRouting'
import ThemeSelector from './components/ThemeSelector'

function Main() {
  const [primaryColor, setPrimaryColor] = useState('#bf0000');
  const [secondaryColor, setSecondaryColor] = useState('#333333');

  const theme = useMemo(
    () => createTheme({
      palette: {
        primary: {
          main: primaryColor,
        },
        secondary: {
          main: secondaryColor,
        },
      },
      typography: {
        fontFamily: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ].join(','),
      },
    }),
    [primaryColor, secondaryColor]
  );

  const handleThemeChange = (primary: string, secondary: string) => {
    setPrimaryColor(primary);
    setSecondaryColor(secondary);
  };

  return (
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ThemeSelector onThemeChange={handleThemeChange} />
        <AppWithRouting />
      </ThemeProvider>
    </React.StrictMode>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(<Main />)