import React from 'react';
import { Shield, Menu } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={onToggle}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded-md"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Sidebar */}
      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-40
          w-64 bg-gray-800 text-white transform transition-transform duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-8">
            <Shield className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-lg font-semibold">Fraud Detection</h1>
              <p className="text-sm text-gray-400">Pipeline</p>
            </div>
          </div>

          <nav className="space-y-4">
            <a
              href="#"
              className="flex items-center space-x-3 px-3 py-2 rounded-md bg-blue-600 text-white"
            >
              <span>Dashboard</span>
            </a>
            <a
              href="#"
              className="flex items-center space-x-3 px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700"
            >
              <span>Transactions</span>
            </a>
            <a
              href="#"
              className="flex items-center space-x-3 px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700"
            >
              <span>Analytics</span>
            </a>
            <a
              href="#"
              className="flex items-center space-x-3 px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700"
            >
              <span>Settings</span>
            </a>
          </nav>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={onToggle}
        />
      )}
    </>
  );
};

export default Sidebar;