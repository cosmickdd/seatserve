import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authAPI } from '../api/endpoints';

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      // ✅ SECURE: Tokens are stored in HTTP-only cookies by backend
      const response = await authAPI.login(email, password);
      // Store user info in Redux (not sensitive data)
      sessionStorage.setItem('user', JSON.stringify(response.data.user));
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Login failed');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async ({ email, firstName, lastName, password, passwordConfirm }, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(email, firstName, lastName, password, passwordConfirm);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Registration failed');
    }
  }
);

export const getProfile = createAsyncThunk(
  'auth/getProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getProfile();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch profile');
    }
  }
);

const initialState = {
  user: sessionStorage.getItem('user') ? JSON.parse(sessionStorage.getItem('user')) : null,
  // ✅ SECURE: Check if cookies exist (backend will handle verification)
  isAuthenticated: document.cookie.includes('access_token'),
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      // ✅ SECURE: Cookies are cleared automatically by backend on logout
      sessionStorage.removeItem('user');
      state.user = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        sessionStorage.setItem('user', JSON.stringify(action.payload.user));
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
      })
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(getProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(getProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        sessionStorage.setItem('user', JSON.stringify(action.payload));
      })
      .addCase(getProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
