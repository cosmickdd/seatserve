import React from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Button, Container } from '../components/common';
import { Navbar, Footer } from '../components/layout';

export const HomePage = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);

  const features = [
    {
      icon: '🪑',
      title: 'Table Management',
      description: 'Organize and manage your restaurant tables with ease',
    },
    {
      icon: '📱',
      title: 'QR Code Ordering',
      description: 'Customers scan QR codes at their tables to order',
    },
    {
      icon: '🍽️',
      title: 'Menu Management',
      description: 'Create and manage menu items, categories, and pricing',
    },
    {
      icon: '📊',
      title: 'Live Dashboard',
      description: 'Real-time view of all incoming orders and status',
    },
    {
      icon: '💳',
      title: 'Online Payments',
      description: 'Accept payments directly through your QR ordering system',
    },
    {
      icon: '📈',
      title: 'Analytics',
      description: 'Track sales, popular items, and business metrics',
    },
  ];

  const plans = [
    {
      name: 'Basic',
      price: '$9.99',
      period: '/month',
      description: 'Perfect for small restaurants',
      features: ['Up to 5 tables', 'Up to 50 menu items', 'QR Ordering', 'Live Dashboard'],
    },
    {
      name: 'Standard',
      price: '$24.99',
      period: '/month',
      description: 'For growing restaurants',
      features: ['Up to 20 tables', 'Up to 200 menu items', 'All Basic features', 'Online Payments', 'Staff Roles'],
      featured: true,
    },
    {
      name: 'Pro',
      price: '$49.99',
      period: '/month',
      description: 'For large restaurants & chains',
      features: ['Unlimited tables', 'Unlimited menu items', 'All Standard features', 'Analytics', 'Delivery Integration'],
    },
  ];

  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-700 text-white py-20">
        <Container>
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl font-bold mb-6">
              Modern QR Ordering for Restaurants
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              SeatServe helps restaurants streamline orders, manage tables, and accept
              payments—all through simple QR codes at each table.
            </p>
            <div className="flex gap-4 justify-center">
              <Link to={isAuthenticated ? '/dashboard' : '/signup'}>
                <Button size="lg" variant="outline" className="bg-white text-blue-600 hover:bg-gray-100">
                  Get Started
                </Button>
              </Link>
              <a href="#features">
                <Button size="lg" variant="outline">
                  Learn More
                </Button>
              </a>
            </div>
          </div>
        </Container>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <Container>
          <h2 className="text-4xl font-bold text-center mb-16">Why Choose SeatServe?</h2>
          <div className="grid grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <div key={i} className="text-center">
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <Container>
          <h2 className="text-4xl font-bold text-center mb-16">How It Works</h2>
          <div className="grid grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-bold mb-3">Sign Up & Choose Plan</h3>
              <p className="text-gray-600">Create your restaurant account and select a plan that fits your needs</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-bold mb-3">Set Up Tables & Menu</h3>
              <p className="text-gray-600">Add your restaurant tables and create your menu with items and pricing</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-bold mb-3">Print QR Codes & Go Live</h3>
              <p className="text-gray-600">Print QR codes for each table and start accepting orders immediately</p>
            </div>
          </div>
        </Container>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white">
        <Container>
          <h2 className="text-4xl font-bold text-center mb-16">Simple, Transparent Pricing</h2>
          <div className="grid grid-cols-3 gap-8 max-w-4xl mx-auto">
            {plans.map((plan, i) => (
              <div
                key={i}
                className={`rounded-lg p-8 ${
                  plan.featured
                    ? 'border-2 border-blue-600 shadow-lg transform scale-105'
                    : 'border border-gray-200 shadow'
                }`}
              >
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{plan.description}</p>
                <div className="mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-gray-600">{plan.period}</span>
                </div>
                <Button variant={plan.featured ? 'primary' : 'outline'} className="w-full mb-6">
                  Get Started
                </Button>
                <ul className="space-y-3 text-sm">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-2">
                      <span className="text-green-600">✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <Container>
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Restaurant?</h2>
            <p className="text-xl mb-8 text-blue-100">
              Join hundreds of restaurants already using SeatServe
            </p>
            <Link to={isAuthenticated ? '/dashboard' : '/signup'}>
              <Button size="lg" variant="outline" className="bg-white text-blue-600 hover:bg-gray-100">
                Start Free Today
              </Button>
            </Link>
          </div>
        </Container>
      </section>

      <Footer />
    </>
  );
};
