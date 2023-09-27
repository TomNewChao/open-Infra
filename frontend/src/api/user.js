import axios from '@/libs/api.request'

export const login = ({ username, password }) => {
  const data = {
    username,
    password
  }
  return axios.request({
    url: '/api/users/login/',
    data,
    method: 'post'
  })
}

export const logout = () => {
  return axios.request({
    url: '/api/users/logout/',
    method: 'post'
  })
}

export const getUserInfo = () => {
  return axios.request({
    url: '/api/users/user_info/',
    method: 'get'
  })
}

export const getUnreadCount = () => {
  return axios.request({
    url: '/api/users/message_count/',
    method: 'get'
  })
}

export const getMessage = () => {
  return axios.request({
    url: 'message/init/',
    method: 'get'
  })
}

export const getContentByMsgId = msg_id => {
  return axios.request({
    url: 'message/content/',
    method: 'get',
    params: {
      msg_id
    }
  })
}

export const hasRead = msg_id => {
  return axios.request({
    url: 'message/has_read',
    method: 'post',
    data: {
      msg_id
    }
  })
}

export const removeReaded = msg_id => {
  return axios.request({
    url: 'message/remove_readed',
    method: 'post',
    data: {
      msg_id
    }
  })
}

export const restoreTrash = msg_id => {
  return axios.request({
    url: 'message/restore',
    method: 'post',
    data: {
      msg_id
    }
  })
}
