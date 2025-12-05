/**
 * Staff management page
 */
import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { staffAPI } from '../api/staff';
import { Button, Card, Input, Select, Badge, Modal, Alert, Spinner, EmptyState } from '../components/common';
import { Container } from '../components/layout';

const STAFF_ROLES = [
  { value: 'MANAGER', label: 'Manager' },
  { value: 'CHEF', label: 'Chef' },
  { value: 'WAITER', label: 'Waiter' },
  { value: 'CASHIER', label: 'Cashier' },
  { value: 'DELIVERY', label: 'Delivery Executive' },
];

const STATUS_COLORS = {
  ACTIVE: 'success',
  INACTIVE: 'warning',
  SUSPENDED: 'error',
};

/**
 * Invite Staff Modal
 */
function InviteStaffModal({ isOpen, onClose, onInvite, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    role: 'WAITER',
    can_view_orders: true,
    can_update_orders: false,
    can_view_menu: true,
    can_edit_menu: false,
    can_view_tables: true,
    can_edit_tables: false,
    can_view_analytics: false,
    can_manage_staff: false,
  });
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      await onInvite(formData);
      setFormData({
        name: '',
        email: '',
        phone: '',
        role: 'WAITER',
        can_view_orders: true,
        can_update_orders: false,
        can_view_menu: true,
        can_edit_menu: false,
        can_view_tables: true,
        can_edit_tables: false,
        can_view_analytics: false,
        can_manage_staff: false,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to invite staff');
    }
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Invite Staff Member">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert type="error" message={error} />}

        <Input
          label="Name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="John Doe"
          required
        />

        <Input
          label="Email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="john@example.com"
          required
        />

        <Input
          label="Phone"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          placeholder="+1 (555) 000-0000"
        />

        <Select
          label="Role"
          name="role"
          value={formData.role}
          onChange={handleChange}
          options={STAFF_ROLES}
        />

        <div className="border-t pt-4">
          <h3 className="font-semibold mb-3">Permissions</h3>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="can_view_orders"
                checked={formData.can_view_orders}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Can View Orders</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                name="can_update_orders"
                checked={formData.can_update_orders}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Can Update Order Status</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                name="can_view_menu"
                checked={formData.can_view_menu}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Can View Menu</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                name="can_edit_menu"
                checked={formData.can_edit_menu}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Can Edit Menu</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                name="can_view_analytics"
                checked={formData.can_view_analytics}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Can View Analytics</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                name="can_manage_staff"
                checked={formData.can_manage_staff}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Can Manage Staff</span>
            </label>
          </div>
        </div>

        <div className="flex gap-2 pt-4">
          <Button type="submit" disabled={loading}>
            {loading ? 'Inviting...' : 'Send Invitation'}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </form>
    </Modal>
  );
}

/**
 * Staff list item
 */
