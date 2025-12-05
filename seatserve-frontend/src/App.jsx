import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { getProfile } from './store/authSlice';

// Pages
import { HomePage } from './pages/Home';
import { LoginPage, SignupPage } from './pages/Auth';
import { DashboardPage } from './pages/Dashboard';
import CheckoutPage from './pages/CheckoutPage';
import StaffPage from './pages/StaffPage';
import StaffAcceptancePage from './pages/StaffAcceptancePage';
import OrderAcceptancePage from './pages/OrderAcceptancePage';
import KitchenDisplayPage from './pages/KitchenDisplayPage';
import EmailConfigPage from './pages/EmailConfigPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Lazy components for dashboard pages (in production, implement proper splitting)
const TablesPage = () => <div className="p-8"><h1>Tables Management (Coming Soon)</h1></div>;
const MenuPage = () => <div className="p-8"><h1>Menu Management (Coming Soon)</h1></div>;
const OrdersPage = () => <div className="p-8"><h1>Orders Dashboard (Coming Soon)</h1></div>;
const SubscriptionPage = () => <div className="p-8"><h1>Subscription Management (Coming Soon)</h1></div>;
const SettingsPage = () => <div className="p-8"><h1>Settings (Coming Soon)</h1></div>;

// Public customer pages
const CustomerOrderPage = () => <div className="p-8"><h1>Customer Order Page (Coming Soon)</h1></div>;

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    // Check if user is already logged in
    if (isAuthenticated && localStorage.getItem('access_token')) {
      dispatch(getProfile());
    }
  }, [dispatch, isAuthenticated]);

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Customer QR Routes */}
        <Route path="/order/:restaurantId/:tableToken" element={<CustomerOrderPage />} />
        <Route path="/order-status/:orderToken" element={<OrderAcceptancePage />} />
        <Route path="/staff/accept-invitation/:token" element={<StaffAcceptancePage />} />
        
        {/* Payment Routes */}
        <Route 
          path="/checkout/:orderId" 
          element={
            <ProtectedRoute>
              <CheckoutPage />
            </ProtectedRoute>
          } 
        />

        {/* Protected Dashboard Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/tables"
          element={
            <ProtectedRoute>
              <TablesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/menu"
          element={
            <ProtectedRoute>
              <MenuPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/orders"
          element={
            <ProtectedRoute>
              <OrdersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/subscription"
          element={
            <ProtectedRoute>
              <SubscriptionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/staff"
          element={
            <ProtectedRoute>
              <StaffPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/kitchen"
          element={
            <ProtectedRoute>
              <KitchenDisplayPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/email-config"
          element={
            <ProtectedRoute>
              <EmailConfigPage />
            </ProtectedRoute>
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;

