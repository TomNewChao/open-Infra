import axios from '@/libs/api.request'

export const scanPortApi = () => {
  return axios.request({
    url: '/api/clouds_tools/scan_port/',
    method: 'get'
  })
}

export const downloadExcelApi = account => {
  return axios.request({
    url: '/api/clouds_tools/scan_port/',
    method: 'post',
    data: {
      account
    }
  })
}

export const queryProgressApi = () => {
  return axios.request({
    url: '/api/clouds_tools/scan_port/progress',
    method: 'get'
  })
}