function StaffListItem({ staff, onUpdate, onResendInvitation, onSuspend, onActivate, onRemove }) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold">{staff.name}</h3>
            <Badge color={STATUS_COLORS[staff.status]}>{staff.status}</Badge>
            {staff.is_invited && <Badge color="info">Pending Acceptance</Badge>}
          </div>
          <p className="text-sm text-gray-600 mb-1">{staff.email}</p>
          {staff.phone && <p className="text-sm text-gray-600 mb-1">{staff.phone}</p>}
          <p className="text-sm font-medium text-blue-600">{staff.role_display}</p>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 hover:bg-gray-100 rounded"
          >
            ⋮
          </button>

          {showMenu && (
            <div className="absolute right-0 top-10 bg-white border rounded shadow-lg z-10 min-w-[200px]">
              {staff.is_invited && (
                <button
                  onClick={() => {
                    onResendInvitation(staff.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
                >
                  Resend Invitation
                </button>
              )}

              <button
                onClick={() => {
                  setShowMenu(false);
                  // Open edit modal
                }}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
              >
                Edit Permissions
              </button>

              {staff.status === 'ACTIVE' && (
                <button
                  onClick={() => {
                    onSuspend(staff.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-orange-600"
                >
                  Suspend
                </button>
              )}

              {staff.status === 'SUSPENDED' && (
                <button
                  onClick={() => {
                    onActivate(staff.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-green-600"
                >
                  Activate
                </button>
              )}

              <button
                onClick={() => {
                  if (confirm('Are you sure? This cannot be undone.')) {
                    onRemove(staff.id);
                    setShowMenu(false);
                  }
                }}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-red-600 border-t"
              >
                Remove
              </button>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

/**
 * Staff management page component
 */
export default function StaffPage() {
  const { isAuthenticated } = useSelector((state) => state.auth);
  const [staff, setStaff] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [invitationLoading, setInvitationLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchStaff = async () => {
      try {
        setLoading(true);
        const data = await staffAPI.listStaff();
        setStaff(data.staff_members || []);
        setSummary(data.summary || {});
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load staff');
        setLoading(false);
      }
    };

    fetchStaff();
  }, [isAuthenticated]);

  const handleInviteStaff = async (formData) => {
    try {
      setInvitationLoading(true);
      const newStaff = await staffAPI.inviteStaff(formData);
      setStaff((prev) => [newStaff, ...prev]);
      setSummary((prev) => ({
        ...prev,
        total: (prev.total || 0) + 1,
        pending_invitations: (prev.pending_invitations || 0) + 1,
      }));
      setShowInviteModal(false);
      setInvitationLoading(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to invite staff');
      setInvitationLoading(false);
      throw err;
    }
  };

  const handleResendInvitation = async (staffId) => {
    try {
      await staffAPI.resendInvitation(staffId);
      alert('Invitation resent successfully');
      // Refresh list
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resend invitation');
    }
  };

  const handleSuspendStaff = async (staffId) => {
    try {
      const updated = await staffAPI.suspendStaff(staffId);
      setStaff((prev) =>
        prev.map((s) => (s.id === staffId ? { ...s, status: 'SUSPENDED' } : s))
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to suspend staff');
    }
  };

  const handleActivateStaff = async (staffId) => {
    try {
      const updated = await staffAPI.activateStaff(staffId);
      setStaff((prev) =>
        prev.map((s) => (s.id === staffId ? { ...s, status: 'ACTIVE' } : s))
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to activate staff');
    }
  };

  const handleRemoveStaff = async (staffId) => {
    try {
      await staffAPI.removeStaff(staffId);
      setStaff((prev) => prev.filter((s) => s.id !== staffId));
      setSummary((prev) => ({
        ...prev,
        total: Math.max(0, (prev.total || 0) - 1),
      }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove staff');
    }
  };

  if (loading) {
    return (
      <Container>
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <div className="py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Staff Management</h1>
          <Button onClick={() => setShowInviteModal(true)}>+ Invite Staff Member</Button>
        </div>

        {error && <Alert type="error" message={error} className="mb-6" />}

        {/* Summary cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">{summary.total || 0}</div>
            <div className="text-sm text-gray-600">Total Staff</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-green-600">{summary.active || 0}</div>
            <div className="text-sm text-gray-600">Active</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-yellow-600">{summary.inactive || 0}</div>
            <div className="text-sm text-gray-600">Inactive</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-orange-600">{summary.pending_invitations || 0}</div>
            <div className="text-sm text-gray-600">Pending Invitations</div>
          </Card>
        </div>

        {/* Staff list */}
        {staff.length === 0 ? (
          <EmptyState
            title="No staff members"
            description="Start by inviting your first staff member"
            icon="👥"
          />
        ) : (
          <div className="space-y-4">
            {staff.map((s) => (
              <StaffListItem
                key={s.id}
                staff={s}
                onUpdate={() => {}}
                onResendInvitation={handleResendInvitation}
                onSuspend={handleSuspendStaff}
                onActivate={handleActivateStaff}
                onRemove={handleRemoveStaff}
              />
            ))}
          </div>
        )}

        {/* Invite modal */}
        <InviteStaffModal
          isOpen={showInviteModal}
          onClose={() => setShowInviteModal(false)}
          onInvite={handleInviteStaff}
          loading={invitationLoading}
        />
      </div>
    </Container>
  );
}
