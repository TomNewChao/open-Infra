<template>
  <div>
    <Card>
      <div class="eip-search-con search-con-top">
        <Select v-model="searchKey" class="search-col">
          <Option v-for="item in filter_columns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="searchValue"/>
        <Button @click="handleSearch" class="search-btn" type="primary">
          <Icon type="search"/>搜索
        </Button>
      </div>
      <tables ref="tables" search-place="top" v-model="tableData" :columns="columns" @on-sort-change="handlerEipSort"/>
      <Page :total="pageTotal" :current="pageNum" :page-size="pageSize" show-sizer show-total
            @on-change="handlerPage"
            @on-page-size-change="handlerPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import { eipListApi } from '@/api/tools'

export default {
  name: 'tables_page',
  components: {
    Tables
  },
  data () {
    return {
      searchKey: '',
      searchValue: '',
      pageTotal: 10,
      pageNum: 1,
      pageSize: 10,
      order_by: 'create_time',
      order_type: 1,
      filter_columns: [
        { title: 'IP', key: 'eip' },
        { title: '状态', key: 'eip_type' },
        { title: '归属区域', key: 'eip_zone' },
        { title: '实例id', key: 'example_id' },
        { title: '实例名称', key: 'example_name' },
        { title: '账户', key: 'account' }
      ],
      columns: [
        { title: 'IP', key: 'eip', sortable: 'custom' },
        { title: '状态', key: 'eip_status' },
        { title: '类型', key: 'eip_type' },
        { title: '归属区域', key: 'eip_zone', sortable: 'custom' },
        { title: '宽带id', key: 'bandwidth_id' },
        { title: '宽带名称', key: 'bandwidth_name' },
        { title: '宽带size', key: 'bandwidth_size', sortable: 'custom' },
        { title: '实例id', key: 'example_id' },
        { title: '实例名称', key: 'example_name' },
        { title: '实例类型', key: 'example_type' },
        { title: '账户', key: 'account', sortable: 'custom' },
        { title: '创建时间', key: 'create_time', sortable: 'custom', sortType: "desc"},
        { title: '刷新时间', key: 'refresh_time', sortable: 'custom' }
      ],
      tableData: []
    }
  },
  mounted () {
    this.queryEipList()
  },
  methods: {
    handleSearch () {
      this.queryEipList()
    },
    handlerPage (value) {
      this.pageNum = value
      this.queryEipList()
    },
    handlerPageSize (value) {
      this.pageSize = value
      this.queryEipList()
    },
    handlerEipSort(column){
      this.order_by = column.key
      this.order_type = column.order === "asc" ? 0:1
      this.queryEipList()
    },
    queryEipList () {
      eipListApi(this.pageNum, this.pageSize, this.order_by, this.order_type, this.searchKey, this.searchValue).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.tableData = res.data.data.data
          this.pageTotal = res.data.data.total
          this.pageNum = res.data.data.page
          this.pageSize = res.data.data.size
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
