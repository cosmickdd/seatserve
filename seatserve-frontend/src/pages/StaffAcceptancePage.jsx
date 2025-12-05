import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../api/config';

export default function StaffAcceptancePage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [invitation, setInvitation] = useState(null);
  const [formData, setFormData] = useState({
    password: '',
    password_confirm: '',
    phone: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  // Fetch invitation details
  useEffect(() => {
    const fetchInvitation = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/restaurants/staff/accept-invitation/${token}/`
        );
        if (!response.ok) {
          if (response.status === 404) {
            setError('Invitation not found or has expired');
          } else {
            setError('Failed to load invitation');
          }
          return;
        }
        const data = await response.json();
        setInvitation(data);
      } catch (err) {
        setError('Failed to load invitation details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchInvitation();
    }
  }, [token]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.password) {
      setError('Password is required');
      return;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/restaurants/staff/accept-invitation/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            token,
            password: formData.password,
            phone: formData.phone,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || 'Failed to accept invitation');
        return;
      }

      setSuccess(true);
      setTimeout(() => {
        navigate('/auth/login');
      }, 2000);
    } catch (err) {
      setError('Failed to accept invitation');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading invitation...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !invitation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-5xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-green-600 mb-2">Welcome!</h1>
          <p className="text-gray-600 mb-4">
            Your account has been created successfully.
          </p>
          <p className="text-sm text-gray-500">
            Redirecting to login...
          </p>
        </div>
      </div>
    );
  }

  // Invitation form
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        {/* Restaurant info */}
        {invitation && (
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Welcome to {invitation.restaurant_name}!
            </h1>
            <p className="text-gray-600">
              You've been invited to join the team as a <span className="font-semibold">{invitation.role}</span>
            </p>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Invitation details */}
        {invitation && (
          <div className="bg-indigo-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Email:</span> {invitation.email}
            </p>
            {invitation.invited_by && (
              <p className="text-sm text-gray-700">
                <span className="font-semibold">Invited by:</span> {invitation.invited_by}
              </p>
            )}
          </div>
        )}

        {/* Permissions preview */}
        {invitation?.permissions && (
          <div className="mb-6">
            <h3 className="font-semibold text-gray-800 mb-3">Your Permissions</h3>
            <div className="space-y-2">
              {invitation.permissions.map((perm) => (
                <label key={perm} className="flex items-center text-sm text-gray-700">
                  <span className="text-green-600 mr-2">✓</span>
                  {perm.replace(/_/g, ' ').toUpperCase()}
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Setup form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone (Optional)
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
              placeholder="+1 (555) 000-0000"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password *
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              placeholder="Minimum 8 characters"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Must be at least 8 characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password *
            </label>
            <input
              type="password"
              value={formData.password_confirm}
              onChange={(e) =>
                setFormData({ ...formData, password_confirm: e.target.value })
              }
              placeholder="Re-enter password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 transition"
          >
            {submitting ? 'Creating Account...' : 'Accept Invitation & Create Account'}
          </button>
        </form>

        <p className="text-xs text-gray-500 text-center mt-4">
          By accepting this invitation, you agree to our Terms of Service.
        </p>
      </div>
    </div>
  );
}
