import axios from '@/libs/api.request'

export const errorReq = () => {
  return axios.request({
    url: 'error_url',
    method: 'post'
  })
}

export const saveErrorLogger = info => {
  return axios.request({
    url: '/api/users/log_info',
    data: info,
    method: 'post'
  })
}

