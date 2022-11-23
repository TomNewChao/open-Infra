<template>
  <div>
    <Card>
      <tables ref="tables" editable searchable search-place="top" v-model="accountTableData" :columns="columns" />
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import { accountListApi } from '@/api/tools'

export default {
  name: 'account',
  components: {
    Tables
  },
  data () {
    return {
      columns: [
        { title: 'Account', key: 'account', sortable: true },
        { title: 'Zone', key: 'zone', sortable: true },
      ],
      accountTableData: []
    }
  },
  mounted () {
    this.accountList()
  },
  methods: {
    accountList () {
      accountListApi().then(res => {
        this.accountTableData = res.data.data
      })
    }
  }
}
</script>
