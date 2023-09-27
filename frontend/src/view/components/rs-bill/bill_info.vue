<template>
  <div>
    <Card>
      <div class="bill-search-con search-con-top">
        <Select v-model="searchKeyBillInfo" class="search-col">
          <Option v-for="item in filterColumnsBillInfo" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="searchValueBillInfo"/>
        <Button @click="handleSearchBillInfo" class="search-btn" type="primary">
          <Icon type="search"/>搜索
        </Button>
        <label class="show-label-first">应付金额总计：{{ totalConsumeAmount }}</label>
        <label class="show-label-second">实际费用总计：{{ totalActualCost }}</label>
      </div>
      <tables ref="tables" search-place="top" v-model="tableDataBillInfo" :columns="columnsBillInfo"
              @on-filter-change="handlerBillInfoFilter"
              @on-sort-change="handlerBillInfoSort"/>
      <Page :total="pageTotalBillInfo" :current="pageNumBillInfo" :page-size="pageSizeBillInfo"
            :pageSizeOpts="pageSizeOptsBillInfo"
            show-sizer
            show-total
            @on-change="handlerBillInfoPage"
            @on-page-size-change="handlerBillInfoPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import {
  BillAccountListApi,
  BillInfoListApi,
  BillTypeListApi
} from '@/api/tools'

export default {
  name: 'bill_info',
  components: {
    Tables
  },
  data () {
    return {
      searchKeyBillInfo: '',
      searchValueBillInfo: '',
      pageTotalBillInfo: 10,
      pageNumBillInfo: 1,
      pageSizeBillInfo: 10,
      orderByBillInfo: 'bill_cycle',
      orderTypeBillInfo: 1,
      billAccount: '',
      billType: '',
      totalConsumeAmount: 0,
      totalActualCost: 0,
      pageSizeOptsBillInfo: [10, 20, 50, 100],
      filterColumnsBillInfo: [
        { title: '账期', key: 'bill_cycle' },
        { title: '云服务类型名称', key: 'resource_type_name' }
      ],
      columnsBillInfo: [
        { title: '账期', key: 'bill_cycle', sortable: 'custom' },
        {
          title: '账户',
          key: 'account',
          filters: [],
          filterMultiple: false,
          filterMethod (value, row) {
            return value
          }
        },
        {
          title: '云服务类型名称',
          key: 'resource_type_name',
          filters: [],
          filterMultiple: false,
          filterMethod (value, row) {
            return value
          }
        },
        { title: '应付金额', key: 'consume_amount', sortable: 'custom' },
        { title: '折扣率', key: 'discount_rate', sortable: 'custom' },
        { title: '实际费用', key: 'actual_cost', sortable: 'custom' }
      ],
      tableDataBillInfo: []
    }
  },
  mounted () {
    this.queryBillInfoList()
    this.queryBillAccountItem()
    this.queryBillTypeItem()
  },
  methods: {
    handleSearchBillInfo () {
      this.queryBillInfoList()
    },
    handlerBillInfoPage (value) {
      this.pageNumBillInfo = value
      this.queryBillInfoList()
    },
    handlerBillInfoPageSize (value) {
      this.pageSizeBillInfo = value
      this.queryBillInfoList()
    },
    handlerBillInfoSort (column) {
      this.orderByBillInfo = column.key
      this.orderTypeBillInfo = column.order === 'asc' ? 0 : 1
      this.queryBillInfoList()
    },
    queryBillInfoList () {
      BillInfoListApi(this.pageNumBillInfo, this.pageSizeBillInfo, this.orderByBillInfo, this.orderTypeBillInfo, this.searchKeyBillInfo, this.searchValueBillInfo, this.billAccount, this.billType).then(res => {
        if (res.data.code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.tableDataBillInfo = res.data.data.data
          this.pageTotalBillInfo = res.data.data.total
          this.pageNumBillInfo = res.data.data.page
          this.pageSizeBillInfo = res.data.data.size
          this.totalConsumeAmount = res.data.data.total_consume_amount
          this.totalActualCost = res.data.data.total_actual_cost
        }
      })
    },
    queryBillAccountItem () {
      BillAccountListApi().then(res => {
        if (res.data.code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.columnsBillInfo[1].filters = res.data.data
        }
      })
    },
    queryBillTypeItem () {
      BillTypeListApi().then(res => {
        if (res.data.code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.columnsBillInfo[2].filters = res.data.data
        }
      })
    },
    handlerBillInfoFilter (value) {
      if (value.key === 'account') {
        this.billAccount = value._filterChecked[0]
      } else if (value.key === 'resource_type_name') {
        this.billType = value._filterChecked[0]
      }
      this.queryBillInfoList()
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

.show-label-first {
  margin-left: 20px;
}
.show-label-second {
  margin-left: 20px;
}
</style>
