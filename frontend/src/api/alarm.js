import axios from '@/libs/api.request'

// *************Alarm*****************
export const alarmListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/alarm/alarm/',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

export const alarmBatchDeleteApi = (alarm_ids) => {
  return axios.request({
    url: '/api/alarm/alarm/',
    method: 'post',
    data: {
      alarm_ids
    }
  })
}

// *************AlarmNotification*****************
// Batch alarm notify get list
export const alarmNotifyListApi = (page, size, order_by, order_type, filter_name, filter_value) => {
  return axios.request({
    url: '/api/alarm/alarm_notify/',
    method: 'get',
    params: {
      page, size, order_by, order_type, filter_name, filter_value
    }
  })
}

// Alarm notify get single
export const alarmNotifyGetApi = (id) => {
  return axios.request({
    url: `/api/alarm/alarm_notify/${id}/`,
    method: 'get'
  })
}

// Alarm Notify get items
export const alarmNotifyGetNameApi = () => {
  return axios.request({
    url: '/api/alarm/alarm_notify/alarm_items/',
    method: 'get'
  })
}

// Alarm Notify create
export const alarmNotifyPostApi = (phone, email, desc, name, keywords) => {
  return axios.request({
    url: '/api/alarm/alarm_notify/',
    method: 'post',
    data: {
      phone, email, desc, name, keywords
    }
  })
}

// Alarm Notify put
export const alarmNotifyPutApi = (phone, email, desc, name, keywords, id) => {
  return axios.request({
    url: `/api/alarm/alarm_notify/${id}/`,
    method: 'put',
    data: {
      phone, email, desc, name, keywords, id
    }
  })
}

// Batch alarm notify delete
export const alarmNotifyBatchDeleteApi = (alarm_notify_ids) => {
  return axios.request({
    url: '/api/alarm/alarm_notify/batch_remove',
    method: 'delete',
    data: {
      alarm_notify_ids
    }
  })
}
