/**
 * Material UI Theme Configuration
 * 
 * Defines the color palette, typography, and component styles
 * for the Merma Optimization dashboard.
 */

import { createTheme, ThemeOptions } from '@mui/material/styles';

/**
 * Custom color palette for the waste optimization dashboard
 */
const palette = {
  primary: {
    main: '#1976d2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#dc004e',
    light: '#f73378',
    dark: '#9a0036',
    contrastText: '#ffffff',
  },
  error: {
    main: '#d32f2f',
    light: '#ef5350',
    dark: '#c62828',
  },
  warning: {
    main: '#ed6c02',
    light: '#ff9800',
    dark: '#e65100',
  },
  info: {
    main: '#0288d1',
    light: '#03a9f4',
    dark: '#01579b',
  },
  success: {
    main: '#2e7d32',
    light: '#4caf50',
    dark: '#1b5e20',
  },
  background: {
    default: '#f5f5f5',
    paper: '#ffffff',
  },
  text: {
    primary: '#212121',
    secondary: '#757575',
  },
};

/**
 * Alert severity color mapping for visual differentiation
 */
export const severityColors: Record<string, string> = {
  info: palette.info.main,
  warning: palette.warning.main,
  critical: palette.error.main,
};

/**
 * Chart color palette for data visualization
 */
export const chartColors = [
  '#1976d2',
  '#388e3c',
  '#f57c00',
  '#7b1fa2',
  '#d32f2f',
  '#0097a7',
  '#c2185b',
  '#455a64',
];

/**
 * Default theme configuration options
 */
const defaultThemeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    ...palette,
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)',
    '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)',
    '0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)',
    '0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)',
    '0px 3px 5px -1px rgba(0,0,0,0.2),0px 6px 10px 0px rgba(0,0,0,0.14),0px 1px 18px 0px rgba(0,0,0,0.12)',
    '0px 3px 5px -1px rgba(0,0,0,0.2),0px 8px 10px 0px rgba(0,0,0,0.14),0px 1px 20px 0px rgba(0,0,0,0.12)',
    '0px 4px 5px -2px rgba(0,0,0,0.2),0px 7px 10px 1px rgba(0,0,0,0.14),0px 2px 16px 1px rgba(0,0,0,0.12)',
    '0px 5px 5px -3px rgba(0,0,0,0.2),0px 8px 14px 1px rgba(0,0,0,0.14),0px 3px 20px 1px rgba(0,0,0,0.12)',
    '0px 5px 5px -3px rgba(0,0,0,0.2),0px 8px 18px 1px rgba(0,0,0,0.14),0px 3px 20px 2px rgba(0,0,0,0.12)',
    '0px 6px 6px -3px rgba(0,0,0,0.2),0px 10px 20px 1px rgba(0,0,0,0.14),0px 3px 25px 2px rgba(0,0,0,0.12)',
    '0px 6px 6px -3px rgba(0,0,0,0.2),0px 10px 22px 1px rgba(0,0,0,0.14),0px 3px 26px 2px rgba(0,0,0,0.12)',
    '0px 7px 7px -4px rgba(0,0,0,0.2),0px 12px 26px 1px rgba(0,0,0,0.14),0px 4px 30px 3px rgba(0,0,0,0.12)',
    '0px 7px 7px -4px rgba(0,0,0,0.2),0px 12px 28px 1px rgba(0,0,0,0.14),0px 4px 32px 3px rgba(0,0,0,0.12)',
    '0px 7px 8px -4px rgba(0,0,0,0.2),0px 13px 31px 1px rgba(0,0,0,0.14),0px 5px 35px 3px rgba(0,0,0,0.12)',
    '0px 8px 8px -4px rgba(0,0,0,0.2),0px 14px 34px 1px rgba(0,0,0,0.14),0px 5px 38px 3px rgba(0,0,0,0.12)',
    '0px 8px 9px -5px rgba(0,0,0,0.2),0px 15px 38px 2px rgba(0,0,0,0.14),0px 6px 42px 4px rgba(0,0,0,0.12)',
    '0px 8px 10px -5px rgba(0,0,0,0.2),0px 16px 40px 2px rgba(0,0,0,0.14),0px 6px 44px 4px rgba(0,0,0,0.12)',
    '0px 9px 11px -5px rgba(0,0,0,0.2),0px 17px 43px 2px rgba(0,0,0,0.14),0px 7px 47px 4px rgba(0,0,0,0.12)',
    '0px 9px 12px -6px rgba(0,0,0,0.2),0px 18px 46px 2px rgba(0,0,0,0.14),0px 7px 50px 4px rgba(0,0,0,0.12)',
    '0px 10px 13px -6px rgba(0,0,0,0.2),0px 19px 49px 2px rgba(0,0,0,0.14),0px 8px 53px 5px rgba(0,0,0,0.12)',
    '0px 10px 13px -6px rgba(0,0,0,0.2),0px 20px 51px 2px rgba(0,0,0,0.14),0px 8px 55px 5px rgba(0,0,0,0.12)',
    '0px 10px 14px -6px rgba(0,0,0,0.2),0px 21px 54px 2px rgba(0,0,0,0.14),0px 8px 58px 5px rgba(0,0,0,0.12)',
    '0px 11px 15px -6px rgba(0,0,0,0.2),0px 22px 57px 2px rgba(0,0,0,0.14),0px 9px 62px 6px rgba(0,0,0,0.12)',
    '0px 11px 16px -6px rgba(0,0,0,0.2),0px 23px 60px 2px rgba(0,0,0,0.14),0px 9px 65px 6px rgba(0,0,0,0.12)',
    '0px 11px 17px -6px rgba(0,0,0,0.2),0px 24px 62px 2px rgba(0,0,0,0.14),0px 10px 68px 6px rgba(0,0,0,0.12)',
  ] as any,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          fontWeight: 500,
        },
        contained: {
          boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)',
          '&:hover': {
            boxShadow: '0px 4px 5px -1px rgba(0,0,0,0.2),0px 7px 10px 1px rgba(0,0,0,0.14),0px 2px 16px 1px rgba(0,0,0,0.12)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
        elevation1: {
          boxShadow: '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 600,
          backgroundColor: '#f5f5f5',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: 'none',
          boxShadow: '2px 0 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12)',
        },
      },
    },
  },
};

/**
 * Light theme instance for the application
 */
export const theme = createTheme(defaultThemeOptions);

/**
 * Dark theme configuration (for future implementation)
 */
export const darkThemeOptions: ThemeOptions = {
  ...defaultThemeOptions,
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
      light: '#e3f2fd',
      dark: '#42a5f5',
      contrastText: '#000000',
    },
    secondary: {
      main: '#f48fb1',
      light: '#f8bbd0',
      dark: '#f06292',
      contrastText: '#000000',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
};

export default theme;
