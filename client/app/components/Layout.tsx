import React, { ReactNode, useState } from 'react';
import { 
  Shield, 
  Home, 
  Search, 
  FileDigit, 
  Settings, 
  Menu, 
  X,
  ShieldCheck,
  Github,
  LogOut
} from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { signOut } from 'firebase/auth';
import { auth } from '../../Firebase';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <Home size={20} /> },
    { path: '/scan', label: 'New Scan', icon: <Search size={20} /> },
    { path: '/results/latest', label: 'Results', icon: <FileDigit size={20} /> }
  ];

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      router.push('/login');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-[#f8fafc]">
      {/* Mobile Header */}
      <header className="md:hidden bg-[#020617] border-b border-[#1e293b] p-4 flex justify-between items-center">
        <div className="flex items-center">
          <ShieldCheck className="text-[#0ea5e9] mr-2" size={24} />
          <span className="font-bold text-lg">SecureScan AI</span>
        </div>
        <button 
          onClick={toggleMenu}
          className="p-2 rounded-md hover:bg-[#1e293b] text-[#38bdf8] hover:text-[#7dd3fc] transition-colors"
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      <div className="flex h-screen">
        {/* Sidebar - Desktop */}
        <aside className="hidden md:flex flex-col w-64 bg-[#0f172a] border-r border-[#1e293b]">
          <div className="p-4 border-b border-[#1e293b] flex items-center">
            <Shield className="text-[#0ea5e9] mr-2" size={24} />
            <h1 className="font-bold text-xl">SecureScan AI</h1>
          </div>
          
          <nav className="flex-1 py-4">
            <ul>
              {navItems.map((item) => (
                <li key={item.path}>
                  <Link
                    href={item.path}
                    className={`flex items-center px-4 py-3 ${
                      pathname === item.path 
                        ? 'bg-[#082f49] text-[#7dd3fc] border-l-2 border-[#0ea5e9]'
                        : 'text-[#cbd5e1] hover:bg-[#1e293b] hover:text-[#38bdf8]'
                    } transition-colors`}
                  >
                    <span className={`mr-3 ${pathname === item.path ? 'text-[#38bdf8]' : 'text-[#94a3b8]'}`}>
                      {item.icon}
                    </span>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          {/* Logout Button */}
          <div className="p-4 border-t border-[#1e293b]">
            <button
              onClick={handleLogout}
              className="w-full flex items-center px-4 py-3 text-[#cbd5e1] hover:bg-[#1e293b] hover:text-[#38bdf8] transition-colors rounded-md"
            >
              <LogOut size={20} className="mr-3 text-[#94a3b8]" />
              Logout
            </button>
          </div>
        </aside>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden absolute top-16 left-0 right-0 bg-[#0f172a] border-b border-[#1e293b] z-50 shadow-lg">
            <nav>
              <ul>
                {navItems.map((item) => (
                  <li key={item.path}>
                    <Link
                      href={item.path}
                      className={`flex items-center px-4 py-3 ${
                        pathname === item.path 
                          ? 'bg-[#082f49] text-[#7dd3fc] border-l-2 border-[#0ea5e9]'
                          : 'text-[#cbd5e1] hover:bg-[#1e293b] hover:text-[#38bdf8]'
                      } transition-colors`}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      <span className={`mr-3 ${pathname === item.path ? 'text-[#38bdf8]' : 'text-[#94a3b8]'}`}>
                        {item.icon}
                      </span>
                      {item.label}
                    </Link>
                  </li>
                ))}
                <li>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center px-4 py-3 text-[#cbd5e1] hover:bg-[#1e293b] hover:text-[#38bdf8] transition-colors"
                  >
                    <LogOut size={20} className="mr-3 text-[#94a3b8]" />
                    Logout
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto bg-[#020617]">
          <div className="container mx-auto p-4 md:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;