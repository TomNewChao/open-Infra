import Main from '@/components/main'
import parentView from '@/components/parent-view'

/**
 * iview-admin中meta除了原生参数外可配置的参数:
 * meta: {
 *  title: { String|Number|Function }
 *         显示在侧边栏、面包屑和标签栏的文字
 *         使用'{{ 多语言字段 }}'形式结合多语言使用，例子看多语言的路由配置;
 *         可以传入一个回调函数，参数是当前路由对象，例子看动态路由和带参路由
 *  hideInBread: (false) 设为true后此级路由将不会出现在面包屑中，示例看QQ群路由配置
 *  hideInMenu: (false) 设为true后在左侧菜单不会显示该页面选项
 *  notCache: (false) 设为true后页面在切换标签后不会缓存，如果需要缓存，无需设置这个字段，而且需要设置页面组件name属性和路由配置的name一致
 *  access: (null) 可访问该页面的权限数组，当前路由设置的权限会影响子路由
 *  icon: (-) 该页面在左侧菜单、面包屑和标签导航处显示的图标，如果是自定义图标，需要在图标名称前加下划线'_'
 *  beforeCloseName: (-) 设置该字段，则在关闭当前tab页时会去'@/router/before-close.js'里寻找该字段名对应的方法，作为关闭前的钩子函数
 * }
 */

export default [
  {
    path: '/login',
    name: 'login',
    meta: {
      title: 'Login - 登录',
      hideInMenu: true
    },
    component: () => import('@/view/login/login.vue')
  },
  {
    path: '/',
    name: 'Home',
    redirect: '/home',
    component: Main,
    meta: {
      // hideInMenu: true,
      notCache: true,
      icon: 'logo-windows',
      title: '工具'
    },
    children: [
      {
        path: '/home',
        name: 'home',
        meta: {
          hideInMenu: true,
          title: '首页',
          notCache: true,
          icon: 'md-home'
        },
        component: () => import('@/view/single-page/home')
      }
    ]
  },
  {
    path: '/message',
    name: 'message',
    component: Main,
    meta: {
      hideInBread: true,
      hideInMenu: true
    },
    children: [
      {
        path: 'message_page',
        name: 'message_page',
        meta: {
          icon: 'md-notifications',
          title: '消息中心'
        },
        component: () => import('@/view/single-page/message/index.vue')
      }
    ]
  },
  {
    path: '/resources',
    name: 'Resources',
    meta: {
      icon: 'logo-buffer',
      title: '工具'
    },
    component: Main,
    children: [
      {
        path: 'eip',
        name: 'Eip',
        meta: {
          icon: 'md-arrow-round-forward',
          title: 'eip信息查询'
        },
        component: () => import('@/view/components/eip/eip.vue')
      },
      {
        path: 'service_info',
        name: 'ServiceInfo',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '服务信息'
        },
        component: () => import('@/view/components/service_info/service_info.vue')
      }
    ]
  },
  {
    path: '/tools',
    name: 'Tools',
    meta: {
      icon: 'logo-buffer',
      title: '工具'
    },
    component: Main,
    children: [
      {
        path: 'high_risk_port',
        name: 'high_risk_port',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '高危端口扫描'
        },
        component: () => import('@/view/components/high_risk_port/high_risk_port.vue')
      },
      {
        path: 'multi_scan_port',
        name: 'multi_scan_port',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '多账户端口扫描'
        },
        component: () => import('@/view/components/multi-scan-port/multi-scan-port.vue')
      },
      {
        path: 'single_scan_port',
        name: 'single_scan_port',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '单账户端口扫描'
        },
        component: () => import('@/view/components/single-scan-port/single-scan-port')
      },
      {
        path: 'multi_scan_obs',
        name: 'multi_scan_obs',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '多账户对象系统扫描'
        },
        component: () => import('@/view/components/multi-scan-obs/multi-scan-obs.vue')
      },
      {
        path: 'single_scan_obs',
        name: 'single_scan_obs',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '单账户对象系统扫描'
        },
        component: () => import('@/view/components/single-scan-obs/single-scan-obs')
      }
    ]
  },
  {
    path: '/permission_control',
    name: 'PermissionControl',
    meta: {
      icon: 'logo-buffer',
      title: '权限管控'
    },
    component: Main,
    children: [
      {
        path: 'kubeconfig',
        name: 'KubeConfig',
        meta: {
          icon: 'md-arrow-round-forward',
          title: 'KubeConfig'
        },
        component: () => import('@/view/components/kubeconfig/kubeconfig.vue')
      },
      {
        path: 'fortress_machine',
        name: 'Fortress-Machine',
        meta: {
          icon: 'md-arrow-round-forward',
          title: 'Fortress-Machine'
        },
        component: () => import('@/view/components/fortress-machine/fortress-machine.vue')
      }
    ]
  },
  {
    path: '/alarm',
    name: 'Alarm',
    meta: {
      icon: 'logo-buffer',
      title: '报警'
    },
    component: Main,
    children: [
      {
        path: 'alarm',
        name: 'alarm',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '报警信息'
        },
        component: () => import('@/view/components/alarm/alarm.vue')
      },
      {
        path: 'alarm_email',
        name: 'alarm_email',
        meta: {
          icon: 'md-arrow-round-forward',
          title: '报警邮件'
        },
        component: () => import('@/view/components/alarm-email/alarm-email.vue')
      }
    ]
  },
  {
    path: '/monitor',
    name: 'Monitor',
    meta: {
      icon: 'logo-buffer',
      title: '系统监控'
    },
    component: Main,
    children: [
      {
        path: 'prometheus',
        name: 'prometheus',
        meta: {
          icon: 'md-arrow-round-forward',
          title: 'prometheus'
        },
        component: () => import('@/view/components/prometheus/prometheus.vue')
      },
      {
        path: 'grafana',
        name: 'grafana',
        meta: {
          icon: 'md-arrow-round-forward',
          title: 'grafana'
        },
        component: () => import('@/view/components/grafana/grafana.vue')
      },
      {
        path: 'uptime_status',
        name: 'uptime_status',
        meta: {
          icon: 'md-arrow-round-forward',
          title: 'uptime_status'
        },
        component: () => import('@/view/components/uptime-status/uptime-status.vue')
      }
    ]
  },

  {
    path: '/argu',
    name: 'argu',
    meta: {
      hideInMenu: true
    },
    component: Main,
    children: [
      {
        path: 'params/:id',
        name: 'params',
        meta: {
          icon: 'md-flower',
          title: route => `{{ params }}-${route.params.id}`,
          notCache: true,
          beforeCloseName: 'before_close_normal'
        },
        component: () => import('@/view/argu-page/params.vue')
      },
      {
        path: 'query',
        name: 'query',
        meta: {
          icon: 'md-flower',
          title: route => `{{ query }}-${route.query.id}`,
          notCache: true
        },
        component: () => import('@/view/argu-page/query.vue')
      }
    ]
  },
  {
    path: '/401',
    name: 'error_401',
    meta: {
      hideInMenu: true
    },
    component: () => import('@/view/error-page/401.vue')
  },
  {
    path: '/500',
    name: 'error_500',
    meta: {
      hideInMenu: true
    },
    component: () => import('@/view/error-page/500.vue')
  },
  {
    path: '*',
    name: 'error_404',
    meta: {
      hideInMenu: true
    },
    component: () => import('@/view/error-page/404.vue')
  }
]
