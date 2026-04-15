import React from 'react';
import { Alert } from '../types';
import { formatDateTime } from '../utils/format';

interface AlertsListProps {
  alerts: Alert[];
  maxItems?: number;
}

function getSeverityClass(severity: Alert['severity']) {
  switch (severity) {
    case 'critical': return 'alert-item-icon--error';
    case 'warning':  return 'alert-item-icon--warning';
    default:         return 'alert-item-icon--info';
  }
}

function getSeverityIcon(severity: Alert['severity']) {
  switch (severity) {
    case 'critical': return '🔴';
    case 'warning':  return '🟡';
    default:         return '🔵';
  }
}

function getSeverityLabel(severity: Alert['severity']) {
  switch (severity) {
    case 'critical': return 'Crítico';
    case 'warning':  return 'Advertencia';
    default:         return 'Info';
  }
}

function getBadgeClass(severity: Alert['severity']) {
  switch (severity) {
    case 'critical': return 'badge badge--error';
    case 'warning':  return 'badge badge--warning';
    default:         return 'badge badge--info';
  }
}

export default function AlertsList({ alerts, maxItems = 10 }: AlertsListProps) {
  const displayed = alerts.slice(0, maxItems);
  const hidden = alerts.length - displayed.length;

  if (alerts.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-state-icon">✅</span>
        <span className="empty-state-text">No hay alertas activas en este momento.</span>
      </div>
    );
  }

  return (
    <div>
      {displayed.map((alert) => (
        <div key={alert.id} className="alert-item">
          <div className={`alert-item-icon ${getSeverityClass(alert.severity)}`}>
            {getSeverityIcon(alert.severity)}
          </div>
          <div className="alert-item-body">
            <div className="alert-item-msg">
              {alert.message}
              <span className={getBadgeClass(alert.severity)} style={{ marginLeft: '8px' }}>
                {getSeverityLabel(alert.severity)}
              </span>
            </div>
            <div className="alert-item-time">{formatDateTime(alert.created_at)}</div>
          </div>
        </div>
      ))}
      {hidden > 0 && (
        <div style={{
          textAlign: 'center',
          padding: 'var(--sp-3)',
          fontSize: 'var(--text-xs)',
          color: 'var(--clr-text-3)',
        }}>
          Y {hidden} alerta{hidden > 1 ? 's' : ''} más…
        </div>
      )}
    </div>
  );
}
