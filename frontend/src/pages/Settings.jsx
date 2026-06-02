import { useState, useEffect } from 'react';
import { Save, Loader2, CheckCircle2 } from 'lucide-react';
import { useSettings, useUpdateSettings } from '../hooks/useSettings';

export default function Settings() {
  const { data: settings, isLoading } = useSettings();
  const updateMutation = useUpdateSettings();

  const [webhookUrl, setWebhookUrl] = useState('');
  const [retentionDays, setRetentionDays] = useState(30);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (settings) {
      setWebhookUrl(settings.discord_webhook_url || '');
      setRetentionDays(settings.history_retention_days || 30);
    }
  }, [settings]);

  const handleSubmit = (e) => {
    e.preventDefault();
    updateMutation.mutate({
      discord_webhook_url: webhookUrl,
      history_retention_days: parseInt(retentionDays, 10)
    }, {
      onSuccess: () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Settings</h1>
        <p className="text-slate-400 text-sm mt-1">Configure global application preferences.</p>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-sm overflow-hidden">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          <div className="space-y-4">
            <h2 className="text-lg font-medium text-white border-b border-slate-700 pb-2">Notifications</h2>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">
                Discord Webhook URL
              </label>
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://discord.com/api/webhooks/..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
              />
              <p className="text-xs text-slate-500 mt-2">
                Create a webhook in your Discord server settings and paste the URL here to receive price drop alerts.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-medium text-white border-b border-slate-700 pb-2">Data Management</h2>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">
                History Retention (Days)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={retentionDays}
                onChange={(e) => setRetentionDays(e.target.value)}
                className="w-full sm:w-1/3 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow"
              />
              <p className="text-xs text-slate-500 mt-2">
                Price history older than this number of days will be automatically deleted to save space.
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-700 flex items-center justify-between">
            <div>
              {saved && (
                <span className="flex items-center text-green-400 text-sm font-medium animate-in fade-in">
                  <CheckCircle2 className="h-4 w-4 mr-1.5" />
                  Settings saved
                </span>
              )}
            </div>
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="inline-flex items-center px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
            >
              {updateMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
