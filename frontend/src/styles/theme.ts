import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4f6cff',
      light: '#818cf8',
      dark: '#1e3a5f',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#059669',
      light: '#34d399',
      dark: '#065f46',
      contrastText: '#ffffff',
    },
    error:   { main: '#dc2626', light: '#fca5a5', dark: '#991b1b' },
    warning: { main: '#d97706', light: '#fcd34d', dark: '#92400e' },
    info:    { main: '#0284c7', light: '#7dd3fc', dark: '#075985' },
    success: { main: '#059669', light: '#6ee7b7', dark: '#065f46' },
    background: { default: '#f1f5f9', paper: '#ffffff' },
    text: { primary: '#0f172a', secondary: '#475569', disabled: '#94a3b8' },
    divider: '#e2e8f0',
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Helvetica', sans-serif",
    button: { textTransform: 'none', fontWeight: 600 },
    h4:     { fontWeight: 700 },
    h5:     { fontWeight: 700 },
    h6:     { fontWeight: 600 },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 10, fontWeight: 600 },
        contained: {
          background: 'linear-gradient(135deg, #1e3a5f 0%, #4f6cff 100%)',
          boxShadow: '0 4px 20px rgba(79,108,255,.30)',
          '&:hover': { boxShadow: '0 6px 24px rgba(79,108,255,.45)', filter: 'brightness(1.08)' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          border: '1px solid #e2e8f0',
          boxShadow: '0 2px 6px rgba(15,23,42,.08)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { borderRadius: 14 },
        elevation2: { boxShadow: '0 4px 16px rgba(15,23,42,.10)' },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#4f6cff',
              borderWidth: '2px',
            },
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 600,
          backgroundColor: '#f8fafc',
          color: '#475569',
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        },
      },
    },
    MuiChip: {
      styleOverrides: { root: { borderRadius: 9999, fontWeight: 600, fontSize: '0.72rem' } },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: { borderRadius: 9999, height: 6 },
        bar: { borderRadius: 9999 },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 10 },
      },
    },
  },
});

export default theme;
