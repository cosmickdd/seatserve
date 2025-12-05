import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { restaurantsAPI, subscriptionsAPI, plansAPI, ordersAPI, tablesAPI } from '../api/endpoints';
import { Card, Button, Spinner, Alert, EmptyState } from '../components/common';
import { DashboardLayout, Navbar } from '../components/layout';
import { formatCurrency } from '../utils/helpers';

export const DashboardPage = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  const navigate = useNavigate();

  const [restaurant, setRestaurant] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        
        const restaurantRes = await restaurantsAPI.getMe();
        setRestaurant(restaurantRes.data);

        if (restaurantRes.data?.active_subscription) {
          setSubscription(restaurantRes.data.active_subscription);
        }

        const statsRes = await ordersAPI.getStats();
        setStats(statsRes.data);
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, navigate]);

  if (!restaurant) {
    return (
      <div>
        <Navbar />
        <div className="flex items-center justify-center h-screen">
          <Spinner size="lg" />
        </div>
      </div>
    );
  }

  const sidebarItems = [
    { path: '/dashboard', label: '📊 Overview', icon: '📊' },
    { path: '/dashboard/tables', label: '🪑 Tables & QR', icon: '🪑' },
    { path: '/dashboard/menu', label: '🍽️ Menu', icon: '🍽️' },
    { path: '/dashboard/orders', label: '📋 Orders', icon: '📋' },
    { path: '/dashboard/staff', label: '👥 Staff', icon: '👥' },
    { path: '/dashboard/subscription', label: '💳 Subscription', icon: '💳' },
    { path: '/dashboard/settings', label: '⚙️ Settings', icon: '⚙️' },
  ];

  return (
    <DashboardLayout sidebar={sidebarItems}>
      <h1 className="text-4xl font-bold mb-8">Welcome, {restaurant.name}!</h1>

      {error && <Alert type="error" message={error} />}

      <div className="grid grid-cols-4 gap-6 mb-8">
        <Card>
          <h3 className="text-gray-600 text-sm font-medium mb-2">Today's Orders</h3>
          <p className="text-3xl font-bold text-blue-600">{stats?.total_orders_today || 0}</p>
        </Card>

        <Card>
          <h3 className="text-gray-600 text-sm font-medium mb-2">Today's Revenue</h3>
          <p className="text-3xl font-bold text-green-600">
            {formatCurrency(stats?.total_revenue_today || 0)}
          </p>
        </Card>

        <Card>
          <h3 className="text-gray-600 text-sm font-medium mb-2">Pending Orders</h3>
          <p className="text-3xl font-bold text-orange-600">{stats?.pending_orders || 0}</p>
        </Card>

        <Card>
          <h3 className="text-gray-600 text-sm font-medium mb-2">Plan Status</h3>
          <p className="text-lg font-bold text-blue-600">
            {subscription?.plan_name || 'No Plan'}
          </p>
        </Card>
      </div>

      {!subscription && (
        <Card className="bg-blue-50 border-2 border-blue-300 mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold mb-2">Get Started with a Plan</h3>
              <p className="text-gray-600">Choose a plan to unlock all features</p>
            </div>
            <Button onClick={() => navigate('/dashboard/subscription')}>
              View Plans
            </Button>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <Button onClick={() => navigate('/dashboard/tables')} variant="secondary" className="w-full">
              Manage Tables
            </Button>
            <Button onClick={() => navigate('/dashboard/menu')} variant="secondary" className="w-full">
              Edit Menu
            </Button>
            <Button onClick={() => navigate('/dashboard/orders')} variant="secondary" className="w-full">
              View Orders
            </Button>
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-bold mb-4">Restaurant Info</h3>
          <div className="space-y-3 text-sm">
            <div>
              <p className="text-gray-600">Email</p>
              <p className="font-medium">{restaurant.email}</p>
            </div>
            <div>
              <p className="text-gray-600">Phone</p>
              <p className="font-medium">{restaurant.phone || 'Not set'}</p>
            </div>
            <div>
              <p className="text-gray-600">Location</p>
              <p className="font-medium">
                {restaurant.city && restaurant.country
                  ? `${restaurant.city}, ${restaurant.country}`
                  : 'Not set'}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};
