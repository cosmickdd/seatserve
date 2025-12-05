export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date));
};

export const formatDateTime = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
};

export const getStatusBadgeColor = (status) => {
  const colors = {
    RECEIVED: 'bg-blue-100 text-blue-800',
    IN_KITCHEN: 'bg-yellow-100 text-yellow-800',
    READY_TO_SERVE: 'bg-green-100 text-green-800',
    SERVED: 'bg-gray-100 text-gray-800',
    CANCELLED: 'bg-red-100 text-red-800',
    PENDING: 'bg-orange-100 text-orange-800',
    PAID: 'bg-green-100 text-green-800',
    FAILED: 'bg-red-100 text-red-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

export const getStatusLabel = (status) => {
  const labels = {
    RECEIVED: 'Received',
    IN_KITCHEN: 'In Kitchen',
    READY_TO_SERVE: 'Ready to Serve',
    SERVED: 'Served',
    CANCELLED: 'Cancelled',
    PENDING: 'Pending',
    PAID: 'Paid',
    FAILED: 'Failed',
    ACTIVE: 'Active',
    EXPIRED: 'Expired',
  };
  return labels[status] || status;
};
