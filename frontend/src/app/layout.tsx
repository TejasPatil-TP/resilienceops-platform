import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { LayoutDashboard, Server, Activity, Bell, Beaker } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ResilienceOps Platform",
  description: "Platform for reliability and resilience engineering",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen bg-gray-50 text-gray-900">
          {/* Sidebar */}
          <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
            <div className="h-16 flex items-center px-6 border-b border-gray-200">
              <Activity className="w-6 h-6 text-blue-600 mr-2" />
              <span className="font-bold text-lg text-gray-900">ResilienceOps</span>
            </div>
            <nav className="flex-1 overflow-y-auto py-4">
              <ul className="space-y-1 px-3">
                <li>
                  <Link href="/" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50">
                    <LayoutDashboard className="w-5 h-5 mr-3" />
                    Overview
                  </Link>
                </li>
                <li>
                  <Link href="/services" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50">
                    <Server className="w-5 h-5 mr-3" />
                    Services
                  </Link>
                </li>
                <li>
                  <Link href="/slos" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50">
                    <Activity className="w-5 h-5 mr-3" />
                    SLOs
                  </Link>
                </li>
                <li>
                  <Link href="/alerts" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50">
                    <Bell className="w-5 h-5 mr-3" />
                    Alerts
                  </Link>
                </li>
                <li>
                  <Link href="/experiments" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50">
                    <Beaker className="w-5 h-5 mr-3" />
                    Experiments
                  </Link>
                </li>
              </ul>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 flex flex-col overflow-hidden">
            <header className="h-16 bg-white border-b border-gray-200 flex items-center px-8 shadow-sm z-10">
              <h1 className="text-xl font-semibold text-gray-800">Dashboard</h1>
            </header>
            <div className="flex-1 overflow-y-auto p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
