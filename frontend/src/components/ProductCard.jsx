import { Link } from 'react-router-dom';
import { ExternalLink, RefreshCw, Trash2, TrendingDown, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useDeleteProduct, useForceScrape, useUpdateProduct } from '../hooks/useProducts';

export default function ProductCard({ product }) {
  const deleteMutation = useDeleteProduct();
  const scrapeMutation = useForceScrape();
  const updateMutation = useUpdateProduct();

  const hasValidPrice = product.current_price !== null && product.current_price !== undefined;
  const isPriceDropped = hasValidPrice && product.target_price && product.current_price <= product.target_price;

  const handleDelete = (e) => {
    e.preventDefault();
    if (window.confirm('Are you sure you want to delete this product?')) {
      deleteMutation.mutate(product.id);
    }
  };

  const handleRefresh = (e) => {
    e.preventDefault();
    scrapeMutation.mutate(product.id);
  };

  const toggleActive = (e) => {
    e.preventDefault();
    updateMutation.mutate({
      id: product.id,
      data: { is_active: !product.is_active }
    });
  };

  return (
    <Link to={`/product/${product.id}`} className="block group">
      <div className={`bg-slate-800 rounded-xl border transition-all duration-200 overflow-hidden flex flex-col h-full
        ${isPriceDropped ? 'border-green-500/50 hover:border-green-400' : 'border-slate-700 hover:border-slate-500'}
        ${!product.is_active ? 'opacity-60 grayscale-[50%]' : ''}`}
      >
        <div className="relative h-48 bg-slate-900 p-4 flex items-center justify-center overflow-hidden">
          {product.image_url ? (
            <img 
              src={product.image_url} 
              alt={product.title || 'Product'} 
              className="max-h-full object-contain group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="text-slate-500">No Image</div>
          )}
          <div className="absolute top-2 right-2 flex space-x-1">
            <span className="px-2 py-1 bg-slate-800/80 backdrop-blur text-xs rounded-full font-medium border border-slate-600">
              {product.site || 'Unknown'}
            </span>
          </div>
          {isPriceDropped && (
            <div className="absolute top-2 left-2 flex items-center space-x-1 px-2 py-1 bg-green-500/90 text-white text-xs rounded-full font-bold shadow-lg">
              <TrendingDown className="h-3 w-3" />
              <span>Target Reached</span>
            </div>
          )}
        </div>

        <div className="p-4 flex-1 flex flex-col">
          <h3 className="font-semibold text-slate-100 line-clamp-2 mb-2 flex-1" title={product.title}>
            {product.title || product.url}
          </h3>
          
          <div className="mt-auto space-y-3">
            <div className="flex justify-between items-end">
              <div>
                <p className="text-xs text-slate-400 mb-1">Current Price</p>
                <div className="text-xl font-bold text-white">
                  {hasValidPrice ? (
                    `₹${product.current_price.toLocaleString('en-IN')}`
                  ) : (
                    <span className="text-sm font-normal text-slate-400 italic">Waiting for scrape...</span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400 mb-1">Target Price</p>
                <p className="text-sm font-medium text-slate-300">
                  {product.target_price ? `₹${product.target_price.toLocaleString('en-IN')}` : 'Not set'}
                </p>
              </div>
            </div>

            <div className="flex items-center text-xs text-slate-400 space-x-1">
              <Clock className="h-3 w-3" />
              <span>
                {product.last_checked 
                  ? `Checked ${formatDistanceToNow(new Date(product.last_checked))} ago` 
                  : 'Never checked'}
              </span>
            </div>
            
            <div className="flex items-center justify-between pt-3 border-t border-slate-700">
              <div className="flex space-x-2">
                <button 
                  onClick={handleRefresh}
                  disabled={scrapeMutation.isPending}
                  className="p-1.5 text-slate-400 hover:text-blue-400 hover:bg-slate-700 rounded-md transition-colors"
                  title="Force Refresh"
                >
                  <RefreshCw className={`h-4 w-4 ${scrapeMutation.isPending ? 'animate-spin' : ''}`} />
                </button>
                <a 
                  href={product.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 text-slate-400 hover:text-blue-400 hover:bg-slate-700 rounded-md transition-colors"
                  title="Open Link"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={toggleActive}
                  className={`text-xs px-2 py-1 rounded border transition-colors ${
                    product.is_active 
                      ? 'border-slate-600 text-slate-300 hover:bg-slate-700' 
                      : 'border-blue-500/50 text-blue-400 bg-blue-500/10'
                  }`}
                >
                  {product.is_active ? 'Pause' : 'Resume'}
                </button>
                <button 
                  onClick={handleDelete}
                  className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded-md transition-colors"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
