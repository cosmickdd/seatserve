import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { API_BASE_URL } from '../api/config';

export default function EmailConfigurationPage() {
  const auth = useSelector((state) => state.auth);
  const restaurantId = auth?.restaurant?.id;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [testEmail, setTestEmail] = useState('');
  const [sendingTest, setSendingTest] = useState(false);

  const [formData, setFormData] = useState({
    email_provider: 'SMTP',
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_from_email: '',
    smtp_from_name: auth?.restaurant?.name || 'SeatServe',
    use_tls: true,
    use_ssl: false,
    send_order_confirmation: true,
    send_order_status_updates: true,
    send_invitation_emails: true,
    send_payment_receipts: true,
  });

  // Fetch email config
  useEffect(() => {
    const fetchEmailConfig = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/restaurants/${restaurantId}/email-config/`,
          {
            headers: {
              Authorization: `Bearer ${auth?.token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setFormData((prev) => ({ ...prev, ...data }));
        }
      } catch (err) {
        console.error('Failed to load email config:', err);
      } finally {
        setLoading(false);
      }
    };

    if (restaurantId && auth?.token) {
      fetchEmailConfig();
    }
  }, [restaurantId, auth?.token]);

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/restaurants/${restaurantId}/email-config/`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${auth?.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save email configuration');
      }

      setSuccess('Email configuration saved successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSendTestEmail = async () => {
    if (!testEmail) {
      setError('Please enter a test email address');
      return;
    }

    setSendingTest(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/restaurants/${restaurantId}/send-test-email/`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${auth?.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: testEmail }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to send test email');
      }

      setSuccess(`Test email sent to ${testEmail}!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingTest(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p>Loading email configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📧 Email Configuration
          </h1>
          <p className="text-gray-600">
            Configure email notifications for orders, staff invitations, and payments
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-medium">❌ {error}</p>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 mb-6">
            <p className="text-green-700 font-medium">✅ {success}</p>
          </div>
        )}

        {/* SMTP Configuration */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            SMTP Configuration
          </h2>

          <div className="space-y-6">
            {/* Provider Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Provider
              </label>
              <select
                name="email_provider"
                value={formData.email_provider}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="SMTP">Custom SMTP</option>
                <option value="SENDGRID" disabled>
                  SendGrid (Coming Soon)
                </option>
                <option value="MAILGUN" disabled>
                  Mailgun (Coming Soon)
                </option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                You can use free services like Gmail, Mailgun, or SendGrid
              </p>
            </div>

            {/* SMTP Server Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SMTP Host *
                </label>
                <input
                  type="text"
                  name="smtp_host"
                  value={formData.smtp_host}
                  onChange={handleChange}
                  placeholder="smtp.gmail.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Gmail: smtp.gmail.com | Outlook: smtp-mail.outlook.com
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SMTP Port *
                </label>
                <input
                  type="number"
                  name="smtp_port"
                  value={formData.smtp_port}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Usually 587 (TLS) or 465 (SSL)
                </p>
              </div>
            </div>

            {/* Credentials */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username/Email *
                </label>
                <input
                  type="text"
                  name="smtp_username"
                  value={formData.smtp_username}
                  onChange={handleChange}
                  placeholder="your-email@gmail.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password/App Password *
                </label>
                <input
                  type="password"
                  name="smtp_password"
                  value={formData.smtp_password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  For Gmail, use App Password
                </p>
              </div>
            </div>

            {/* From Address */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  From Email *
                </label>
                <input
                  type="email"
                  name="smtp_from_email"
                  value={formData.smtp_from_email}
                  onChange={handleChange}
                  placeholder="noreply@restaurant.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  From Name
                </label>
                <input
                  type="text"
                  name="smtp_from_name"
                  value={formData.smtp_from_name}
                  onChange={handleChange}
                  placeholder="Restaurant Name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {/* SSL/TLS Options */}
            <div className="grid grid-cols-2 gap-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="use_tls"
                  checked={formData.use_tls}
                  onChange={handleChange}
                  className="w-4 h-4 rounded border-gray-300"
                />
                <span className="ml-2 text-gray-700">Use TLS (Port 587)</span>
              </label>

              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="use_ssl"
                  checked={formData.use_ssl}
                  onChange={handleChange}
                  className="w-4 h-4 rounded border-gray-300"
                />
                <span className="ml-2 text-gray-700">Use SSL (Port 465)</span>
              </label>
            </div>
          </div>

          {/* Test Email Section */}
          <div className="mt-8 pt-8 border-t">
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              Send Test Email
            </h3>
            <div className="flex gap-2">
              <input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="test@example.com"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={handleSendTestEmail}
                disabled={sendingTest || !formData.smtp_host}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium transition"
              >
                {sendingTest ? 'Sending...' : 'Send Test'}
              </button>
            </div>
          </div>
        </div>

        {/* Email Notification Settings */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Notification Settings
          </h2>

          <div className="space-y-4">
            <label className="flex items-center cursor-pointer p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
              <input
                type="checkbox"
                name="send_order_confirmation"
                checked={formData.send_order_confirmation}
                onChange={handleChange}
                className="w-5 h-5 text-indigo-600 rounded"
              />
              <div className="ml-4 flex-1">
                <p className="font-medium text-gray-800">Order Confirmation</p>
                <p className="text-sm text-gray-600">
                  Send confirmation email when customer places order
                </p>
              </div>
            </label>

            <label className="flex items-center cursor-pointer p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
              <input
                type="checkbox"
                name="send_order_status_updates"
                checked={formData.send_order_status_updates}
                onChange={handleChange}
                className="w-5 h-5 text-indigo-600 rounded"
              />
              <div className="ml-4 flex-1">
                <p className="font-medium text-gray-800">Order Status Updates</p>
                <p className="text-sm text-gray-600">
                  Notify customer when order status changes (preparing, ready, etc.)
                </p>
              </div>
            </label>

            <label className="flex items-center cursor-pointer p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
              <input
                type="checkbox"
                name="send_invitation_emails"
                checked={formData.send_invitation_emails}
                onChange={handleChange}
                className="w-5 h-5 text-indigo-600 rounded"
              />
              <div className="ml-4 flex-1">
                <p className="font-medium text-gray-800">Staff Invitations</p>
                <p className="text-sm text-gray-600">
                  Send invitation links when inviting new staff members
                </p>
              </div>
            </label>

            <label className="flex items-center cursor-pointer p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
              <input
                type="checkbox"
                name="send_payment_receipts"
                checked={formData.send_payment_receipts}
                onChange={handleChange}
                className="w-5 h-5 text-indigo-600 rounded"
              />
              <div className="ml-4 flex-1">
                <p className="font-medium text-gray-800">Payment Receipts</p>
                <p className="text-sm text-gray-600">
                  Send receipt email after successful payment
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Email Templates (Info) */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-bold text-blue-900 mb-3">
            📧 Email Templates
          </h3>
          <p className="text-blue-800 mb-3">
            Default email templates are available for:
          </p>
          <ul className="list-disc list-inside text-blue-800 space-y-1">
            <li>Order confirmation</li>
            <li>Order status updates</li>
            <li>Staff invitation</li>
            <li>Payment receipt</li>
          </ul>
          <p className="text-sm text-blue-700 mt-3">
            Custom templates will be available in the next phase.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <button
            onClick={() => window.history.back()}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  );
}
