"use client";
import { Alert, Experiment, OverviewData, Service, SLO } from '@/types';


import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { AlertTriangle, CheckCircle, XCircle } from "lucide-react";

export default function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const overview = await api.getOverview();
        setData(overview);
      } catch (err) {
        setError("Error loading data");
      }
    }
    loadData();
  }, []);

  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!data) return <div className="p-8">Loading overview...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Platform Overview</h2>
      
      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Service Health</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-green-600">
              <CheckCircle className="w-5 h-5 mr-1" />
              <span className="font-bold text-xl">{data.serviceHealth.healthy}</span>
            </div>
            <div className="flex items-center text-yellow-600">
              <AlertTriangle className="w-5 h-5 mr-1" />
              <span className="font-bold text-xl">{data.serviceHealth.warning}</span>
            </div>
            <div className="flex items-center text-red-600">
              <XCircle className="w-5 h-5 mr-1" />
              <span className="font-bold text-xl">{data.serviceHealth.critical}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Error Budget (Global)</h3>
          <div className="flex flex-col">
            <span className="text-3xl font-bold text-gray-900">{data.errorBudget.remaining}%</span>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-3">
              <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${data.errorBudget.consumed}%` }}></div>
            </div>
            <span className="text-xs text-gray-500 mt-1">{data.errorBudget.consumed}% consumed</span>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Active Alerts</h3>
          <div className="flex items-center">
            <span className="text-3xl font-bold text-red-600">{data.activeAlerts.length}</span>
            <span className="ml-2 text-sm text-gray-500">requires attention</span>
          </div>
        </div>
      </div>

      {/* Chart & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Request Rate</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.requestRates} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 12 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Line type="monotone" dataKey="rate" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Alerts</h3>
          <div className="space-y-4">
            {data.activeAlerts.map((alert: Alert) => (
              <div key={alert.id} className="flex p-3 rounded-md bg-red-50 border border-red-100">
                <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-red-800">{alert.message}</h4>
                  <p className="text-xs text-red-600 mt-1">{alert.service} • {alert.time}</p>
                </div>
              </div>
            ))}
            {data.activeAlerts.length === 0 && (
              <p className="text-sm text-gray-500">No active alerts.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
