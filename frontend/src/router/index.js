import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/components/common/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', icon: 'HomeFilled' }
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/system/Profile.vue'),
        meta: { title: '个人中心', hidden: true }
      },
      // 样品管理
      {
        path: 'sample',
        name: 'SampleManage',
        redirect: '/sample/list',
        meta: { title: '样品管理', icon: 'Box' },
        children: [
          {
            path: 'register',
            name: 'SampleRegister',
            component: () => import('@/views/sample/Register.vue'),
            meta: { title: '样品登记', icon: 'DocumentAdd' }
          },
          {
            path: 'list',
            name: 'SampleList',
            component: () => import('@/views/sample/List.vue'),
            meta: { title: '样品列表', icon: 'List' }
          },
          {
            path: 'storage',
            name: 'SampleStorage',
            component: () => import('@/views/sample/Storage.vue'),
            meta: { title: '样品存储', icon: 'Grid' }
          },
          {
            path: 'detail/:id',
            name: 'SampleDetail',
            component: () => import('@/views/sample/Detail.vue'),
            meta: { title: '样品详情', hidden: true }
          }
        ]
      },
      // 任务管理
      {
        path: 'task',
        name: 'TaskManage',
        redirect: '/task/list',
        meta: { title: '任务管理', icon: 'Tickets' },
        children: [
          {
            path: 'list',
            name: 'TaskList',
            component: () => import('@/views/task/List.vue'),
            meta: { title: '任务列表', icon: 'List' }
          },
          {
            path: 'assign',
            name: 'TaskAssign',
            component: () => import('@/views/task/Assign.vue'),
            meta: { title: '任务分配', icon: 'Connection' }
          },
          {
            path: 'method',
            name: 'StandardMethod',
            component: () => import('@/views/task/Method.vue'),
            meta: { title: '标准方法', icon: 'Document' }
          },
          {
            path: 'detail/:id',
            name: 'TaskDetail',
            component: () => import('@/views/task/Detail.vue'),
            meta: { title: '任务详情', hidden: true }
          }
        ]
      },
      // 数据管理
      {
        path: 'data',
        name: 'DataManage',
        redirect: '/data/input',
        meta: { title: '数据管理', icon: 'DataAnalysis' },
        children: [
          {
            path: 'input',
            name: 'DataInput',
            component: () => import('@/views/data/Input.vue'),
            meta: { title: '数据录入', icon: 'Edit' }
          },
          {
            path: 'record',
            name: 'OriginalRecord',
            component: () => import('@/views/data/Record.vue'),
            meta: { title: '原始记录', icon: 'Tickets' }
          },
          {
            path: 'trace',
            name: 'DataTrace',
            component: () => import('@/views/data/Trace.vue'),
            meta: { title: '数据溯源', icon: 'Share' }
          },
          {
            path: 'dilution-calculator',
            name: 'DilutionCalculator',
            component: () => import('@/views/data/DilutionCalculator.vue'),
            meta: { title: '稀释倍数计算器', icon: 'Calculator' }
          }
        ]
      },
      // 资源管理
      {
        path: 'resource',
        name: 'ResourceManage',
        redirect: '/resource/reagent',
        meta: { title: '资源管理', icon: 'Grid' },
        children: [
          {
            path: 'reagent',
            name: 'ReagentList',
            component: () => import('@/views/resource/Reagent.vue'),
            meta: { title: '试剂管理', icon: 'FirstAidKit' }
          },
          {
            path: 'equipment',
            name: 'EquipmentList',
            component: () => import('@/views/resource/Equipment.vue'),
            meta: { title: '设备管理', icon: 'Monitor' }
          },
          {
            path: 'consumable',
            name: 'ConsumableList',
            component: () => import('@/views/resource/Consumable.vue'),
            meta: { title: '耗材管理', icon: 'Box' }
          }
        ]
      },
      // 报告管理
      {
        path: 'report',
        name: 'ReportManage',
        redirect: '/report/list',
        meta: { title: '报告管理', icon: 'Document' },
        children: [
          {
            path: 'list',
            name: 'ReportList',
            component: () => import('@/views/report/List.vue'),
            meta: { title: '报告列表', icon: 'List' }
          },
          {
            path: 'template',
            name: 'ReportTemplate',
            component: () => import('@/views/report/Template.vue'),
            meta: { title: '报告模板', icon: 'Files' }
          },
          {
            path: 'detail/:id',
            name: 'ReportDetail',
            component: () => import('@/views/report/Detail.vue'),
            meta: { title: '报告详情', hidden: true }
          }
        ]
      },
      // 质量合规
      {
        path: 'quality',
        name: 'QualityManage',
        redirect: '/quality/audit',
        meta: { title: '质量合规', icon: 'Medal' },
        children: [
          {
            path: 'audit',
            name: 'AuditLog',
            component: () => import('@/views/quality/AuditLog.vue'),
            meta: { title: '审计追踪', icon: 'View' }
          },
          {
            path: 'permission',
            name: 'PermissionManage',
            component: () => import('@/views/quality/Permission.vue'),
            meta: { title: '权限管理', icon: 'Lock' }
          }
        ]
      },
      // 系统设置
      {
        path: 'system',
        name: 'SystemManage',
        redirect: '/system/users',
        meta: { title: '系统设置', icon: 'Setting' },
        children: [
          {
            path: 'users',
            name: 'UserManage',
            component: () => import('@/views/system/Users.vue'),
            meta: { title: '用户管理', icon: 'User' }
          },
          {
            path: 'role',
            name: 'RoleManage',
            component: () => import('@/views/system/Role.vue'),
            meta: { title: '角色管理', icon: 'UserFilled' }
          }
        ]
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - LIMS` : 'LIMS - 实验室信息管理系统'

  // 判断是否需要登录
  if (to.meta.requiresAuth !== false) {
    if (!token) {
      next('/login')
    } else {
      next()
    }
  } else {
    if (token && to.path === '/login') {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
