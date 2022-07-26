import axios from '@/libs/api.request'

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
    }
  })
}

export const queryProgressScanPortApi = () => {
  return axios.request({
    url: '/api/clouds_tools/scan_port/progress',
    method: 'get',
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
    }
  })
}

export const queryProgressScanObsApi = () => {
  return axios.request({
    url: '/api/clouds_tools/scan_obs/progress',
    method: 'get',
    responseType: 'blob'
  })
}
