import { useState } from 'react';
import { Plus, AlertCircle, Loader2 } from 'lucide-react';
import { useProducts, useAddProduct } from '../hooks/useProducts';
import ProductCard from '../components/ProductCard';

export default function Dashboard() {
  const { data: products, isLoading, isError } = useProducts();
  const addMutation = useAddProduct();
  
  const [isAdding, setIsAdding] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [alertType, setAlertType] = useState('fixed');
  const [alertValue, setAlertValue] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleAddSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    
    if (!newUrl) {
      setErrorMsg('URL is required');
      return;
    }

    addMutation.mutate({
      url: newUrl,
      target_price: targetPrice ? parseFloat(targetPrice) : null,
      alert_threshold_type: alertType,
      alert_threshold_value: alertValue ? parseFloat(alertValue) : 0,
      is_active: true
    }, {
      onSuccess: () => {
        setIsAdding(false);
        setNewUrl('');
        setTargetPrice('');
        setAlertValue('');
      },
      onError: (err) => {
        setErrorMsg(err.response?.data?.detail || 'Failed to add product');
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Tracked Products</h1>
          <p className="text-slate-400 text-sm mt-1">Monitor prices from Amazon, Flipkart, and Croma.</p>
        </div>
        <button
          onClick={() => setIsAdding(!isAdding)}
          className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Product
        </button>
      </div>

      {isAdding && (
        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700 shadow-lg animate-in fade-in slide-in-from-top-4 duration-200">
          <h2 className="text-lg font-medium text-white mb-4">Add New Product</h2>
          <form onSubmit={handleAddSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Product URL</label>
              <input
                type="url"
                required
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://www.amazon.in/..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Target Price (₹) <span className="text-slate-500 font-normal">(Optional)</span></label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  placeholder="e.g. 5000"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Alert Threshold Type</label>
                <select
                  value={alertType}
                  onChange={(e) => setAlertType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
                >
                  <option value="fixed">Fixed Drop Amount (₹)</option>
                  <option value="percentage">Percentage Drop (%)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Alert Threshold Value</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={alertValue}
                  onChange={(e) => setAlertValue(e.target.value)}
                  placeholder={alertType === 'fixed' ? 'e.g. 500' : 'e.g. 10'}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
                />
              </div>
            </div>

            {errorMsg && (
              <div className="flex items-center space-x-2 text-red-400 text-sm bg-red-400/10 p-3 rounded-lg border border-red-400/20">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={addMutation.isPending}
                className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
              >
                {addMutation.isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Save Product
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p>Loading products...</p>
        </div>
      ) : isError ? (
        <div className="text-center py-20 text-red-400 bg-red-400/10 rounded-xl border border-red-400/20">
          <AlertCircle className="h-8 w-8 mx-auto mb-2" />
          <p>Failed to load products. Is the backend running?</p>
        </div>
      ) : products?.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed border-slate-700 rounded-xl bg-slate-800/50">
          <p className="text-slate-400 mb-4">No products tracked yet.</p>
          <button
            onClick={() => setIsAdding(true)}
            className="text-blue-400 hover:text-blue-300 font-medium"
          >
            Add your first product
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
