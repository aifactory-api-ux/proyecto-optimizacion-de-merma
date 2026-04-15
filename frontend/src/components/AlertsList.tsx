import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider,
  Alert as MuiAlert,
  AlertTitle,
} from '@mui/material';
import {
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { Alert } from '../types';
import { formatDateTime } from '../utils/format';

interface AlertsListProps {
  alerts: Alert[];
  maxItems?: number;
  showTimestamp?: boolean;
}

function getSeverityIcon(severity: Alert['severity']) {
  switch (severity) {
    case 'critical':
      return <ErrorIcon sx={{ color: 'error.main' }} />;
    case 'warning':
      return <WarningIcon sx={{ color: 'warning.main' }} />;
    case 'info':
    default:
      return <InfoIcon sx={{ color: 'info.main' }} />;
  }
}

function getSeverityColor(severity: Alert['severity']): 'error' | 'warning' | 'info' {
  switch (severity) {
    case 'critical':
      return 'error';
    case 'warning':
      return 'warning';
    case 'info':
    default:
      return 'info';
  }
}

function getSeverityLabel(severity: Alert['severity']): string {
  switch (severity) {
    case 'critical':
      return 'Crítico';
    case 'warning':
      return 'Advertencia';
    case 'info':
    default:
      return 'Información';
  }
}

function AlertsList({ alerts, maxItems = 10, showTimestamp = true }: AlertsListProps) {
  const displayAlerts = alerts.slice(0, maxItems);
  const hasAlerts = alerts.length > 0;
  const totalCount = alerts.length;
  const hiddenCount = totalCount - maxItems;

  if (!hasAlerts) {
    return (
      <Card
        sx={{
          width: '100%',
          bgcolor: 'background.paper',
          borderRadius: 2,
        }}
      >
        <CardContent>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 4,
            }}
          >
            <InfoIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No hay alertas activas
            </Typography>
            <Typography variant="body2" color="text.secondary">
              El sistema no ha detectado ninguna alerta en este momento.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        width: '100%',
        bgcolor: 'background.paper',
        borderRadius: 2,
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 2,
          }}
        >
          <Typography variant="h6" component="h2" gutterBottom sx={{ mb: 0 }}>
            Alertas
          </Typography>
          <Chip
            label={`${totalCount} ${totalCount === 1 ? 'alerta' : 'alertas'}`}
            color={totalCount > 5 ? 'error' : totalCount > 2 ? 'warning' : 'default'}
            size="small"
          />
        </Box>

        <Divider sx={{ mb: 2 }} />

        <List disablePadding>
          {displayAlerts.map((alert, index) => (
            <React.Fragment key={alert.id}>
              <ListItem
                alignItems="flex-start"
                sx={{
                  px: 0,
                  py: 1,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                  borderRadius: 1,
                  mb: 1,
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, mt: 1 }}>
                  {getSeverityIcon(alert.severity)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        flexWrap: 'wrap',
                      }}
                    >
                      <Typography
                        variant="body1"
                        component="span"
                        sx={{ fontWeight: 500 }}
                      >
                        {alert.message}
                      </Typography>
                      <Chip
                        label={getSeverityLabel(alert.severity)}
                        color={getSeverityColor(alert.severity)}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  }
                  secondary={
                    showTimestamp ? (
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        component="span"
                      >
                        {formatDateTime(alert.created_at)}
                      </Typography>
                    ) : null
                  }
                />
              </ListItem>
              {index < displayAlerts.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
        </List>

        {hiddenCount > 0 && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Y {hiddenCount} {hiddenCount === 1 ? 'alerta más' : 'alertas más'}...
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

function AlertsListCompact({ alerts }: { alerts: Alert[] }) {
  if (alerts.length === 0) {
    return null;
  }

  return (
    <Box sx={{ width: '100%' }}>
      {alerts.slice(0, 3).map((alert) => (
        <MuiAlert
          key={alert.id}
          severity={getSeverityColor(alert.severity)}
          sx={{ mb: 1 }}
        >
          <AlertTitle sx={{ m: 0 }}>
            {getSeverityLabel(alert.severity)}
          </AlertTitle>
          {alert.message}
        </MuiAlert>
      ))}
      {alerts.length > 3 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          +{alerts.length - 3} más
        </Typography>
      )}
    </Box>
  );
}

export default AlertsList;
export { AlertsListCompact };
