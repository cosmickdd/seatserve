# SeatServe Frontend

A modern React SPA for the SeatServe multi-tenant restaurant management platform.

## Project Structure

```
src/
├── api/                    # API client and endpoints
├── components/
│   ├── common.jsx         # Reusable UI components
│   └── layout.jsx         # Layout components (Navbar, Sidebar, etc)
├── pages/                 # Page components
│   ├── Home.jsx           # Marketing homepage
│   ├── Auth.jsx           # Login/Signup pages
│   └── Dashboard.jsx      # Main dashboard
├── store/
│   ├── authSlice.js       # Redux auth slice
│   └── store.js           # Redux store configuration
├── utils/
│   └── helpers.js         # Utility functions
├── App.jsx                # Main app with routing
├── main.jsx               # Entry point
├── index.css              # Global styles
└── index.html             # HTML template
```

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd seatserve-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create .env file** (optional)
   ```bash
   VITE_API_URL=http://localhost:8000/api
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3000`

## Development

### Key Technologies

- **React 18** - UI library
- **React Router v6** - Client-side routing
- **Redux Toolkit** - State management
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Vite** - Build tool

### API Integration

API calls are centralized in `src/api/endpoints.js`. Each API module is organized by feature:

```javascript
// Example usage
import { restaurantsAPI, tablesAPI } from '../api/endpoints';

const restaurant = await restaurantsAPI.getMe();
const tables = await tablesAPI.list();
```

### State Management

Redux is used for global state management, currently focused on authentication:

```javascript
import { useSelector, useDispatch } from 'react-redux';
import { loginUser, logout } from '../store/authSlice';

const { user, isAuthenticated, loading } = useSelector(state => state.auth);
const dispatch = useDispatch();

dispatch(loginUser({ email, password }));
dispatch(logout());
```

### Styling

TailwindCSS is pre-configured. Use utility classes in components:

```jsx
<div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
  <h1 className="text-2xl font-bold">Title</h1>
</div>
```

## Building

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Features Implemented

### ✅ Completed
- Home/marketing page
- User registration & login
- JWT authentication with token refresh
- Main dashboard
- Redux state management
- Responsive layout
- Reusable UI components
- API client with auto-token injection

### 🚧 In Progress / TODO
- [ ] Tables management page
- [ ] Menu management page
- [ ] Orders dashboard with real-time updates
- [ ] Subscription selection & management
- [ ] Settings page
- [ ] QR code scanning page
- [ ] Customer ordering flow
- [ ] Order status tracking
- [ ] Payment integration UI
- [ ] Toast notifications
- [ ] Form validation improvements
- [ ] Error boundary
- [ ] Loading skeletons
- [ ] Dark mode support

## Page Routes

### Public Routes
- `/` - Home/marketing page
- `/login` - Login page
- `/signup` - Registration page
- `/order/:restaurantId/:tableToken` - Customer ordering (QR-based)
- `/order-status/:orderToken` - Order status tracking

### Protected Routes (Restaurant Dashboard)
- `/dashboard` - Main overview
- `/dashboard/tables` - Table management
- `/dashboard/menu` - Menu management
- `/dashboard/orders` - Orders dashboard
- `/dashboard/subscription` - Plan management
- `/dashboard/settings` - Settings

## Component Examples

### Button Component
```jsx
<Button 
  onClick={handleClick}
  variant="primary"
  size="lg"
  loading={isLoading}
>
  Click Me
</Button>
```

### Card Component
```jsx
<Card className="bg-blue-50">
  <h3>Title</h3>
  <p>Content</p>
</Card>
```

### Input Component
```jsx
<Input
  label="Email"
  type="email"
  placeholder="your@email.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={errors.email}
  required
/>
```

## API Integration

### Authentication Flow
1. User enters credentials
2. Redux action `loginUser` called
3. API returns access and refresh tokens
4. Tokens stored in localStorage
5. Axios interceptor automatically adds token to requests
6. If token expires, interceptor refreshes automatically

### Error Handling
- API client catches errors and returns to Redux
- Components display error alerts
- Failed token refresh redirects to login

## Performance Tips

1. **Code Splitting**: Use React.lazy() for heavy pages
2. **Memoization**: Use useMemo, useCallback for expensive operations
3. **API Caching**: Implement React Query for automatic caching
4. **Images**: Optimize images before committing
5. **Bundle**: Check bundle size with `npm run build`

## Security

- Tokens stored in localStorage (consider HTTP-only cookies for production)
- CORS enabled for local development
- API client validates requests
- Protected routes check authentication
- Sensitive data not logged

## Deployment

### Vercel (Recommended for SPA)
```bash
npm run build
# Deploy dist/ folder
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Environment Variables
```
VITE_API_URL=https://api.seatserve.com
```

## Troubleshooting

### API Connection Issues
- Check backend is running on http://localhost:8000
- Verify VITE_API_URL environment variable
- Check CORS configuration in Django settings

### Token/Auth Issues
- Clear localStorage and cookies
- Check token expiration in Redux DevTools
- Verify JWT_SECRET in backend

### Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf dist`
- Update packages: `npm update`

## Contributing

- Keep components small and focused
- Use TypeScript for new components (when migrated)
- Follow existing code style
- Test API changes manually
- Document complex logic

## Next Steps

1. Implement remaining dashboard pages
2. Add form validation (Formik/React Hook Form)
3. Implement real-time updates (WebSocket)
4. Add offline support
5. Implement analytics
6. Add tests (Vitest, React Testing Library)
7. Migrate to TypeScript
8. Set up CI/CD

## License

Proprietary - SeatServe
