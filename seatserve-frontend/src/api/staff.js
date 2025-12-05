/**
 * Staff management API integration
 */
import client from './client';

export const staffAPI = {
  /**
   * Get all staff members for restaurant
   * @returns {Promise} Staff members with summary
   */
  listStaff: async () => {
    const response = await client.get('/api/restaurants/staff/');
    return response.data;
  },

  /**
   * Get staff member by ID
   * @param {number} staffId - Staff member ID
   * @returns {Promise} Staff member details
   */
  getStaff: async (staffId) => {
    const response = await client.get(`/api/restaurants/staff/${staffId}/`);
    return response.data;
  },

  /**
   * Invite new staff member
   * @param {object} data - Staff data (name, email, role, permissions)
   * @returns {Promise} Created staff member
   */
  inviteStaff: async (data) => {
    const response = await client.post('/api/restaurants/staff/', data);
    return response.data;
  },

  /**
   * Update staff member permissions and role
   * @param {number} staffId - Staff member ID
   * @param {object} data - Updated staff data
   * @returns {Promise} Updated staff member
   */
  updateStaff: async (staffId, data) => {
    const response = await client.patch(`/api/restaurants/staff/${staffId}/`, data);
    return response.data;
  },

  /**
   * Resend invitation email
   * @param {number} staffId - Staff member ID
   * @returns {Promise} Response confirmation
   */
  resendInvitation: async (staffId) => {
    const response = await client.post(`/api/restaurants/staff/${staffId}/resend_invitation/`);
    return response.data;
  },

  /**
   * Suspend staff member
   * @param {number} staffId - Staff member ID
   * @returns {Promise} Updated staff member
   */
  suspendStaff: async (staffId) => {
    const response = await client.post(`/api/restaurants/staff/${staffId}/suspend/`);
    return response.data;
  },

  /**
   * Activate staff member
   * @param {number} staffId - Staff member ID
   * @returns {Promise} Updated staff member
   */
  activateStaff: async (staffId) => {
    const response = await client.post(`/api/restaurants/staff/${staffId}/activate/`);
    return response.data;
  },

  /**
   * Remove staff member
   * @param {number} staffId - Staff member ID
   * @returns {Promise} Deletion confirmation
   */
  removeStaff: async (staffId) => {
    const response = await client.delete(`/api/restaurants/staff/${staffId}/`);
    return response.data;
  },

  /**
   * Get staff grouped by role
   * @returns {Promise} Staff members grouped by role
   */
  getStaffByRole: async () => {
    const response = await client.get('/api/restaurants/staff/by_role/');
    return response.data;
  },
};

export default staffAPI;
