// *************ApplicationTools*****************
import axios from '@/libs/api.request'

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
    params: { account },
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
    params: { account },
    responseType: 'blob'
  })
}
