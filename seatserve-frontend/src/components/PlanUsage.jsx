/**
 * Plan usage and limits display component
 */
import { useEffect, useState } from 'react';
import { Card, Badge, Button } from './common';
import restaurantAPI from '../api/endpoints';

export function PlanUsageCard({ restaurant }) {
  const [planInfo, setPlanInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlanInfo = async () => {
      try {
        setLoading(true);
        // Get plan info from stats endpoints
        const tableStats = await restaurantAPI.tableStats?.();
        if (tableStats?.plan) {
          setPlanInfo(tableStats.plan);
        }
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch plan info:', err);
        setLoading(false);
      }
    };

    if (restaurant) {
      fetchPlanInfo();
    }
  }, [restaurant]);

  if (loading || !planInfo) {
    return null;
  }

  const { plan, status, tables_used, tables_available, menu_items_used, menu_items_available, usage_percent } = planInfo;

  if (!plan) {
    return (
      <Card className="p-6 bg-gradient-to-r from-orange-50 to-red-50 border-2 border-orange-300">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-bold text-lg mb-2">⚠️ No Active Subscription</h3>
            <p className="text-sm text-gray-700 mb-4">
              You don't have an active subscription. Please upgrade to use SeatServe.
            </p>
          </div>
          <Button href="/subscription" size="sm">
            Choose Plan
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h3 className="font-bold text-lg">{plan.name} Plan</h3>
          <p className="text-sm text-gray-600">${plan.price}/{plan.billing_period.toLowerCase()}</p>
        </div>
        <Badge color="success">Active</Badge>
      </div>

      {/* Tables usage */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-semibold">Tables</label>
          <span className="text-sm text-gray-600">
            {tables_used} / {tables_available}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              usage_percent.tables >= 80 ? 'bg-red-500' : usage_percent.tables >= 60 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(100, usage_percent.tables)}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">{usage_percent.tables}% used</p>
      </div>

      {/* Menu items usage */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-semibold">Menu Items</label>
          <span className="text-sm text-gray-600">
            {menu_items_used} / {menu_items_available}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              usage_percent.menu_items >= 80 ? 'bg-red-500' : usage_percent.menu_items >= 60 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(100, usage_percent.menu_items)}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">{usage_percent.menu_items}% used</p>
      </div>

      {/* Features */}
      {plan.features && Object.keys(plan.features).length > 0 && (
        <div className="mb-4 pt-4 border-t">
          <h4 className="text-sm font-semibold mb-2">Features</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(plan.features).map(([feature, enabled]) => (
              <div key={feature} className="text-sm">
                {enabled ? '✓' : '✗'} {feature.replace(/_/g, ' ')}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warning if usage high */}
      {(usage_percent.tables >= 80 || usage_percent.menu_items >= 80) && (
        <div className="bg-orange-100 border border-orange-300 text-orange-800 p-3 rounded mt-4 text-sm">
          <strong>⚠️ Approaching Limits:</strong> You're nearing your plan limits. Consider upgrading your plan.
        </div>
      )}

      {/* Upgrade button if at limits */}
      {(tables_used >= tables_available || menu_items_used >= menu_items_available) && (
        <Button href="/subscription" variant="primary" className="w-full mt-4">
          Upgrade Plan
        </Button>
      )}
    </Card>
  );
}

/**
 * Plan limit warning component (for dashboard or list pages)
 */
export function PlanLimitWarning({ resource, used, available }) {
  if (used < available) return null;

  return (
    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-2xl">🚫</span>
        </div>
        <div className="ml-3">
          <h3 className="font-semibold text-red-800 text-sm">Plan Limit Reached</h3>
          <p className="text-red-700 text-sm mt-1">
            You've reached the maximum number of {resource} for your plan. Upgrade to add more.
          </p>
          <Button href="/subscription" size="sm" className="mt-2">
            Upgrade Plan
          </Button>
        </div>
      </div>
    </div>
  );
}

export default PlanUsageCard;
