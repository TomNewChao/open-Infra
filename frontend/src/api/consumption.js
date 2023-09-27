// *************ConsumptionControl*****************
import axios from '@/libs/api.request'

export const BillInfoListApi = (page, size, order_by, order_type, filter_name, filter_value, account, type) => {
  return axios.request({
    url: '/api/consumption_control/bill',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value, account, type
    }
  })
}

export const BillTypeListApi = () => {
  return axios.request({
    url: '/api/consumption_control/resource_type_name',
    method: 'get'
  })
}

export const BillAccountListApi = () => {
  return axios.request({
    url: '/api/consumption_control/account_name',
    method: 'get'
  })
}

export const BillYearAmountListApi = (year) => {
  return axios.request({
    url: '/api/consumption_control/year_amount',
    method: 'get',
    params: {
      year
    }
  })
}

export const BillMonthAccountListApi = (account, bill_cycle) => {
  return axios.request({
    url: '/api/consumption_control/month_amount',
    method: 'get',
    params: {
      account, bill_cycle
    }
  })
}

export const AllBillCycleListApi = () => {
  return axios.request({
    url: '/api/consumption_control/all_bill_cycle',
    method: 'get'
  })
}

export const AllYearListApi = () => {
  return axios.request({
    url: '/api/consumption_control/all_year',
    method: 'get'
  })
}

export const queryCpuMonth = () => {
  return axios.request({
    url: '/api/consumption_control/cpu_month',
    method: 'get'
  })
}

export const queryCpuMonthData = (date) => {
  return axios.request({
    url: '/api/consumption_control/cpu_data',
    method: 'get',
    params: {
      date
    }
  })
}

export const exportCpuMonthData = (date) => {
  return axios.request({
    url: '/api/consumption_control/cpu_table',
    method: 'get',
    params: { date },
    responseType: 'blob'
  })
}

export const queryMemMonth = () => {
  return axios.request({
    url: '/api/consumption_control/mem_month',
    method: 'get'
  })
}

export const queryMemMonthData = (date) => {
  return axios.request({
    url: '/api/consumption_control/mem_data',
    method: 'get',
    params: {
      date
    }
  })
}

export const exportMemMonthData = (date) => {
  return axios.request({
    url: '/api/consumption_control/mem_table',
    method: 'get',
    params: { date },
    responseType: 'blob'
  })
}

