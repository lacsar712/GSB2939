// 菜单配置
export const menuRoutes = [
  {
    path: '/dashboard',
    meta: { title: '工作台', icon: 'HomeFilled' }
  },
  {
    path: '/sample',
    meta: { title: '样品管理', icon: 'Box' },
    children: [
      { path: 'register', meta: { title: '样品登记', icon: 'DocumentAdd' } },
      { path: 'list', meta: { title: '样品列表', icon: 'List' } },
      { path: 'storage', meta: { title: '样品存储', icon: 'Grid' } }
    ]
  },
  {
    path: '/task',
    meta: { title: '任务管理', icon: 'Tickets' },
    children: [
      { path: 'list', meta: { title: '任务列表', icon: 'List' } },
      { path: 'assign', meta: { title: '任务分配', icon: 'Connection' } },
      { path: 'method', meta: { title: '标准方法', icon: 'Document' } }
    ]
  },
  {
    path: '/data',
    meta: { title: '数据管理', icon: 'DataAnalysis' },
    children: [
      { path: 'input', meta: { title: '数据录入', icon: 'Edit' } },
      { path: 'record', meta: { title: '原始记录', icon: 'Tickets' } },
      { path: 'trace', meta: { title: '数据溯源', icon: 'Share' } },
      { path: 'dilution', meta: { title: '稀释计算器', icon: 'Calculator' } }
    ]
  },
  {
    path: '/resource',
    meta: { title: '资源管理', icon: 'Grid' },
    children: [
      { path: 'reagent', meta: { title: '试剂管理', icon: 'FirstAidKit' } },
      { path: 'equipment', meta: { title: '设备管理', icon: 'Monitor' } },
      { path: 'consumable', meta: { title: '耗材管理', icon: 'Box' } }
    ]
  },
  {
    path: '/report',
    meta: { title: '报告管理', icon: 'Document' },
    children: [
      { path: 'list', meta: { title: '报告列表', icon: 'List' } },
      { path: 'template', meta: { title: '报告模板', icon: 'Files' } }
    ]
  },
  {
    path: '/quality',
    meta: { title: '质量合规', icon: 'Medal' },
    children: [
      { path: 'audit', meta: { title: '审计追踪', icon: 'View' } },
      { path: 'permission', meta: { title: '权限管理', icon: 'Lock' } }
    ]
  },
  {
    path: '/system',
    meta: { title: '系统设置', icon: 'Setting' },
    children: [
      { path: 'users', meta: { title: '用户管理', icon: 'User' } },
      { path: 'role', meta: { title: '角色管理', icon: 'UserFilled' } }
    ]
  }
]
