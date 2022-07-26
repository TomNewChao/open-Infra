<template>
  <div>
    <Card>
      <tables ref="tables" editable searchable search-place="top" v-model="tableData" :columns="columns"
              :loading="loading"
              @on-delete="handleDelete"/>
      <Button style="margin: 10px 2px 2px;" type="primary" @click="exportExcel">导出</Button>

    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables';
import {scanPortApi, downloadScanPortExcelApi, queryProgressScanPortApi} from '@/api/tools';
import {blobDownload} from '@/libs/download.js';
import {getStrDate} from '@/libs/tools.js';

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
      loading: false,
      tempValue: null
    }
  },
  mounted() {
    this.scanPort()
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
      this.loading = false
    }
  },
  methods: {
    handleDelete(params) {
    },
    exportExcel() {
      let selectName = [];
      for (let i = 0; i < this.tableData.length; i++) {
        selectName.push(this.tableData[i].account)
      }
      if (selectName.length === 0) {
        this.$Message.info('请至少选择一个Account。');
      } else {
        downloadScanPortExcelApi(selectName).then(res => {
          if (res.data.err_code !== 0) {
            this.$Message.info(res.data.description)
          } else {
            this.startTimer();
            this.loading = true
          }
        })
      }
    },
    queryExcel() {
      queryProgressScanPortApi().then(res => {
        if (res.headers['content-type'] === 'application/octet-stream') {
          let strDate = getStrDate();
          const fileName = "IP端口扫描统计表_" + strDate + ".xlsx";
          blobDownload(res.data, fileName);
          if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
            this.loading = false
          }
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
      this.timer = setInterval(() => {
        setTimeout(this.queryExcel, 0)
      }, 3000)
    },
  }
}
</script>
