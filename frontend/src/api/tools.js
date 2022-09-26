import axios from '@/libs/api.request'
// ToolBar
export const highRiskPortApiList = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/clouds_tools/high_risk_port',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

export const highRiskPortApiPost = (port, desc) => {
  return axios.request({
    url: '/api/clouds_tools/high_risk_port',
    method: 'post',
    data: {
      port, desc
    }
  })
}

export const highRiskPortApiDeletePost = (port_list) => {
  return axios.request({
    url: '/api/clouds_tools/bulk_high_risk_port',
    method: 'post',
    data: {
      port_list
    }
  })
}

export const scanPortApi = () => {
  return axios.request({
    url: '/api/clouds_tools/scan_port',
    method: 'get'
  })
}

export const downloadScanPortExcelApi = account => {
  return axios.request({
    url: '/api/clouds_tools/scan_port',
    method: 'post',
    data: {
      account
    },
    responseType: 'blob'
  })
}

export const downloadSingleScanPortExcelApi = (ak, sk, account) => {
  return axios.request({
    url: '/api/clouds_tools/single_scan_port',
    method: 'post',
    data: {
      ak, sk, account
    }
  })
}

export const queryProgressSingleScanPortApi = (account) => {
  return axios.request({
    url: '/api/clouds_tools/single_scan_port/progress',
    method: 'get',
    params: {account},
    responseType: 'blob'
  })
}

export const scanObsApi = () => {
  return axios.request({
    url: '/api/clouds_tools/scan_obs',
    method: 'get'
  })
}

export const downloadScanObsExcelApi = account => {
  return axios.request({
    url: '/api/clouds_tools/scan_obs',
    method: 'post',
    data: {
      account
    },
    responseType: 'blob'
  })
}

export const downloadSingleScanObsExcelApi = (ak, sk, account) => {
  return axios.request({
    url: '/api/clouds_tools/single_scan_obs',
    method: 'post',
    data: {
      ak, sk, account
    }
  })
}

export const queryProgressSingleScanObsApi = (account) => {
  return axios.request({
    url: '/api/clouds_tools/single_scan_obs/progress',
    method: 'get',
    params: {account},
    responseType: 'blob'
  })
}

// Resources
export const eipListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/clouds_tools/eip',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

export const slaListApi = (page, size, order_by, order_type, filter_name, filter_value, sla_date) => {
  return axios.request({
    url: '/api/clouds_tools/sla',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value, sla_date
    }
  })
}

export const exportSlaData = () => {
  return axios.request({
    url: '/api/clouds_tools/sla_export',
    method: 'get',
    responseType: 'blob'
  })
}

// Alarm
export const AlarmListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/alarm/alarm',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}


export const batchDeleteAlarmPostApi = (alarm_ids) => {
  return axios.request({
    url: '/api/alarm/alarm',
    method: 'post',
    data: {
      alarm_ids
    }
  })
}

// Alarm Notify
export const alarmNameGetApi = () => {
  return axios.request({
      url: '/api/alarm/alarm_name',
      method: 'GET'
    }
  )
}

// Alarm notify create
export const alarmNotifyPostApi = (phone, email, desc, name, keywords) => {
  return axios.request({
    url: '/api/alarm/alarm_notify',
    method: 'post',
    data: {
      phone, email, desc, name, keywords
    }
  })
}


// Alarm notify get single alarmNotify
export const alarmNotifyGetApi = (id) => {
  return axios.request({
    url: '/api/alarm/alarm_notify',
    method: 'get',
    params: {
      id
    }
  })
}

// Batch alarm notify list
export const alarmNotifyListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/alarm/batch_alarm_notify',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

// Batch alarm notify delete
export const alarmNotifyDeletePostApi = (alarm_notify_ids) => {
  return axios.request({
    url: '/api/alarm/batch_alarm_notify',
    method: 'post',
    data: {
      alarm_notify_ids
    }
  })
}




