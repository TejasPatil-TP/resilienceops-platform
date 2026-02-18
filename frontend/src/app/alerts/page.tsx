"use client";
import { Alert, Experiment, OverviewData, Service, SLO } from '@/types';


import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AlertTriangle, Clock } from "lucide-react"; 

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getAlerts();
        setAlerts(data);
      } catch (err) {
        setError("Error loading data");
      }
    }
    loadData();
  }, []);

  if (error) return <div className="p-8 text-red-600">{error}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Active Alerts</h2>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
        <ul className="divide-y divide-gray-200">
          {alerts.map((alert) => (
            <li key={alert.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <AlertTriangle className={`h-6 w-6 ${alert.severity === 'critical' ? 'text-red-600' : 'text-yellow-600'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {alert.message}
                  </p>
                  <p className="text-sm text-gray-500 truncate">
                    {alert.service}
                  </p>
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Clock className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                  <p>{alert.time}</p>
                </div>
                <div>
                  <button className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50">
                    Acknowledge
                  </button>
                </div>
              </div>
            </li>
          ))}
          {alerts.length === 0 && (
            <li className="p-8 text-center text-gray-500">
              No active alerts. Everything looks good!
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
