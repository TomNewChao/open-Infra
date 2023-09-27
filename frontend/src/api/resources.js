// *************ApplicationResources*****************
import axios from '@/libs/api.request'

export const accountListApi = () => {
  return axios.request({
    url: '/api/app_resources/account',
    method: 'get'
  })
}

export const eipListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/app_resources/eip',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

export const ServiceInfoListApi = (page, size, order_by, order_type, filter_name, filter_value, cluster, region, community, base_image, base_os) => {
  return axios.request({
    url: '/api/app_resources/service',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value, cluster, region, community, base_image, base_os
    }
  })
}

export const ServiceDetailApi = (id) => {
  return axios.request({
    url: '/api/app_resources/detail_service',
    method: 'get',
    params: {
      id
    }
  })
}

export const ServiceClusterListApi = () => {
  return axios.request({
    url: '/api/app_resources/cluster',
    method: 'get'
  })
}

export const ServiceRegionListApi = () => {
  return axios.request({
    url: '/api/app_resources/region',
    method: 'get'
  })
}

export const ServiceCommunityListApi = () => {
  return axios.request({
    url: '/api/app_resources/community',
    method: 'get'
  })
}

export const ServiceBaseOsListApi = () => {
  return axios.request({
    url: '/api/app_resources/base_os',
    method: 'get'
  })
}

export const ServiceBaseImageListApi = () => {
  return axios.request({
    url: '/api/app_resources/base_image',
    method: 'get'
  })
}

export const exportSlaData = () => {
  return axios.request({
    url: '/api/app_resources/sla_export',
    method: 'get',
    responseType: 'blob'
  })
}

export const exportServiceData = (order_by, order_type, filter_name, filter_value, cluster, region, community, base_image, base_os) => {
  return axios.request({
    url: '/api/app_resources/service_export',
    method: 'get',
    responseType: 'blob',
    params: {
      order_by, order_type, filter_name, filter_value, cluster, region, community, base_image, base_os
    }
  })
}
