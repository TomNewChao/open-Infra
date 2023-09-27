// *************PermissionControl*****************
// Single KubeConfig Detail
import axios from '@/libs/api.request'

export const kubeConfigGetApi = (id) => {
  return axios.request({
    url: '/api/permission/kubeconfig',
    method: 'get',
    params: {
      id
    }
  })
}

// Single KubeConfig Put
export const kubeConfigPutApi = (expired_time, role, id) => {
  return axios.request({
    url: '/api/permission/kubeconfig',
    method: 'put',
    data: {
      expired_time, role, id
    }
  })
}

// Batch KubeConfig list
export const kubeConfigListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/permission/batch_kubeconfig',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

// Batch KubeConfig delete
export const kubeConfigDeletePostApi = (kubeconfig_ids) => {
  return axios.request({
    url: '/api/permission/batch_kubeconfig',
    method: 'post',
    data: {
      kubeconfig_ids
    }
  })
}
