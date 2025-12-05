import apiClient from './client';

// Auth API
export const authAPI = {
  register: (email, firstName, lastName, password, passwordConfirm) =>
    apiClient.post('/auth/register/create/', {
      email,
      first_name: firstName,
      last_name: lastName,
      password,
      password_confirm: passwordConfirm,
    }),

  login: (email, password) =>
    apiClient.post('/auth/auth/login/', { email, password }),

  refreshToken: (refresh) =>
    apiClient.post('/auth/auth/refresh/', { refresh }),

  getProfile: () =>
    apiClient.get('/auth/profile/me/'),

  updateProfile: (data) =>
    apiClient.put('/auth/profile/update_profile/', data),
};

// Plans API
export const plansAPI = {
  list: () =>
    apiClient.get('/restaurants/plans/'),
};

// Restaurants API
export const restaurantsAPI = {
  getMe: () =>
    apiClient.get('/restaurants/me/'),

  create: (name, email, phone, city, country, address) =>
    apiClient.post('/restaurants/me/create_restaurant/', {
      name,
      email,
      phone,
      city,
      country,
      address,
    }),

  update: (data) =>
    apiClient.put('/restaurants/me/update_me/', data),
};

// Subscriptions API
export const subscriptionsAPI = {
  getCurrent: () =>
    apiClient.get('/restaurants/subscriptions/my_subscription/'),

  getHistory: () =>
    apiClient.get('/restaurants/subscriptions/subscription_history/'),

  selectPlan: (planId) =>
    apiClient.post('/restaurants/subscriptions/select_plan/', { plan_id: planId }),
};

// Tables API
export const tablesAPI = {
  list: () =>
    apiClient.get('/restaurants/tables/'),

  create: (name, capacity) =>
    apiClient.post('/restaurants/tables/', { name, capacity }),

  update: (id, data) =>
    apiClient.patch(`/restaurants/tables/${id}/`, data),

  delete: (id) =>
    apiClient.delete(`/restaurants/tables/${id}/`),

  getQRCode: (id) =>
    apiClient.get(`/restaurants/tables/${id}/qr_code/`),

  getStats: () =>
    apiClient.get('/restaurants/tables/stats/'),
};

// Menu Categories API
export const categoriesAPI = {
  list: () =>
    apiClient.get('/menu/categories/'),

  create: (name, sortOrder) =>
    apiClient.post('/menu/categories/', { name, sort_order: sortOrder }),

  update: (id, data) =>
    apiClient.patch(`/menu/categories/${id}/`, data),

  delete: (id) =>
    apiClient.delete(`/menu/categories/${id}/`),
};

// Menu Items API
export const menuItemsAPI = {
  list: () =>
    apiClient.get('/menu/items/'),

  create: (categoryId, name, description, price, imageUrl, tags, isAvailable) =>
    apiClient.post('/menu/items/', {
      category: categoryId,
      name,
      description,
      price,
      image_url: imageUrl,
      tags,
      is_available: isAvailable,
    }),

  update: (id, data) =>
    apiClient.patch(`/menu/items/${id}/`, data),

  delete: (id) =>
    apiClient.delete(`/menu/items/${id}/`),

  getByCategory: () =>
    apiClient.get('/menu/items/by_category/'),

  getStats: () =>
    apiClient.get('/menu/items/stats/'),
};

// Orders API (Restaurant)
export const ordersAPI = {
  list: () =>
    apiClient.get('/orders/'),

  getToday: () =>
    apiClient.get('/orders/today/'),

  getPending: () =>
    apiClient.get('/orders/pending/'),

  getDetails: (id) =>
    apiClient.get(`/orders/${id}/`),

  updateStatus: (id, status) =>
    apiClient.patch(`/orders/${id}/update_status/`, { status }),

  getStats: () =>
    apiClient.get('/orders/stats/'),
};

// Public API (Customer)
export const publicAPI = {
  getMenu: (restaurantPublicId, tableToken) =>
    apiClient.get(`/public/restaurant/${restaurantPublicId}/table/${tableToken}/menu/`),

  createOrder: (restaurantPublicId, tableToken, items, customerNote) =>
    apiClient.post(`/public/restaurant/${restaurantPublicId}/table/${tableToken}/orders/`, {
      items,
      customer_note: customerNote,
    }),

  getOrderStatus: (orderToken) =>
    apiClient.get(`/public/order/${orderToken}/`),
};
