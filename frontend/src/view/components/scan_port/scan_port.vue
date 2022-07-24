<template>
  <div>
    <Card>
      <tables ref="tables" editable searchable search-place="top" v-model="tableData" :columns="columns" :loading="loading"
              @on-delete="handleDelete"/>
      <Button style="margin: 10px 2px 2px;" type="primary" @click="exportExcel">导出</Button>

    </Card>
  </div>
</template>

<script>
  import Tables from '_c/tables';
  import {scanPortApi, downloadExcelApi, queryProgressApi} from '@/api/tools';
  import {blobDownload} from '@/libs/download.js';

  export default {
    name: 'tables_page',
    components: {
      Tables
    },
    data() {
      return {
        columns: [
          {title: 'Account', key: 'account', sortable: true},
          {title: 'Zone', key: 'zone', sortable: true},
          {
            title: 'Handle',
            key: 'handle',
            options: ['delete'],
            button: [
              (h, params, vm) => {
                return h('Poptip', {
                  props: {
                    confirm: true,
                    title: '你确定要删除吗?'
                  },
                  on: {
                    'on-ok': () => {
                      vm.$emit('on-delete', params)
                      vm.$emit('input', params.tableData.filter((item, index) => index !== params.row.initRowIndex))
                    }
                  }
                })
              }
            ]
          }
        ],
        tableData: [],
        timer: null,
        loading: false
      }
    },
    mounted() {
      this.scanPort()
    },
    beforeDestroy() {
      // self.stopTimer()
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
        this.loading = false
      }
    },
    methods: {
      handleDelete(params) {
        console.log(params)
      },
      exportExcel() {
        let selectName = [];
        for (let i = 0; i < this.tableData.length; i++) {
          selectName.push(this.tableData[i].account)
        }
        console.log(selectName)
        selectName = ["hwstaff_intl_openEuler",]
        downloadExcelApi(selectName).then(res => {
          this.startTimer();
          this.loading = true
        })
      },
      queryExcel() {
        queryProgressApi().then(res => {
          console.log(res.data.description);
          console.log(res.headers);
          if (res.headers['content-type'] === 'application/octet-stream') {
            blobDownload(res.data, "IP端口扫描统计表.xlsx");
            if (this.timer) {
              clearInterval(this.timer);
              this.timer = null;
              this.loading = false
            }
          } else {
            console.log(res.data.description)
          }
        })
      },
      scanPort() {
        scanPortApi().then(res => {
          this.tableData = res.data.data
        })
      },
      startTimer() {
        if (this.timer) {
          clearInterval(this.timer);
          this.timer = null
        }
        this.timer = setInterval(() => {setTimeout(this.queryExcel, 0)}, 1000)
      },
    }
  }
</script>

<style>

</style>
