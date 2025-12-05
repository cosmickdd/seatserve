/**
 * Checkout page for order payment via Stripe
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import stripeAPI from '../api/stripe';
import ordersAPI from '../api/endpoints';
import { Button, Card, Spinner, Alert } from '../components/common';
import { Container } from '../components/layout';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');

/**
 * Checkout form component
 */
function CheckoutForm({ orderId, onSuccess, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);

  useEffect(() => {
    // Create checkout session
    const createSession = async () => {
      try {
        setLoading(true);
        const data = await stripeAPI.createCheckoutSession(orderId);
        setSessionData(data);
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to create checkout session');
        onError(err);
        setLoading(false);
      }
    };

    createSession();
  }, [orderId, onError]);

  const handleCheckout = async () => {
    if (!sessionData?.session_id) {
      setError('Session not initialized');
      return;
    }

    try {
      setLoading(true);
      const result = await stripe.redirectToCheckout({
        sessionId: sessionData.session_id,
      });

      if (result.error) {
        setError(result.error.message);
        onError(result.error);
      }
    } catch (err) {
      setError(err.message);
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-6 max-w-md">
      <h2 className="text-2xl font-bold mb-4">Secure Payment</h2>

      {error && <Alert type="error" message={error} className="mb-4" />}

      <div className="mb-6 p-4 bg-gray-50 rounded">
        <p className="text-sm text-gray-600">Processing order payment securely via Stripe</p>
      </div>

      {loading ? (
        <div className="flex justify-center">
          <Spinner />
        </div>
      ) : (
        <Button
          onClick={handleCheckout}
          disabled={!sessionData || loading}
          className="w-full"
          size="lg"
        >
          Proceed to Payment
        </Button>
      )}

      <p className="text-xs text-gray-500 text-center mt-4">
        🔒 Secure payment powered by Stripe
      </p>
    </Card>
  );
}

/**
 * Checkout page
 */
export default function CheckoutPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        setLoading(true);
        // Note: Use appropriate API endpoint for your setup
        // This assumes a public order endpoint
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    if (orderId) {
      fetchOrder();
    }
  }, [orderId]);

  const handleSuccess = () => {
    // Redirect to success page after payment
    navigate(`/order-status/${orderId}`);
  };

  const handleError = (err) => {
    console.error('Payment error:', err);
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
      <div className="max-w-2xl mx-auto py-8">
        <h1 className="text-3xl font-bold mb-8">Complete Your Order</h1>

        {error && <Alert type="error" message={error} className="mb-6" />}

        {orderId && (
          <Elements stripe={stripePromise}>
            <CheckoutForm orderId={orderId} onSuccess={handleSuccess} onError={handleError} />
          </Elements>
        )}

        <div className="mt-8 bg-blue-50 p-4 rounded border border-blue-200">
          <h3 className="font-semibold mb-2">💳 Payment Information</h3>
          <ul className="text-sm space-y-1 text-gray-700">
            <li>✓ Secure SSL encrypted payment</li>
            <li>✓ PCI DSS Level 1 compliant</li>
            <li>✓ Multiple payment methods supported</li>
            <li>✓ Instant confirmation</li>
          </ul>
        </div>
      </div>
    </Container>
  );
}
