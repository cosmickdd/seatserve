import React from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/authSlice';
import { Button } from './common';

export const Navbar = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector((state) => state.auth);

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            🪑 SeatServe
          </Link>

          <div className="flex gap-4 items-center">
            {!isAuthenticated ? (
              <>
                <Link to="/login">
                  <Button variant="outline" size="sm">
                    Login
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button size="sm">Sign Up</Button>
                </Link>
              </>
            ) : (
              <>
                <span className="text-gray-700">{user?.email}</span>
                <Link to="/dashboard">
                  <Button variant="secondary" size="sm">
                    Dashboard
                  </Button>
                </Link>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => dispatch(logout())}
                >
                  Logout
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export const Sidebar = ({ items = [] }) => {
  return (
    <aside className="w-64 bg-gray-900 text-white h-screen overflow-y-auto">
      <div className="p-4">
        <Link to="/" className="text-2xl font-bold">
          🪑 SeatServe
        </Link>
      </div>

      <nav className="mt-8">
        {items.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="block px-4 py-3 hover:bg-gray-800 transition-colors"
          >
            {item.icon && <span className="mr-2">{item.icon}</span>}
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export const DashboardLayout = ({ children, sidebar = [] }) => {
  return (
    <div className="flex">
      <Sidebar items={sidebar} />
      <main className="flex-1 bg-gray-50 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export const Container = ({ children, className = '' }) => (
  <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
    {children}
  </div>
);

export const Footer = () => (
  <footer className="bg-gray-900 text-white py-12">
    <Container>
      <div className="grid grid-cols-4 gap-8 mb-8">
        <div>
          <h3 className="font-bold mb-4">SeatServe</h3>
          <p className="text-gray-400">Modern QR ordering for restaurants</p>
        </div>
        <div>
          <h4 className="font-semibold mb-4">Product</h4>
          <ul className="text-gray-400 space-y-2">
            <li><a href="#" className="hover:text-white">Features</a></li>
            <li><a href="#" className="hover:text-white">Pricing</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-4">Company</h4>
          <ul className="text-gray-400 space-y-2">
            <li><a href="#" className="hover:text-white">About</a></li>
            <li><a href="#" className="hover:text-white">Contact</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold mb-4">Legal</h4>
          <ul className="text-gray-400 space-y-2">
            <li><a href="#" className="hover:text-white">Privacy</a></li>
            <li><a href="#" className="hover:text-white">Terms</a></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
        <p>&copy; 2025 SeatServe. All rights reserved.</p>
      </div>
    </Container>
  </footer>
);
