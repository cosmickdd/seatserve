import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../api/config';

export default function OrderAcceptancePage() {
  const { orderToken } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/public/orders/${orderToken}/`
        );
        if (!response.ok) {
          setError('Order not found');
          return;
        }
        const data = await response.json();
        setOrder(data);
      } catch (err) {
        setError('Failed to load order details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (orderToken) {
      fetchOrder();
    }
  }, [orderToken]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading order...</p>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <p className="text-red-600 font-medium mb-4">{error}</p>
          <a href="/" className="text-indigo-600 hover:underline">
            Return to home
          </a>
        </div>
      </div>
    );
  }

  const statusColors = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    CONFIRMED: 'bg-blue-100 text-blue-800',
    PREPARING: 'bg-orange-100 text-orange-800',
    READY: 'bg-green-100 text-green-800',
    COMPLETED: 'bg-gray-100 text-gray-800',
    CANCELLED: 'bg-red-100 text-red-800',
  };

  const itemStatusColors = {
    pending: 'bg-gray-100 text-gray-800',
    preparing: 'bg-orange-100 text-orange-800',
    ready: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Order #{order.order_number}
              </h1>
              <p className="text-gray-600">
                Table: <span className="font-semibold">{order.table_name}</span>
              </p>
            </div>
            <div>
              <span
                className={`inline-block px-4 py-2 rounded-full font-semibold ${
                  statusColors[order.status] || 'bg-gray-100 text-gray-800'
                }`}
              >
                {order.status}
              </span>
            </div>
          </div>

          {/* Timeline */}
          <div className="space-y-2 text-sm text-gray-600">
            <p>
              <span className="font-semibold">Ordered:</span>{' '}
              {new Date(order.created_at).toLocaleTimeString()}
            </p>
            {order.updated_at && (
              <p>
                <span className="font-semibold">Updated:</span>{' '}
                {new Date(order.updated_at).toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>

        {/* Order Items */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Items</h2>
          <div className="space-y-3">
            {order.items && order.items.length > 0 ? (
              order.items.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800">
                      {item.menu_item_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      Quantity: {item.quantity}
                      {item.notes && (
                        <span className="ml-2 italic">- {item.notes}</span>
                      )}
                    </p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        itemStatusColors[item.status] ||
                        'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {item.status?.toUpperCase() || 'PENDING'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No items in this order</p>
            )}
          </div>
        </div>

        {/* Summary */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Summary</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal:</span>
              <span className="font-semibold">
                ${(order.subtotal || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tax:</span>
              <span className="font-semibold">
                ${(order.tax || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Service Charge:</span>
              <span className="font-semibold">
                ${(order.service_charge || 0).toFixed(2)}
              </span>
            </div>
            <div className="border-t pt-2 flex justify-between">
              <span className="font-bold text-gray-800">Total:</span>
              <span className="text-2xl font-bold text-indigo-600">
                ${(order.total || 0).toFixed(2)}
              </span>
            </div>
          </div>

          {/* Payment Status */}
          {order.payment_status && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm">
                <span className="font-semibold">Payment Status:</span>{' '}
                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                    order.payment_status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {order.payment_status.toUpperCase()}
                </span>
              </p>
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="mt-8 text-center text-gray-600 text-sm">
          <p>
            Your order status will update automatically.{' '}
            <button
              onClick={() => window.location.reload()}
              className="text-indigo-600 hover:underline font-medium"
            >
              Refresh page
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
