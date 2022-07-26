<template>
  <div>
    <Table border ref="selection" :columns="columns" :data="data"></Table>
    <div style="margin-top: 0px">
      <Button style="margin: 10px 2px 2px;" type="primary" @click="handleSelectAll(true)">全选</Button>
      <Button style="margin: 10px 2px 2px;" type="primary" @click="handleSelectAll(false)">取消全选</Button>
      <Button style="margin: 10px 2px 2px;" type="primary" @click="exportExcel">导出</Button>
    </div>
  </div>
</template>
<script>
  import {scanObsApi, downloadScanObsExcelApi, queryProgressScanObsApi} from '@/api/tools';

  export default {
    data() {
      return {
        columns: [
          {
            type: 'selection',
            width: 60,
            align: 'center'
          },
          {
            title: 'Account',
            key: 'account'
          },
          {
            title: 'Zone',
            key: 'zone'
          }
        ],
        data: []
      }
    },
    mounted() {
      this.getAccountInfo()
    },
    methods: {
      handleSelectAll(status) {
        this.$refs.selection.selectAll(status);
        console.log(this.$refs.selection)
      },
      getAccountInfo() {
        scanObsApi().then(res => {
          this.data = res.data.data
        })
      }
    }
  }
</script>
