<template>
  <Table height="750" :columns="columns" :data="data"></Table>
</template>
<script>
import { queryPortListApi } from '@/api/tools'

export default {
  data () {
    return {
      columns: [
        {
          title: 'Port',
          key: 'port',
          sortable: true
        },
        {
          title: 'Describe',
          key: 'describe'
        }
      ],
      data: []
    }
  },
  mounted () {
    this.queryPortList()
  },
  methods: {
    queryPortList () {
      queryPortListApi().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.data = res.data.data
        }
      })
    }
  }

}
</script>
