import axios from '@/libs/api.request'
// *************Index*****************
export const indexApiList = () => {
  return axios.request({
    url: '/api/app_resources/index',
    methods: 'get'
  })
}
