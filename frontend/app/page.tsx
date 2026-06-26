'use client'

import { useState, useEffect } from 'react'
import { 
  Search, 
  Plus, 
  Users, 
  Building2, 
  Package, 
  BarChart3,
  Settings,
  Bell,
  User,
  Menu,
  Home,
  Scan,
  CreditCard,
  FolderTree,
  FileText,
  Calendar,
  MessageSquare,
  Zap
} from 'lucide-react'

export default function Home() {
  const [mounted, setMounted] = useState(false)
  const [stats, setStats] = useState({
    contacts: 0,
    companies: 0,
    products: 0,
    cardsScanned: 0
  })

  useEffect(() => {
    setMounted(true)
    // Fetch stats from API
    fetch('/api/v1/system/info')
      .then(res => res.json())
      .then(data => {
        console.log('System info:', data)
      })
      .catch(err => console.error('Error fetching system info:', err))
  }, [])

  if (!mounted) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading AKAVIN OS...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-blue-600">AKAVIN OS</h1>
          <p className="text-sm text-gray-500">v1.0.0</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          <NavItem icon={Home} label="Dashboard" active />
          <NavItem icon={Scan} label="Scan Card" />
          <NavItem icon={Users} label="Contacts" />
          <NavItem icon={Building2} label="Companies" />
          <NavItem icon={Package} label="Products" />
          <NavItem icon={FolderTree} label="Catalogs" />
          <NavItem icon={FileText} label="Documents" />
          <NavItem icon={Calendar} label="Calendar" />
          <NavItem icon={MessageSquare} label="Messages" />
          <NavItem icon={BarChart3} label="Analytics" />
          <NavItem icon={Settings} label="Settings" />
        </nav>
        
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium">Admin User</p>
              <p className="text-xs text-gray-500">admin@akavin.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4 flex-1">
            <button className="lg:hidden">
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search contacts, companies, products..."
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button className="relative">
              <Bell className="w-5 h-5 text-gray-600" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                3
              </span>
            </button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New</span>
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <StatCard
              icon={Users}
              label="Contacts"
              value={stats.contacts}
              color="blue"
            />
            <StatCard
              icon={Building2}
              label="Companies"
              value={stats.companies}
              color="green"
            />
            <StatCard
              icon={Package}
              label="Products"
              value={stats.products}
              color="purple"
            />
            <StatCard
              icon={Scan}
              label="Cards Scanned"
              value={stats.cardsScanned}
              color="orange"
            />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Zap className="w-5 h-5 text-yellow-500 mr-2" />
                Quick Actions
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <ActionButton icon={Scan} label="Scan Card" />
                <ActionButton icon={Users} label="Add Contact" />
                <ActionButton icon={Building2} label="Add Company" />
                <ActionButton icon={Package} label="Add Product" />
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <CreditCard className="w-5 h-5 text-green-500 mr-2" />
                Recent Activity
              </h3>
              <div className="space-y-3">
                <ActivityItem
                  icon={Scan}
                  text="Scanned John Smith's business card"
                  time="2 min ago"
                />
                <ActivityItem
                  icon={Users}
                  text="Added new contact: Sarah Johnson"
                  time="15 min ago"
                />
                <ActivityItem
                  icon={Building2}
                  text="Created company: ABC Technologies"
                  time="1 hour ago"
                />
                <ActivityItem
                  icon={Package}
                  text="Added product: LED Panel 300W"
                  time="3 hours ago"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Components
function NavItem({ icon: Icon, label, active = false }: any) {
  return (
    <button className={`
      w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition
      ${active 
        ? 'bg-blue-50 text-blue-600' 
        : 'text-gray-600 hover:bg-gray-100'
      }
    `}>
      <Icon className="w-4 h-4" />
      <span className="text-sm">{label}</span>
    </button>
  )
}

function StatCard({ icon: Icon, label, value, color }: any) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  }
  
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <div className={`w-10 h-10 rounded-lg ${colors[color]} flex items-center justify-center`}>
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-2xl font-bold">{value || 0}</span>
      </div>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  )
}

function ActionButton({ icon: Icon, label }: any) {
  return (
    <button className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
      <Icon className="w-4 h-4 text-blue-600" />
      <span className="text-sm">{label}</span>
    </button>
  )
}

function ActivityItem({ icon: Icon, text, time }: any) {
  return (
    <div className="flex items-start space-x-3">
      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-gray-600" />
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-800">{text}</p>
        <p className="text-xs text-gray-400">{time}</p>
      </div>
    </div>
  )
}
