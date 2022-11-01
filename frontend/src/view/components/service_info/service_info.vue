<template>
  <div>
    <Card>
      <div class="service-info-search-con search-con-top">
        <Select v-model="searchKeyServiceInfo" class="search-col">
          <Option v-for="item in filterColumnsServiceInfo" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="searchValueServiceInfo"/>
        <Button @click="handleSearchServiceInfo" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
        <Button type="primary" @click="slaHandleSubmit" class="sla-export">导出SLA数据</Button>
      </div>
      <tables ref="tables" search-place="top" v-model="tableDataServiceInfo" :columns="columnsServiceInfo"
              @on-sort-change="handlerServiceInfoSort"/>
      <Page :total="pageTotalServiceInfo" :current="pageNumServiceInfo" :page-size="pageSizeServiceInfo"
            show-sizer
            show-total
            @on-change="handlerServiceInfoPage"
            @on-page-size-change="handlerServiceInfoPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import { exportSlaData, ServiceInfoListApi } from '@/api/tools'
import { getStrDate } from '@/libs/tools'
import { blobDownload } from '@/libs/download'

export default {
  name: 'tables_page',
  components: {
    Tables
  },
  data () {
    return {
      searchKeyServiceInfo: '',
      searchValueServiceInfo: '',
      pageTotalServiceInfo: 10,
      pageNumServiceInfo: 1,
      pageSizeServiceInfo: 10,
      orderByServiceInfo: 'service_name',
      orderTypeServiceInfo: 1,
      filterColumnsServiceInfo: [
        { title: '服务名称', key: 'service_name' },
        { title: '服务别名', key: 'service_alias' },
        { title: '服务介绍', key: 'service_introduce' },
        { title: '社区', key: 'community' }
      ],
      columnsServiceInfo: [
        { title: '服务名称', key: 'service_name', sortable: 'custom' },
        { title: '命名空间', key: 'namespace' },
        { title: '集群名称', key: 'cluster' },
        { title: '服务别名', key: 'service_alias' },
        { title: '服务介绍', key: 'service_introduce' },
        { title: '社区', key: 'community' },
        { title: '月度异常累计时间', key: 'month_abnormal_time', sortable: 'custom' },
        { title: '年度异常累计时间', key: 'year_abnormal_time', sortable: 'custom' },
        { title: '月度sla', key: 'month_sla', sortable: 'custom' },
        { title: '年度sla', key: 'year_sla', sortable: 'custom' },
        { title: '年度剩余sla配额', key: 'remain_time', sortable: 'custom' }

      ],
      tableDataServiceInfo: []
    }
  },
  mounted () {
    this.queryServiceInfoList()
  },
  methods: {
    handleSearchServiceInfo () {
      this.queryServiceInfoList()
    },
    handlerServiceInfoPage (value) {
      this.pageNumServiceInfo = value
      this.queryServiceInfoList()
    },
    handlerServiceInfoPageSize (value) {
      this.pageSizeServiceInfo = value
      this.queryServiceInfoList()
    },
    handlerServiceInfoSort (column) {
      this.orderByServiceInfo = column.key
      this.orderTypeServiceInfo = column.order === 'asc' ? 0 : 1
      this.queryServiceInfoList()
    },
    queryServiceInfoList () {
      ServiceInfoListApi(this.pageNumServiceInfo, this.pageSizeServiceInfo, this.orderByServiceInfo, this.orderTypeServiceInfo, this.searchKeyServiceInfo, this.searchValueServiceInfo).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.tableDataServiceInfo = res.data.data.data
          this.pageTotalServiceInfo = res.data.data.total
          this.pageNumServiceInfo = res.data.data.page
          this.pageSizeServiceInfo = res.data.data.size
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
