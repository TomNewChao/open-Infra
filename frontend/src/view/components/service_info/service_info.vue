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
      </div>
      <tables ref="tables" search-place="top" v-model="tableDataServiceInfo" :columns="columnsServiceInfo" @on-sort-change="handlerServiceInfoSort"/>
      <Page :total="pageTotalServiceInfo" :current="pageNumServiceInfo" :page-size="pageSizeServiceInfo" show-sizer show-total
            @on-change="handlerServiceInfoPage"
            @on-page-size-change="handlerServiceInfoPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import {ServiceInfoListApi} from '@/api/tools'

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
        { title: '集群名称', key: 'cluster' },
        { title: '命名空间', key: 'namespace' },
        { title: 'URL', key: 'url' }
      ],
      columnsServiceInfo: [
        { title: '服务名称', key: 'service_name', sortable: 'custom'},
        { title: '集群名称', key: 'cluster' },
        { title: '命名空间', key: 'namespace' },
        { title: 'URL', key: 'url'},
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
    handlerServiceInfoSort(column){
      this.orderByServiceInfo = column.key
      this.orderTypeServiceInfo = column.order === "asc" ? 0:1
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
    }
  }
}
</script>
<style>
.ivu-page {
  margin-top: 30px;
  text-align: center;
}
</style>
