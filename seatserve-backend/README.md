# 🍽️ SeatServe - Restaurant Management Platform

**Transform your restaurant's operations with intelligent table management, QR-based ordering, real-time dashboards, and seamless payment processing.**

## Why SeatServe?

✨ **Features that drive revenue**
- 📱 **QR-Based Ordering** - Customers order directly from their tables
- 🍽️ **Intelligent Table Management** - Optimize seating and reduce wait times
- 📊 **Real-Time Dashboards** - Track orders, payments, and performance instantly
- 💳 **Integrated Payments** - Accept payments directly from orders
- 📈 **Multi-Restaurant Support** - Manage multiple locations from one dashboard
- 🔒 **Enterprise Security** - Production-grade authentication and encryption

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (production) or SQLite (development)

### Setup (5 minutes)

```bash
# 1. Clone and navigate
cd seatserve-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings (DEBUG=True for development)

# 5. Initialize database
python manage.py migrate
python manage.py seed_data

# 6. Start server
python manage.py runserver

# 7. Access the API
# → http://localhost:8000/api/
# → Admin: http://localhost:8000/admin/
```

## API Overview

The SeatServe API uses **JWT authentication** with **role-based access control** for enterprise-grade security.

### 🔐 Authentication & User Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/register/create/` | Register new restaurant owner |
| POST | `/api/auth/auth/login/` | Login with email/password |
| POST | `/api/auth/auth/refresh/` | Refresh access token |
| POST | `/api/auth/auth/logout/` | Logout and invalidate token |
| GET | `/api/auth/profile/me/` | Get current user profile |

### 🏢 Restaurant Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/restaurants/me/create_restaurant/` | Create new restaurant |
| GET | `/api/restaurants/me/` | Get restaurant details |
| PUT | `/api/restaurants/me/update_me/` | Update restaurant settings |

### 💰 Subscription & Billing
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/restaurants/plans/` | Browse subscription plans |
| GET | `/api/restaurants/subscriptions/my_subscription/` | View current plan |
| POST | `/api/restaurants/subscriptions/select_plan/` | Upgrade/change plan |
| GET | `/api/restaurants/subscriptions/subscription_history/` | View billing history |

### 🪑 Table Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/restaurants/tables/` | List all tables |
| POST | `/api/restaurants/tables/` | Create new table |
| PUT | `/api/restaurants/tables/{id}/` | Update table details |
| DELETE | `/api/restaurants/tables/{id}/` | Delete table |
| GET | `/api/restaurants/tables/{id}/qr_code/` | Get QR code for table |
| GET | `/api/restaurants/tables/stats/` | View table analytics |

### 🍴 Menu Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/menu/categories/` | List categories |
| POST | `/api/menu/categories/` | Create category |
| PUT | `/api/menu/categories/{id}/` | Update category |
| DELETE | `/api/menu/categories/{id}/` | Delete category |
| GET | `/api/menu/items/` | List menu items |
| POST | `/api/menu/items/` | Add menu item |
| PUT | `/api/menu/items/{id}/` | Update menu item |
| DELETE | `/api/menu/items/{id}/` | Remove menu item |
| GET | `/api/menu/items/by_category/` | Items grouped by category |

### 📋 Order Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/orders/` | View all orders |
| GET | `/api/orders/today/` | Today's orders |
| GET | `/api/orders/pending/` | Active orders |
| GET | `/api/orders/{id}/` | Order details |
| PATCH | `/api/orders/{id}/update_status/` | Update order status |
| GET | `/api/orders/stats/` | Order analytics |

### 💳 Payment Processing
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/payments/` | Payment history |
| GET | `/api/payments/today/` | Today's payments |

### 👥 Public Customer API (No Authentication)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/public/restaurant/{id}/table/{token}/menu/` | Customer menu |
| POST | `/api/public/restaurant/{id}/table/{token}/orders/` | Place order |
| GET | `/api/public/order/{token}/` | Check order status |

## How It Works

### 🏗️ Architecture

