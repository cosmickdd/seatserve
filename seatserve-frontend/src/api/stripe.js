/**
 * Stripe payment integration
 */
import client from './client';

export const stripeAPI = {
  /**
   * Create Stripe checkout session
   * @param {number} orderId - Order ID to create payment for
   * @returns {Promise} Session data with session_id and stripe_publishable_key
   */
  createCheckoutSession: async (orderId) => {
    const response = await client.post('/api/payments/create_checkout/', {
      order_id: orderId,
    });
    return response.data;
  },

  /**
   * Confirm payment after checkout
   * @param {string} sessionId - Stripe checkout session ID
   * @returns {Promise} Payment confirmation data
   */
  confirmPayment: async (sessionId) => {
    const response = await client.post('/api/payments/confirm_payment/', {
      session_id: sessionId,
    });
    return response.data;
  },

  /**
   * Get payment details
   * @param {number} paymentId - Payment ID
   * @returns {Promise} Payment object
   */
  getPayment: async (paymentId) => {
    const response = await client.get(`/api/payments/${paymentId}/`);
    return response.data;
  },

  /**
   * Get today's payments summary
   * @returns {Promise} List of payments with summary
   */
  getTodayPayments: async () => {
    const response = await client.get('/api/payments/today/');
    return response.data;
  },

  /**
   * Refund a payment
   * @param {number} paymentId - Payment ID
   * @param {number} amount - Optional refund amount
   * @param {string} reason - Refund reason
   * @returns {Promise} Refund confirmation
   */
  refundPayment: async (paymentId, amount = null, reason = 'Customer requested') => {
    const response = await client.post(`/api/payments/${paymentId}/refund/`, {
      amount,
      reason,
    });
    return response.data;
  },

  /**
   * Get restaurant's payment history
   * @returns {Promise} List of all payments
   */
  getPaymentHistory: async () => {
    const response = await client.get('/api/payments/');
    return response.data;
  },
};

export default stripeAPI;
