'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, ShieldAlert, Activity, Globe } from 'lucide-react';
import RecentScans from "../components/RecentScans";
import { VulnerabilityStatsCard, PrivacyStatsCard } from '../components/StatsCard';
import Layout from "../components/Layout";
import ProtectedRoute from "../components/ProtectedRoute";

const mockScans = [
  {
    id: '1',
    target: {
      name: 'Example Website',
      url: 'https://example.com',
    },
    status: 'completed' as const,
    startedAt: '2024-03-20T10:00:00Z',
    completedAt: '2024-03-20T10:05:00Z',
    stats: {
      vulnerabilities: {
        critical: 2,
        high: 5,
        medium: 8,
        low: 12,
        info: 15,
        total: 42,
      },
      privacyIssues: {
        high: 3,
        medium: 6,
        low: 9,
        total: 18,
      },
      dependencies: {
        total: 156,
      },
    },
  },
];

const Dashboard = () => {
  const totalStats = mockScans
    .filter(scan => scan.status === 'completed')
    .reduce(
      (acc, scan) => {
        return {
          vulnerabilities: {
            critical: acc.vulnerabilities.critical + scan.stats.vulnerabilities.critical,
            high: acc.vulnerabilities.high + scan.stats.vulnerabilities.high,
            medium: acc.vulnerabilities.medium + scan.stats.vulnerabilities.medium,
            low: acc.vulnerabilities.low + scan.stats.vulnerabilities.low,
            info: acc.vulnerabilities.info + scan.stats.vulnerabilities.info,
          },
          privacyIssues: {
            high: acc.privacyIssues.high + scan.stats.privacyIssues.high,
            medium: acc.privacyIssues.medium + scan.stats.privacyIssues.medium,
            low: acc.privacyIssues.low + scan.stats.privacyIssues.low,
          },
        };
      },
      {
        vulnerabilities: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
        privacyIssues: { high: 0, medium: 0, low: 0 },
      }
    );

  const recentCompletedScan = mockScans.find(scan => scan.status === 'completed');

  return (
    <ProtectedRoute>
      <Layout>
        <div>
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-extrabold text-white drop-shadow-lg animate-fade-in">
                Security Dashboard
              </h1>
              <p className="text-[#cbd5e1] mt-1 animate-fade-in-slow">
                Monitor and manage your security scanning activities
              </p>
            </div>
            <Link
              href="/scan"
              className="px-5 py-2 bg-gradient-to-r from-[#0284c7] to-[#38bdf8] text-white rounded-lg shadow-lg hover:from-[#0369a1] hover:to-[#0ea5e9] transition-all duration-200 flex items-center gap-2"
            >
              New Scan <ArrowRight size={18} />
            </Link>
          </div>
          
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gradient-to-br from-[#0c4a6e] via-[#0369a1] to-[#075985] rounded-2xl border border-[#0369a1]/60 p-6 shadow-xl hover:scale-105 hover:shadow-2xl transition-transform duration-300 animate-fade-in">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-white/10 rounded-lg animate-pulse">
                  <ShieldAlert size={24} className="text-[#bae6fd]" />
                </div>
                <h2 className="text-xl font-semibold text-[#e0f2fe]">AI-Powered Security</h2>
              </div>
              <p className="text-[#bae6fd] text-sm mb-4">
                Scan for vulnerabilities using advanced AI models that can detect potential security risks.
              </p>
              <Link href="/scan" className="text-[#bae6fd] hover:text-[#e0f2fe] text-sm font-medium flex items-center">
                Start scanning <ArrowRight size={14} className="ml-1" />
              </Link>
            </div>
            
            <div className="bg-gradient-to-br from-[#7c2d12] via-[#c2410c] to-[#9a3412] rounded-2xl border border-[#c2410c]/60 p-6 shadow-xl hover:scale-105 hover:shadow-2xl transition-transform duration-300 animate-fade-in">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-white/10 rounded-lg animate-pulse">
                  <Activity size={24} className="text-[#fed7aa]" />
                </div>
                <h2 className="text-xl font-semibold text-[#ffedd5]">Privacy Analysis</h2>
              </div>
              <p className="text-[#fed7aa] text-sm mb-4">
                Detect trackers, cookies, and potential GDPR/CCPA compliance issues with privacy analysis.
              </p>
              <Link href="/scan" className="text-[#fed7aa] hover:text-[#ffedd5] text-sm font-medium flex items-center">
                Check privacy <ArrowRight size={14} className="ml-1" />
              </Link>
            </div>
            
            <div className="bg-gradient-to-br from-[#134e4a] via-[#0f766e] to-[#115e59] rounded-2xl border border-[#0f766e]/60 p-6 shadow-xl hover:scale-105 hover:shadow-2xl transition-transform duration-300 animate-fade-in">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-white/10 rounded-lg animate-pulse">
                  <Globe size={24} className="text-[#99f6e4]" />
                </div>
                <h2 className="text-xl font-semibold text-[#ccfbf1]">Supply Chain Security</h2>
              </div>
              <p className="text-[#99f6e4] text-sm mb-4">
                Analyze dependencies for vulnerabilities and security risks in your supply chain.
              </p>
              <Link href="/scan" className="text-[#99f6e4] hover:text-[#ccfbf1] text-sm font-medium flex items-center">
                Analyze dependencies <ArrowRight size={14} className="ml-1" />
              </Link>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <RecentScans scans={mockScans} />
              
              {recentCompletedScan && (
                <div className="bg-[#1e293b] rounded-lg border border-[#334155] overflow-hidden">
                  <div className="p-4 border-b border-[#334155]">
                    <h2 className="text-[#f1f5f9] font-medium">Recent Scan Overview</h2>
                    <p className="text-[#94a3b8] text-sm">
                      {recentCompletedScan.target.name} - {recentCompletedScan.target.url}
                    </p>
                  </div>
                  
                  <div className="p-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                      <div className="bg-[#334155]/50 p-3 rounded-md">
                        <div className="flex items-center justify-between">
                          <span className="text-[#94a3b8] text-sm">Vulnerabilities</span>
                          <span className="text-[#f87171] font-medium text-lg">
                            {recentCompletedScan.stats.vulnerabilities.total}
                          </span>
                        </div>
                      </div>
                      
                      <div className="bg-[#334155]/50 p-3 rounded-md">
                        <div className="flex items-center justify-between">
                          <span className="text-[#94a3b8] text-sm">Privacy Issues</span>
                          <span className="text-[#fb923c] font-medium text-lg">
                            {recentCompletedScan.stats.privacyIssues.total}
                          </span>
                        </div>
                      </div>
                      
                      <div className="bg-[#334155]/50 p-3 rounded-md">
                        <div className="flex items-center justify-between">
                          <span className="text-[#94a3b8] text-sm">Dependencies</span>
                          <span className="text-[#2dd4bf] font-medium text-lg">
                            {recentCompletedScan.stats.dependencies.total}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <Link 
                      href={`/results/${recentCompletedScan.id}`}
                      className="text-[#38bdf8] hover:text-[#7dd3fc] text-sm font-medium flex items-center"
                    >
                      View complete results <ArrowRight size={14} className="ml-1" />
                    </Link>
                  </div>
                </div>
              )}
            </div>
            
            <div className="space-y-8">
              <VulnerabilityStatsCard 
                critical={totalStats.vulnerabilities.critical}
                high={totalStats.vulnerabilities.high}
                medium={totalStats.vulnerabilities.medium}
                low={totalStats.vulnerabilities.low}
                info={totalStats.vulnerabilities.info}
              />
              
              <PrivacyStatsCard 
                high={totalStats.privacyIssues.high}
                medium={totalStats.privacyIssues.medium}
                low={totalStats.privacyIssues.low}
              />
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default Dashboard;