SeatServe uses a **multi-tenant architecture** where each restaurant operates in complete data isolation. Here's what powers it:

- **JWT Authentication**: Secure token-based auth with role-based access control
- **PostgreSQL Database**: Scalable relational data storage
- **Django REST Framework**: Enterprise-grade API framework
- **Stripe Integration**: PCI-compliant payment processing
- **QR Code Generation**: Automatic unique codes per table

### 🔑 Core Entities

| Entity | Purpose | Key Fields |
|--------|---------|-----------|
| **User** | Restaurant owner/staff | email, role, password |
| **Plan** | Subscription tier | name, price, max_tables, features |
| **Restaurant** | Your business | name, location, subscription_status |
| **Table** | Physical dining table | number, qr_token, capacity |
| **Category** | Menu grouping | name (e.g., "Appetizers", "Mains") |
| **MenuItem** | Individual dish | name, price, description, availability |
| **Order** | Customer order | items, status, total, timestamp |
| **Payment** | Transaction record | amount, status, stripe_reference |

### 🔒 Security Features

Built with enterprise security in mind:

- ✅ **HTTP-Only Cookies** - XSS protection
- ✅ **Rate Limiting** - DDoS & brute force protection
- ✅ **Webhook Verification** - Stripe signature verification
- ✅ **Strong Passwords** - 12+ character minimum
- ✅ **Security Headers** - HSTS, CSP, X-Frame-Options
- ✅ **Audit Logging** - Track all security events
- ✅ **Environment Isolation** - Separate dev/production configs

## Management Dashboard

Access the Django Admin at `http://localhost:8000/admin/`

**Full control over:**
- 👥 Users & Roles - Manage team members and permissions
- 💰 Plans & Billing - Create subscription tiers
- 🏪 Restaurants - Monitor all locations
- 📊 Subscriptions - Track active plans
- 🪑 Tables - Configure seating
- 🍽️ Menus - Update items and pricing
- 📋 Orders - Review order history
- 💳 Payments - Track transactions

## Deployment Guide

### Development Setup
```bash
# SQLite works fine for local development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Production Setup
```bash
# Use PostgreSQL for production
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/seatserve
ALLOWED_HOSTS=api.seatserve.com

# Enable security features
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# Stripe configuration
STRIPE_LIVE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Backup & Recovery
# → Regular database backups
# → Automated security logs
```

### Docker Deployment
```bash
# Build image
docker build -t seatserve-api .

# Run container
docker run -p 8000:8000 --env-file .env seatserve-api

# With docker-compose
docker-compose up
```

### Key Production Considerations

| Area | Requirement | Impact |
|------|-------------|--------|
| **Database** | PostgreSQL 12+ | Handles concurrent users |
| **Cache** | Redis | Menu & session caching |
| **Security** | SSL/TLS | HTTPS enforced |
| **Monitoring** | APM Service | Error tracking |
| **Backups** | Daily Snapshots | Data recovery |
| **Logging** | Centralized Logs | Audit trail |

## Roadmap

### Current (v1.0) ✅
- ✅ Multi-restaurant management
- ✅ QR-based ordering system
- ✅ Real-time order tracking
- ✅ Payment integration
- ✅ User authentication & authorization
- ✅ Admin dashboard
- ✅ Enterprise security

### Upcoming (v2.0)
- 📱 Mobile app for restaurant staff
- 🤖 AI-powered demand forecasting
- 📊 Advanced analytics & reporting
- 💌 Email & SMS notifications
- 🏪 Multi-location analytics
- 🔗 Integration marketplace
- 🎯 Customer loyalty program
- 📦 Inventory management

## Support & Documentation

- 📖 **API Docs** - [Full API Reference](#api-overview)
- 🆘 **Troubleshooting** - Check `.env.example` for configuration
- 🔐 **Security** - See `SECURITY.md` for security information
- 📧 **Contact** - support@seatserve.com

## License

Proprietary - SeatServe © 2025
