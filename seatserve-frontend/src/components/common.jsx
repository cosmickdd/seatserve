import React from 'react';
import classNames from 'classnames';

export const Card = ({ children, className = '' }) => (
  <div className={classNames('bg-white rounded-lg shadow-md p-6', className)}>
    {children}
  </div>
);

export const Button = ({
  children,
  onClick,
  className = '',
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  type = 'button',
}) => {
  const baseStyles = 'font-semibold rounded-lg transition-colors duration-200 flex items-center justify-center gap-2';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-400',
    success: 'bg-green-600 text-white hover:bg-green-700 disabled:bg-green-400',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 disabled:border-blue-400',
  };

  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={classNames(baseStyles, variants[variant], sizes[size], className)}
    >
      {loading && <span className="animate-spin">⏳</span>}
      {children}
    </button>
  );
};

export const Input = ({
  label,
  type = 'text',
  placeholder = '',
  value,
  onChange,
  error = '',
  required = false,
  className = '',
}) => (
  <div className="w-full">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-600 ml-1">*</span>}
      </label>
    )}
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={classNames(
        'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        error && 'border-red-500',
        className
      )}
    />
    {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
  </div>
);

export const Select = ({
  label,
  options = [],
  value,
  onChange,
  error = '',
  required = false,
  className = '',
}) => (
  <div className="w-full">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-600 ml-1">*</span>}
      </label>
    )}
    <select
      value={value}
      onChange={onChange}
      className={classNames(
        'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        error && 'border-red-500',
        className
      )}
    >
      <option value="">Select...</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
  </div>
);

export const Badge = ({ children, variant = 'primary', className = '' }) => {
  const variants = {
    primary: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    gray: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={classNames('px-3 py-1 rounded-full text-sm font-medium', variants[variant], className)}>
      {children}
    </span>
  );
};

export const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={classNames('bg-white rounded-lg shadow-lg p-6 w-full', sizes[size])}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export const Spinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={classNames('animate-spin rounded-full border-4 border-gray-200 border-t-blue-600', sizes[size])}>
    </div>
  );
};

export const Alert = ({ type = 'info', title, message, onClose }) => {
  const colors = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  };

  return (
    <div className={classNames('border rounded-lg p-4 flex justify-between items-start', colors[type])}>
      <div>
        {title && <h3 className="font-semibold">{title}</h3>}
        {message && <p className="text-sm">{message}</p>}
      </div>
      {onClose && (
        <button onClick={onClose} className="ml-2 font-bold">
          ✕
        </button>
      )}
    </div>
  );
};

export const EmptyState = ({ icon, title, message, action }) => (
  <div className="text-center py-12">
    <div className="text-6xl mb-4">{icon}</div>
    <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-500 mb-6">{message}</p>
    {action}
  </div>
);
