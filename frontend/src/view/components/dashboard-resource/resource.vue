<template>
  <div>
    <Row :gutter="20" style="margin-left: 2px; margin-top: -10px">
      <div class="dashboard-resource-search-con search-con-top">
        <label class="show-label-first">采集时间：</label>
        <Select v-model="curCpuMonth" class="search-col">
          <Option v-for="item in CpuMonth" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Button @click="getCpuMonthData" class="search-btn" type="primary">
          <Icon type="search"/>搜索
        </Button>
        <Button type="primary" @click="cpuExportHandler" class="download">导出选择周的CPU数据</Button>
      </div>
    </Row>
    <Row :gutter="20" style="margin-left: 2px; margin-top: 10px; margin-right: 2px">
      <Card shadow>
        <ScatterChar :chartData="CpuData" title="cpu" height="500px" width="100%"/>
      </Card>
    </Row>
    <Row :gutter="20" style="margin-left: 2px; margin-top: 10px">
      <div class="dashboard-resource-search-con search-con-top">
        <label class="show-label-first">采集时间：</label>
        <Select v-model="curMemMonth" class="search-col">
          <Option v-for="item in MemMonth" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Button @click="getMemMonthData" class="search-btn" type="primary">
          <Icon type="search"/>搜索
        </Button>
        <Button type="primary" @click="memExportHandler" class="download">导出选择周的内存数据</Button>
      </div>
    </Row>
    <Row :gutter="20" style="margin-left: 2px; margin-top: 10px; margin-right: 2px">
      <Card shadow>
        <ScatterChar :chartData="MemData" title="内存" height="500px" width="100%"/>
      </Card>
    </Row>
  </div>
</template>

<script>
import ScatterChar from './scatter_char.vue'
import {
  queryCpuMonth, queryCpuMonthData, queryMemMonth, exportCpuMonthData, queryMemMonthData, exportMemMonthData
} from '@/api/tools'
import { blobDownload } from '@/libs/download'

export default {
  name: 'dashboard-resource',
  components: {
    ScatterChar
  },
  data () {
    return {
      CpuData: [],
      CpuMonth: {},
      curCpuMonth: '',
      MemData: [],
      MemMonth: {},
      curMemMonth: ''
    }
  },
  mounted () {
    this.getCpuMonth()
    this.getMemMonth()
  },
  methods: {
    getCpuMonth () {
      queryCpuMonth().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.CpuMonth = res.data.data
          if (this.CpuMonth.length !== 0) {
            this.curCpuMonth = this.CpuMonth[0].key
            this.getCpuMonthData()
          }
        }
      })
    },
    getCpuMonthData () {
      let date = this.curCpuMonth
      queryCpuMonthData(date).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.CpuData = res.data.data
        }
      })
    },
    cpuExportHandler () {
      let date = this.curCpuMonth
      exportCpuMonthData(date).then(res => {
        if (res.headers['content-type'] === 'application/octet-stream') {
          const fileName = '服务器cpu数据统计表_' + date + '.xlsx'
          blobDownload(res.data, fileName)
        }
      })
    },
    getMemMonth () {
      queryMemMonth().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.MemMonth = res.data.data
          if (this.MemMonth.length !== 0) {
            this.curMemMonth = this.MemMonth[0].key
            this.getMemMonthData()
          }
        }
      })
    },
    getMemMonthData () {
      let date = this.curMemMonth
      queryMemMonthData(date).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.MemData = res.data.data
        }
      })
    },
    memExportHandler () {
      let date = this.curMemMonth
      exportMemMonthData(date).then(res => {
        if (res.headers['content-type'] === 'application/octet-stream') {
          const fileName = '服务器内存数据统计表' + date + '.xlsx'
          blobDownload(res.data, fileName)
        }
      })
    }
  }
}
</script>

<style lang="less">
.dashboard-resource-search-con {
  padding: 10px 0;

  .search {
    &-col {
      display: inline-block;
      width: 200px;
    }

    &-input {
      display: inline-block;
      width: 200px;
      margin-left: 2px;
    }

    &-btn {
      margin-left: 2px;
    }
  }
}

.show-label-first {
  margin-left: 1px;
  margin-right: 2px;
}
.download {
  margin-left: 5px;
}
</style>
