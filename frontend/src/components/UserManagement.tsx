'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UserGroupIcon,
  UserPlusIcon,
  PencilIcon,
  TrashIcon,
  ShieldCheckIcon,
  EyeIcon,
  EyeSlashIcon,
  KeyIcon,
  EnvelopeIcon,
  PhoneIcon,
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { formatDate, formatRelativeTime } from '@/lib/utils'

interface User {
  id: string
  firstName: string
  lastName: string
  email: string
  phone?: string
  role: string
  department: string
  status: 'active' | 'inactive' | 'pending' | 'suspended'
  lastLogin: string
  createdAt: string
  permissions: string[]
  avatar?: string
  twoFactorEnabled: boolean
  loginAttempts: number
  lastPasswordChange: string
}

interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  userCount: number
  isSystem: boolean
}

const PERMISSIONS = [
  { id: 'portfolio.view', name: 'View Portfolio', category: 'Portfolio' },
  { id: 'portfolio.edit', name: 'Edit Portfolio', category: 'Portfolio' },
  { id: 'risk.view', name: 'View Risk Data', category: 'Risk Management' },
  { id: 'risk.calculate', name: 'Calculate Risk', category: 'Risk Management' },
  { id: 'compliance.view', name: 'View Compliance Reports', category: 'Compliance' },
  { id: 'compliance.generate', name: 'Generate Reports', category: 'Compliance' },
  { id: 'audit.view', name: 'View Audit Trail', category: 'Security' },
  { id: 'audit.export', name: 'Export Audit Data', category: 'Security' },
  { id: 'users.view', name: 'View Users', category: 'Administration' },
  { id: 'users.manage', name: 'Manage Users', category: 'Administration' },
  { id: 'system.configure', name: 'System Configuration', category: 'Administration' },
  { id: 'ai.interact', name: 'AI Assistant Access', category: 'AI Features' }
]

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [showUserModal, setShowUserModal] = useState(false)
  const [showRoleModal, setShowRoleModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'permissions'>('users')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterRole, setFilterRole] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  useEffect(() => {
    // Mock data
    const mockUsers: User[] = [
      {
        id: '1',
        firstName: 'Sarah',
        lastName: 'Chen',
        email: 'sarah.chen@globaltech.com',
        phone: '+1 (555) 123-4567',
        role: 'Treasury Manager',
        department: 'Treasury',
        status: 'active',
        lastLogin: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        createdAt: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
        permissions: ['portfolio.view', 'portfolio.edit', 'risk.view', 'risk.calculate', 'ai.interact'],
        twoFactorEnabled: true,
        loginAttempts: 0,
        lastPasswordChange: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '2',
        firstName: 'Michael',
        lastName: 'Rodriguez',
        email: 'michael.rodriguez@globaltech.com',
        phone: '+1 (555) 234-5678',
        role: 'Risk Analyst',
        department: 'Risk Management',
        status: 'active',
        lastLogin: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        createdAt: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(),
        permissions: ['portfolio.view', 'risk.view', 'risk.calculate', 'compliance.view'],
        twoFactorEnabled: true,
        loginAttempts: 0,
        lastPasswordChange: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '3',
        firstName: 'Emily',
        lastName: 'Johnson',
        email: 'emily.johnson@globaltech.com',
        role: 'System Administrator',
        department: 'IT',
        status: 'active',
        lastLogin: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
        permissions: ['users.view', 'users.manage', 'system.configure', 'audit.view', 'audit.export'],
        twoFactorEnabled: true,
        loginAttempts: 0,
        lastPasswordChange: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '4',
        firstName: 'David',
        lastName: 'Kim',
        email: 'david.kim@globaltech.com',
        role: 'Compliance Officer',
        department: 'Compliance',
        status: 'active',
        lastLogin: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
        permissions: ['compliance.view', 'compliance.generate', 'audit.view', 'portfolio.view'],
        twoFactorEnabled: false,
        loginAttempts: 0,
        lastPasswordChange: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '5',
        firstName: 'Lisa',
        lastName: 'Wang',
        email: 'lisa.wang@globaltech.com',
        role: 'Analyst',
        department: 'Treasury',
        status: 'pending',
        lastLogin: new Date(0).toISOString(),
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        permissions: ['portfolio.view'],
        twoFactorEnabled: false,
        loginAttempts: 0,
        lastPasswordChange: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      }
    ]

    const mockRoles: Role[] = [
      {
        id: 'treasury_manager',
        name: 'Treasury Manager',
        description: 'Full access to treasury operations and portfolio management',
        permissions: ['portfolio.view', 'portfolio.edit', 'risk.view', 'risk.calculate', 'ai.interact'],
        userCount: 1,
        isSystem: false
      },
      {
        id: 'risk_analyst',
        name: 'Risk Analyst',
        description: 'Risk analysis and monitoring capabilities',
        permissions: ['portfolio.view', 'risk.view', 'risk.calculate', 'compliance.view'],
        userCount: 1,
        isSystem: false
      },
      {
        id: 'compliance_officer',
        name: 'Compliance Officer',
        description: 'Compliance reporting and audit access',
        permissions: ['compliance.view', 'compliance.generate', 'audit.view', 'portfolio.view'],
        userCount: 1,
        isSystem: false
      },
      {
        id: 'system_admin',
        name: 'System Administrator',
        description: 'Full system administration privileges',
        permissions: ['users.view', 'users.manage', 'system.configure', 'audit.view', 'audit.export'],
        userCount: 1,
        isSystem: true
      },
      {
        id: 'analyst',
        name: 'Analyst',
        description: 'Read-only access to portfolio data',
        permissions: ['portfolio.view'],
        userCount: 1,
        isSystem: false
      }
    ]

    setUsers(mockUsers)
    setRoles(mockRoles)
  }, [])

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesRole = filterRole === 'all' || user.role === filterRole
    const matchesStatus = filterStatus === 'all' || user.status === filterStatus
    
    return matchesSearch && matchesRole && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'inactive':
        return 'text-gray-600 bg-gray-50 border-gray-200'
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'suspended':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-4 w-4" />
      case 'suspended':
        return <XCircleIcon className="h-4 w-4" />
      case 'pending':
        return <ExclamationTriangleIcon className="h-4 w-4" />
      default:
        return <XCircleIcon className="h-4 w-4" />
    }
  }

  const renderUsersTab = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Roles</option>
            {roles.map(role => (
              <option key={role.id} value={role.name}>{role.name}</option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
            <option value="suspended">Suspended</option>
          </select>
          <button
            onClick={() => {
              setSelectedUser(null)
              setShowUserModal(true)
            }}
            className="btn-primary"
          >
            <UserPlusIcon className="h-4 w-4 mr-2" />
            Add User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role & Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Security
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <motion.tr
                  key={user.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-medium">
                        {user.firstName[0]}{user.lastName[0]}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.firstName} {user.lastName}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{user.role}</div>
                    <div className="text-sm text-gray-500">{user.department}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(user.status)}`}>
                      {getStatusIcon(user.status)}
                      <span className="ml-1 capitalize">{user.status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.lastLogin === new Date(0).toISOString() ? 'Never' : formatRelativeTime(user.lastLogin)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {user.twoFactorEnabled ? (
                        <ShieldCheckIcon className="h-4 w-4 text-green-500" title="2FA Enabled" />
                      ) : (
                        <ShieldCheckIcon className="h-4 w-4 text-gray-300" title="2FA Disabled" />
                      )}
                      {user.loginAttempts > 0 && (
                        <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" title={`${user.loginAttempts} failed attempts`} />
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => {
                          setSelectedUser(user)
                          setShowUserModal(true)
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderRolesTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Role Management</h3>
          <p className="text-sm text-gray-600">Define roles and permissions for users</p>
        </div>
        <button
          onClick={() => {
            setSelectedRole(null)
            setShowRoleModal(true)
          }}
          className="btn-primary"
        >
          <UserPlusIcon className="h-4 w-4 mr-2" />
          Create Role
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {roles.map((role) => (
          <motion.div
            key={role.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="text-lg font-medium text-gray-900">{role.name}</h4>
                <p className="text-sm text-gray-600 mt-1">{role.description}</p>
              </div>
              {role.isSystem && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  System
                </span>
              )}
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Users:</span>
                <span className="font-medium text-gray-900">{role.userCount}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Permissions:</span>
                <span className="font-medium text-gray-900">{role.permissions.length}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => {
                    setSelectedRole(role)
                    setShowRoleModal(true)
                  }}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Edit Role
                </button>
                {!role.isSystem && (
                  <button className="text-red-600 hover:text-red-800 text-sm font-medium">
                    Delete
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )

  const renderPermissionsTab = () => {
    const permissionsByCategory = PERMISSIONS.reduce((acc, permission) => {
      if (!acc[permission.category]) {
        acc[permission.category] = []
      }
      acc[permission.category].push(permission)
      return acc
    }, {} as Record<string, typeof PERMISSIONS>)

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900">System Permissions</h3>
          <p className="text-sm text-gray-600">Available permissions that can be assigned to roles</p>
        </div>

        {Object.entries(permissionsByCategory).map(([category, permissions]) => (
          <div key={category} className="bg-white rounded-lg border border-gray-200 p-6">
            <h4 className="text-md font-medium text-gray-900 mb-4">{category}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {permissions.map((permission) => (
                <div key={permission.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <KeyIcon className="h-4 w-4 text-gray-400 mr-3" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{permission.name}</div>
                    <div className="text-xs text-gray-500">{permission.id}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
          <p className="text-gray-600 mt-1">Manage users, roles, and permissions</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-sm text-gray-600">
            {users.filter(u => u.status === 'active').length} active users
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'users', name: 'Users', icon: UserGroupIcon },
            { id: 'roles', name: 'Roles', icon: ShieldCheckIcon },
            { id: 'permissions', name: 'Permissions', icon: KeyIcon }
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'users' && renderUsersTab()}
          {activeTab === 'roles' && renderRolesTab()}
          {activeTab === 'permissions' && renderPermissionsTab()}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}