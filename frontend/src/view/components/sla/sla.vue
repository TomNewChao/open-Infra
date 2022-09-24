<template>
  <div>
    <Card>
      <div class="sla-search-con search-con-top">
        <DatePicker type="date" placeholder="Select date" confirm v-model="slaDate" style="width: 200px"/>
        <Select v-model="slaSearchKey" class="search-col">
          <Option v-for="item in slaFilterColumns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="slaSearchValue"/>
        <Button @click="handleSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
        <Button type="primary" @click="slaHandleSubmit" class="sla-export">导出所有数据</Button>
      </div>
      <tables ref="tables" search-place="top" :no-data-text="loadingText ? loadingText : '暂无数据'" v-model="slaTableData" :columns="slaColumns" @on-sort-change="slaSort"/>
      <Page :total="slaPageTotal" :current="slaPageNum" :page-size="slaPageSize" show-sizer show-total
            @on-change="slaHandlerPage"
            @on-page-size-change="slaHandlerPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import { slaListApi, exportSlaData } from '@/api/tools'
import { getStrDate } from '@/libs/tools'
import { blobDownload } from '@/libs/download'

export default {
  name: 'tables_page',
  components: {
    Tables
  },
  data () {
    return {
      slaDate: '',
      slaSearchKey: '',
      slaSearchValue: '',
      slaPageTotal: 10,
      slaPageNum: 1,
      slaPageSize: 10,
      order_by: 'sla_year_remain',
      order_type: 0,
      loadingText: '',
      slaFilterColumns: [
        { title: '服务名', key: 'service_name' }
      ],
      slaColumns: [
        { title: '服务名', key: 'service_name' },
        { title: '服务介绍', key: 'introduce' },
        { title: '访问地址', key: 'sla_url' },
        { title: '社区', key: 'sla_zone' },
        { title: '月度异常累计时间(min)', key: 'month_exp_min', sortable: 'custom'},
        { title: '年度异常累计时间(min)', key: 'year_exp_min' , sortable: 'custom'},
        { title: '月度SLA', key: 'month_sla' , sortable: 'custom'},
        { title: '年度SLA', key: 'year_sla' , sortable: 'custom'},
        { title: '年度剩余SLA配额', key: 'sla_year_remain' , sortable: 'custom', sortType: "asc"}
      ],
      slaTableData: []
    }
  },
  mounted () {
    this.setSlaDate()
    this.querySlaList()
  },
  methods: {
    setSlaDate () {
      let time = new Date()
      let month = time.getMonth() + 1
      let day = time.getDate()
      let nowTime = time.getFullYear() + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day)
      this.slaDate = nowTime + 'T16:00:00.000Z'
    },
    handleSearch () {
      this.querySlaList()
    },
    slaHandlerPage (value) {
      this.slaPageNum = value
      this.querySlaList()
    },
    slaHandlerPageSize (value) {
      this.slaPageSize = value
      this.querySlaList()
    },
    slaSort(column){
      this.order_by = column.key
      this.order_type = column.order === "asc" ? 0:1
      this.querySlaList()
    },
    querySlaList () {
      this.loadingText = '数据正在加载中'
      slaListApi(this.slaPageNum, this.slaPageSize, this.order_by, this.order_type, this.slaSearchKey, this.slaSearchValue, this.slaDate).then(res => {
        this.loadingText = ''
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.slaTableData = res.data.data.data
          this.slaPageTotal = res.data.data.total
          this.slaPageNum = res.data.data.page
          this.slaPageSize = res.data.data.size
        }
      })
    },
    slaHandleSubmit () {
      exportSlaData().then(res => {
        if (res.headers['content-type'] === 'application/octet-stream') {
          let strDate = getStrDate()
          const fileName = 'Sla数据统计表_' + strDate + '.xlsx'
          blobDownload(res.data, fileName)
        }
      })
    }
  }
}
</script>
<style>
.ivu-page {
  margin-top: 30px;
  text-align: center;
}

.search-col {
  margin-left: 3px;
}
.sla-export {
  margin-left: 5px;
}
</style>
