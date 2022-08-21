<template>
  <div>
    <Card>
      <div class="search-con search-con-top">
        <Select v-model="searchKey" class="search-col">
          <Option v-for="item in columns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="searchValue"/>
        <Button @click="handleSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
      </div>
      <tables ref="tables" search-place="top" v-model="tableData" :columns="columns"/>
      <Page :total="100" show-sizer/>
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
    data() {
      return {
        searchValue: "",
        searchKey: "",
        columns: [
          {title: 'IP', key: 'eip', sortable: true},
          {title: '状态', key: 'eip_status'},
          {title: '类型', key: 'eip_type'},
          {title: '归属区域', key: 'eip_zone'},
          {title: '宽带id', key: 'bandwidth_id'},
          {title: '宽带名称', key: 'bandwidth_name'},
          {title: '宽带size', key: 'bandwidth_size'},
          {title: '实例id', key: 'example_id'},
          {title: '实例名称', key: 'example_name'},
          {title: '实例类型', key: 'example_type'},
          {title: '账户', key: 'account'},
          {title: '创建时间', key: 'create_time', sortable: true},

        ],
        tableData: []
      }
    },
    mounted() {
      this.queryEipList()
    },
    methods: {
      handleSearch() {
        console.log(this.searchKey)
        console.log(this.searchValue)
      },
      queryEipList() {
        eipListApi().then(res => {
          if (res.data.err_code !== 0) {
            this.$Message.info(res.data.description)
          } else {
            this.tableData = res.data.data
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
