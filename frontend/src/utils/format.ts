// Utility formatting functions for dates, currency, quantities, and percentages

export function formatDateTime(dateString: string | Date): string {
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  if (isNaN(date.getTime())) return '';
  return date.toLocaleString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDate(dateString: string | Date): string {
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  if (isNaN(date.getTime())) return '';
  return date.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function formatCurrency(amount: number, currency: string = 'MXN'): string {
  return amount.toLocaleString('es-MX', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatQuantity(quantity: number, decimals: number = 2): string {
  return quantity.toLocaleString('es-MX', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function calculatePercentage(part: number, total: number, decimals: number = 2): string {
  if (!total || total === 0) return '0%';
  const percent = (part / total) * 100;
  return percent.toFixed(decimals) + '%';
}
