import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Loader2, TrendingDown, Clock, Bell } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { useProduct } from '../hooks/useProducts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800 border border-slate-700 p-3 rounded-lg shadow-xl">
        <p className="text-slate-300 text-xs mb-1">{format(new Date(label), 'MMM d, yyyy HH:mm')}</p>
        <p className="text-white font-bold text-lg">
          ₹{payload[0].value.toLocaleString('en-IN')}
        </p>
      </div>
    );
  }
  return null;
};

export default function ProductDetails() {
  const { id } = useParams();
  const { data: product, isLoading, isError } = useProduct(id);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="text-center py-20 text-red-400">
        <p>Failed to load product details.</p>
        <Link to="/" className="text-blue-500 hover:underline mt-4 inline-block">Back to Dashboard</Link>
      </div>
    );
  }

  // Format data for Recharts
  const chartData = [...(product.history || [])]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .map(h => ({
      ...h,
      timestamp: parseISO(h.timestamp).getTime(), // Convert to timestamp for better x-axis scaling if needed
      dateStr: h.timestamp // raw string for tooltip
    }));

  const hasValidPrice = product.current_price !== null && product.current_price !== undefined;
  const lowestPrice = chartData.length > 0 ? Math.min(...chartData.map(d => d.price)) : product.current_price;
  const isTargetReached = hasValidPrice && product.target_price && product.current_price <= product.target_price;

  return (
    <div className="space-y-6">
      <Link to="/" className="inline-flex items-center text-sm text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Dashboard
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Details */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 shadow-sm flex flex-col items-center text-center">
            <div className="w-full h-48 bg-slate-900 rounded-lg flex items-center justify-center p-4 mb-6 border border-slate-700/50">
              {product.image_url ? (
                <img 
                  src={product.image_url} 
                  alt={product.title} 
                  className="max-h-full object-contain"
                />
              ) : (
                <span className="text-slate-500">No Image</span>
              )}
            </div>
            
            <h1 className="text-xl font-bold text-white mb-2 line-clamp-3">{product.title || 'Unknown Product'}</h1>
            <span className="px-3 py-1 bg-slate-700 text-slate-300 text-xs rounded-full font-medium mb-6">
              {product.site}
            </span>

            <div className="w-full space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Current Price</span>
                <span className="text-2xl font-bold text-white">
                  {hasValidPrice ? `₹${product.current_price.toLocaleString('en-IN')}` : <span className="text-sm font-normal text-slate-400 italic">Waiting for scrape...</span>}
                </span>
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Lowest Recorded</span>
                <span className="text-lg font-medium text-green-400">
                  {lowestPrice !== null && lowestPrice !== undefined ? `₹${lowestPrice.toLocaleString('en-IN')}` : <span className="text-sm font-normal text-slate-400 italic">Waiting for scrape...</span>}
                </span>
              </div>

              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Target Price</span>
                <span className="text-lg font-medium text-slate-200">
                  {product.target_price ? `₹${product.target_price.toLocaleString('en-IN')}` : 'Not set'}
                </span>
              </div>

              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Alert Config</span>
                <span className="text-sm font-medium text-slate-300 flex items-center">
                  <Bell className="h-3 w-3 mr-1" />
                  Drop by {product.alert_threshold_type === 'percentage' 
                    ? `${product.alert_threshold_value}%` 
                    : `₹${product.alert_threshold_value}`}
                </span>
              </div>
            </div>

            <a 
              href={product.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="mt-6 w-full flex items-center justify-center px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-lg transition-colors"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              View on Store
            </a>
          </div>
        </div>

        {/* Right Column: Chart */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-white">Price History</h2>
              <div className="flex items-center text-xs text-slate-400">
                <Clock className="h-3.5 w-3.5 mr-1" />
                Last checked: {product.last_checked ? format(new Date(product.last_checked), 'PP p') : 'Never'}
              </div>
            </div>
            
            {chartData.length > 0 ? (
              <div className="h-[400px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis 
                      dataKey="timestamp" 
                      stroke="#94a3b8" 
                      fontSize={12}
                      tickFormatter={(unixTime) => format(new Date(unixTime), 'MMM d')}
                      minTickGap={30}
                    />
                    <YAxis 
                      stroke="#94a3b8" 
                      fontSize={12}
                      tickFormatter={(value) => `₹${value}`}
                      domain={['auto', 'auto']}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    
                    {product.target_price && (
                      <ReferenceLine 
                        y={product.target_price} 
                        label={{ position: 'top', value: 'Target', fill: '#fbbf24', fontSize: 12 }} 
                        stroke="#fbbf24" 
                        strokeDasharray="3 3" 
                      />
                    )}
                    
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#3b82f6" 
                      strokeWidth={3}
                      dot={{ r: 3, fill: '#3b82f6', strokeWidth: 2, stroke: '#1e293b' }}
                      activeDot={{ r: 6, fill: '#60a5fa', strokeWidth: 0 }}
                      animationDuration={1000}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[400px] flex items-center justify-center border-2 border-dashed border-slate-700 rounded-xl">
                <p className="text-slate-400">Not enough history data yet.</p>
              </div>
            )}
          </div>

          {isTargetReached && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 flex items-start space-x-4">
              <div className="p-3 bg-green-500/20 rounded-full">
                <TrendingDown className="h-6 w-6 text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-green-400">Target Price Reached!</h3>
                <p className="text-green-400/80 mt-1">
                  This product is currently available at or below your target price of ₹{product.target_price.toLocaleString('en-IN')}.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
