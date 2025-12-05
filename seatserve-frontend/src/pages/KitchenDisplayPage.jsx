import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { API_BASE_URL } from '../api/config';

export default function KitchenDisplayPage() {
  const auth = useSelector((state) => state.auth);
  const restaurantId = auth?.restaurant?.id;

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('PENDING');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch orders from kitchen
  const fetchOrders = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/restaurants/${restaurantId}/orders/?status=${filterStatus}`,
        {
          headers: {
            Authorization: `Bearer ${auth?.token}`,
          },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch orders');

      const data = await response.json();
      setOrders(Array.isArray(data) ? data : data.results || []);
      setError(null);
    } catch (err) {
      setError('Failed to load orders');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh orders
  useEffect(() => {
    fetchOrders();

    if (autoRefresh) {
      const interval = setInterval(fetchOrders, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [filterStatus, autoRefresh, restaurantId, auth?.token]);

  const handleUpdateOrderStatus = async (orderId, newStatus) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/restaurants/${restaurantId}/orders/${orderId}/`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${auth?.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) throw new Error('Failed to update order');

      // Update local state
      setOrders((prev) =>
        prev.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o))
      );
    } catch (err) {
      alert(`Failed to update order: ${err.message}`);
    }
  };

  const handleUpdateItemStatus = async (orderId, itemId, newStatus) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/restaurants/${restaurantId}/orders/${orderId}/items/${itemId}/`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${auth?.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) throw new Error('Failed to update item');

      // Update local state
      setOrders((prev) =>
        prev.map((o) => {
          if (o.id === orderId) {
            return {
              ...o,
              items: o.items.map((item) =>
                item.id === itemId ? { ...item, status: newStatus } : item
              ),
            };
          }
          return o;
        })
      );
    } catch (err) {
      alert(`Failed to update item: ${err.message}`);
    }
  };

  const statusBadgeColor = (status) => {
    const colors = {
      PENDING: 'bg-red-500',
      CONFIRMED: 'bg-blue-500',
      PREPARING: 'bg-orange-500',
      READY: 'bg-green-500',
      COMPLETED: 'bg-gray-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  const priorityColor = (minutesOld) => {
    if (minutesOld > 15) return 'border-red-500 border-4'; // Critical
    if (minutesOld > 10) return 'border-orange-500 border-2'; // Warning
    return 'border-gray-300'; // Normal
  };

  return (
    <div className="h-screen bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <div className="bg-black p-4 border-b-2 border-indigo-600">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">👨‍🍳 Kitchen Display System</h1>
          <div className="flex gap-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm">Auto-Refresh (5s)</span>
            </label>
            <button
              onClick={fetchOrders}
              className="bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded font-semibold transition"
            >
              🔄 Refresh Now
            </button>
          </div>
        </div>
      </div>

      {/* Status Filter */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <div className="flex gap-2 flex-wrap">
          {['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'COMPLETED'].map(
            (status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-4 py-2 rounded font-semibold transition ${
                  filterStatus === status
                    ? `${statusBadgeColor(status)} text-white`
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                {status} ({orders.filter((o) => o.status === status).length})
              </button>
            )
          )}
        </div>
      </div>

      {/* Content */}
      <div className="overflow-auto h-[calc(100vh-130px)] p-4">
        {error && (
          <div className="bg-red-900 border-2 border-red-500 rounded p-4 mb-4">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
            <p>Loading orders...</p>
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-2xl">No orders with status: {filterStatus}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {orders.map((order) => {
              const minutesOld = Math.floor(
                (new Date() - new Date(order.created_at)) / 60000
              );
              const allItemsReady = order.items?.every(
                (item) => item.status === 'ready' || item.status === 'READY'
              );

              return (
                <div
                  key={order.id}
                  className={`bg-gray-800 rounded-lg overflow-hidden border-4 ${priorityColor(
                    minutesOld
                  )}`}
                >
                  {/* Card Header */}
                  <div className={`${statusBadgeColor(order.status)} p-4`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-2xl font-bold">
                          Order #{order.order_number}
                        </h3>
                        <p className="text-sm opacity-90">
                          Table: {order.table_name}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm opacity-90">
                          {minutesOld} min ago
                        </p>
                        {minutesOld > 15 && (
                          <span className="inline-block bg-red-700 px-2 py-1 rounded text-xs font-bold mt-1">
                            ⚠️ URGENT
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Items */}
                  <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
                    {order.items && order.items.length > 0 ? (
                      order.items.map((item) => (
                        <div key={item.id} className="bg-gray-700 rounded p-3">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <p className="font-semibold text-lg">
                                {item.quantity}x {item.menu_item_name}
                              </p>
                              {item.notes && (
                                <p className="text-xs text-yellow-300 mt-1">
                                  📝 {item.notes}
                                </p>
                              )}
                            </div>
                            <div className="ml-2">
                              <span
                                className={`inline-block px-2 py-1 rounded text-xs font-bold ${
                                  item.status === 'ready' ||
                                  item.status === 'READY'
                                    ? 'bg-green-500 text-white'
                                    : item.status === 'preparing' ||
                                      item.status === 'PREPARING'
                                    ? 'bg-orange-500 text-white'
                                    : 'bg-gray-600 text-gray-300'
                                }`}
                              >
                                {item.status?.toUpperCase() || 'PENDING'}
                              </span>
                            </div>
                          </div>

                          {/* Item Actions */}
                          <div className="flex gap-2 mt-2">
                            <button
                              onClick={() =>
                                handleUpdateItemStatus(
                                  order.id,
                                  item.id,
                                  'PREPARING'
                                )
                              }
                              className="flex-1 bg-orange-600 hover:bg-orange-700 px-2 py-1 rounded text-xs font-bold transition"
                            >
                              Start
                            </button>
                            <button
                              onClick={() =>
                                handleUpdateItemStatus(
                                  order.id,
                                  item.id,
                                  'READY'
                                )
                              }
                              className="flex-1 bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs font-bold transition"
                            >
                              Ready
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No items</p>
                    )}
                  </div>

                  {/* Card Footer */}
                  <div className="bg-gray-700 p-4 border-t border-gray-600">
                    {allItemsReady ? (
                      <button
                        onClick={() =>
                          handleUpdateOrderStatus(order.id, 'READY')
                        }
                        className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded font-bold transition"
                      >
                        ✅ Mark Order Ready
                      </button>
                    ) : (
                      <p className="text-center text-gray-400 text-sm">
                        Waiting for items...
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
