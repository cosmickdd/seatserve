# SeatServe - Multi-Tenant Restaurant SaaS Platform

A production-ready SaaS platform for restaurants to manage tables, QR-based ordering, menus, live order dashboards, and payments.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- pip, npm/yarn
- Git

### Setup Backend

```bash
cd seatserve-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Seed initial data (plans)
python manage.py seed_data

# Create superuser (for admin access)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`
Admin panel at `http://localhost:8000/admin`

### Setup Frontend

```bash
cd seatserve-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📋 System Architecture

### Tech Stack

**Backend:**
- Django 4.2 + Django REST Framework
- PostgreSQL (SQLite for dev)
- JWT Authentication
- Redis (optional, for caching)

**Frontend:**
- React 18 with Vite
- Redux Toolkit (state management)
- React Router v6
- Tailwind CSS
- Axios

### Database Models

```
User (Custom)
├── Restaurant (1-to-1)
│   ├── RestaurantSubscription → Plan
│   ├── Table
│   ├── Category
│   │   └── MenuItem
│   ├── Order
│   │   └── OrderItem → MenuItem
│   └── Payment
```

## 🎯 Core Features

### For Restaurants
- ✅ Sign up and subscription management
- ✅ Table management with QR code generation
- ✅ Menu management (categories, items, pricing)
- ✅ Live order dashboard with status tracking
- ✅ Payment status monitoring
- ✅ Daily revenue and order statistics

### For Customers
- ✅ Scan QR code at table
- ✅ Browse restaurant menu
- ✅ Place order and pay
- ✅ Track order status in real-time
- ✅ View estimated preparation time

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register/create/       - Register restaurant
POST   /api/auth/auth/login/            - Login
POST   /api/auth/auth/refresh/          - Refresh token
GET    /api/auth/profile/me/            - Get profile
```

### Restaurants & Plans
```
GET    /api/restaurants/plans/          - List plans
GET    /api/restaurants/me/             - Get my restaurant
POST   /api/restaurants/me/create_restaurant/ - Create restaurant
```

### Subscriptions
```
GET    /api/restaurants/subscriptions/my_subscription/     - Current subscription
POST   /api/restaurants/subscriptions/select_plan/         - Select plan
```

### Tables
```
GET    /api/restaurants/tables/         - List tables
POST   /api/restaurants/tables/         - Create table
GET    /api/restaurants/tables/{id}/qr_code/ - Get QR code
```

### Menu
```
GET    /api/menu/categories/            - List categories
POST   /api/menu/categories/            - Create category
GET    /api/menu/items/                 - List items
POST   /api/menu/items/                 - Create item
```

### Orders (Restaurant)
```
GET    /api/orders/                     - List orders
GET    /api/orders/today/               - Today's orders
PATCH  /api/orders/{id}/update_status/  - Update status
GET    /api/orders/stats/               - Statistics
```

### Public API (Customers)
```
GET    /api/public/restaurant/{id}/table/{token}/menu/  - Get menu
POST   /api/public/restaurant/{id}/table/{token}/orders/ - Create order
GET    /api/public/order/{token}/       - Order status
```

## 📊 User Roles

| Role | Permissions |
|------|------------|
| SUPER_ADMIN | Manage all restaurants, plans, billing |
| RESTAURANT | Manage own restaurant, tables, menu, orders |
| STAFF | View orders, update status (future feature) |
| CUSTOMER | Place orders via QR |

## 🔐 Authentication

- JWT-based authentication
- Access token: 1 hour expiry
- Refresh token: 7 day expiry
- Automatic token refresh on client side
- Secure password hashing (PBKDF2)

## 💳 Plans

### Basic ($9.99/month)
- Up to 5 tables
- Up to 50 menu items
- QR ordering
- Live dashboard

### Standard ($24.99/month)
- Up to 20 tables
- Up to 200 menu items
- All Basic features
- Online payments
- Staff roles

### Pro ($49.99/month)
- Unlimited tables & items
- All features
- Analytics
- Delivery integration

## 🛠️ Development

### Project Structure
```
seatserve/
├── seatserve-backend/
│   ├── config/              # Django settings
│   ├── accounts/            # User authentication
│   ├── restaurants/         # Restaurant, plans, tables
│   ├── menu/                # Menu management
│   ├── orders/              # Order management
│   ├── payments/            # Payment processing
│   ├── manage.py
│   └── requirements.txt
│
└── seatserve-frontend/
    ├── src/
    │   ├── api/             # API client
    │   ├── components/      # React components
    │   ├── pages/           # Page components
    │   ├── store/           # Redux store
    │   ├── utils/           # Utilities
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

### Running Tests

Backend:
```bash
cd seatserve-backend
python manage.py test
```

Frontend:
```bash
cd seatserve-frontend
npm test
```

### Database Migrations

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# See migration status
python manage.py showmigrations
```

## 🚀 Production Deployment

### Backend (Django)

1. **Switch to PostgreSQL**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'seatserve',
           'USER': 'postgres',
           'PASSWORD': '...',
           'HOST': 'prod-db.example.com',
           'PORT': '5432',
       }
   }
   ```

2. **Configure environment variables**
   ```bash
   SECRET_KEY=very-secret-key
   DEBUG=False
   ALLOWED_HOSTS=seatserve.com,www.seatserve.com
   DATABASE_URL=postgresql://user:pass@host:5432/db
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Run with Gunicorn**
   ```bash
   gunicorn config.wsgi:application
   ```

6. **Use Nginx as reverse proxy**
   ```nginx
   location /api/ {
       proxy_pass http://localhost:8000;
       proxy_set_header Host $host;
   }
   ```

### Frontend (React)

1. **Build for production**
   ```bash
   npm run build
   ```

2. **Deploy to CDN/Vercel**
   ```bash
   vercel deploy
   ```

3. **Configure API endpoint**
   ```bash
   VITE_API_URL=https://api.seatserve.com
   ```

## 🐛 Common Issues

### Backend issues

**Migrations fail**
```bash
python manage.py migrate --fake-initial
```

**Port 8000 already in use**
```bash
python manage.py runserver 8001
```

**Database reset (development only)**
```bash
python manage.py flush
python manage.py migrate
python manage.py seed_data
```

### Frontend issues

**CORS errors**
- Ensure Django CORS is configured
- Check ALLOWED_HOSTS
- Verify API URL in .env

**Token not persisting**
- Check localStorage in browser devtools
- Clear cache and cookies
- Check login response includes tokens

**API requests failing**
- Verify backend is running
- Check network tab in devtools
- Verify API URL matches

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Redux Documentation](https://redux.js.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 📝 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Customer loyalty program
- [ ] Advanced analytics & reporting
- [ ] Staff management dashboard
- [ ] Kitchen display system (KDS)
- [ ] Delivery integration
- [ ] SMS/Email notifications
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Offline mode
- [ ] API rate limiting
- [ ] Advanced search & filtering

## 📄 License

Proprietary - SeatServe

## 👥 Support

For issues, questions, or feedback:
- GitHub Issues: [link]
- Email: support@seatserve.com
- Documentation: [link]

---

**Built with ❤️ for restaurants**
