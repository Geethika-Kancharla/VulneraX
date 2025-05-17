import React from 'react';
import { AlertTriangle, Shield, Info } from 'lucide-react';

interface VulnerabilityStatsProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

interface PrivacyStatsProps {
  high: number;
  medium: number;
  low: number;
}

export const VulnerabilityStatsCard: React.FC<VulnerabilityStatsProps> = ({
  critical,
  high,
  medium,
  low,
  info,
}) => {
  return (
    <div className="bg-dark-800 rounded-lg border border-dark-700 p-4">
      <h3 className="text-lg font-medium text-dark-50 mb-4">Vulnerability Statistics</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-error-500" />
            <span className="text-dark-300">Critical</span>
          </div>
          <span className="text-error-400 font-medium">{critical}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-orange-500" />
            <span className="text-dark-300">High</span>
          </div>
          <span className="text-orange-400 font-medium">{high}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-yellow-500" />
            <span className="text-dark-300">Medium</span>
          </div>
          <span className="text-yellow-400 font-medium">{medium}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield size={16} className="text-blue-500" />
            <span className="text-dark-300">Low</span>
          </div>
          <span className="text-blue-400 font-medium">{low}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Info size={16} className="text-gray-500" />
            <span className="text-dark-300">Info</span>
          </div>
          <span className="text-gray-400 font-medium">{info}</span>
        </div>
      </div>
    </div>
  );
};

export const PrivacyStatsCard: React.FC<PrivacyStatsProps> = ({
  high,
  medium,
  low,
}) => {
  return (
    <div className="bg-dark-800 rounded-lg border border-dark-700 p-4">
      <h3 className="text-lg font-medium text-dark-50 mb-4">Privacy Issues</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-error-500" />
            <span className="text-dark-300">High Risk</span>
          </div>
          <span className="text-error-400 font-medium">{high}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-yellow-500" />
            <span className="text-dark-300">Medium Risk</span>
          </div>
          <span className="text-yellow-400 font-medium">{medium}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield size={16} className="text-blue-500" />
            <span className="text-dark-300">Low Risk</span>
          </div>
          <span className="text-blue-400 font-medium">{low}</span>
        </div>
      </div>
    </div>
  );
}; 