<template>
  <div>
    <Row :gutter="20" style="margin-left: 2px; margin-top: -10px">
      <div class="dashboard-bill-search-con search-con-top">
        <Select v-model="searchYear" class="search-col">
          <Option v-for="item in yearColumns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Button @click="handleYearSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
      </div>
    </Row>
    <Row :gutter="20" style="margin-left: 2px; margin-top: 10px; margin-right: 2px">
      <Card shadow>
        <LineChar :chartData="MonthData" height="500px" width="100%"/>
      </Card>
    </Row>
    <Row :gutter="20" style="margin-left: 2px; margin-top: 10px">
      <div class="dashboard-bill-search-con search-con-top">
        <Select v-model="searchBillCycle" class="search-col">
          <Option v-for="item in billCycleColumns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Button @click="handleMonthSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
      </div>
    </Row>
    <Row :gutter="20" style="margin-top: 10px;">
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData0" :text="titleCommunity[0]"
                     :subtext="titleAccount[0]"></chart-pie>
        </Card>
      </i-col>
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData1" :text="titleCommunity[1]"
                     :subtext="titleAccount[1]"></chart-pie>
        </Card>
      </i-col>
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData2" :text="titleCommunity[2]"
                     :subtext="titleAccount[2]"></chart-pie>
        </Card>
      </i-col>
    </Row>
    <Row :gutter="20" style="margin-top: 10px;">
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData3" :text="titleCommunity[3]"
                     :subtext="titleAccount[3]"></chart-pie>
        </Card>
      </i-col>
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData4" :text="titleCommunity[4]"
                     :subtext="titleAccount[4]"></chart-pie>
        </Card>
      </i-col>
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData5" :text="titleCommunity[5]"
                     :subtext="titleAccount[5]"></chart-pie>
        </Card>
      </i-col>
    </Row>
    <Row :gutter="20" style="margin-top: 10px;">
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData6" :text="titleCommunity[6]"
                     :subtext="titleAccount[6]"></chart-pie>
        </Card>
      </i-col>
      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">
        <Card shadow>
          <chart-pie style="height: 300px;" :value="pieData7" :text="titleCommunity[7]"
                     :subtext="titleAccount[7]"></chart-pie>
        </Card>
      </i-col>
    </Row>
  </div>
</template>

<script>
import { ChartPie } from '_c/charts'
import LineChar from './line_char.vue'
import {
  AllBillCycleListApi,
  AllYearListApi,
  BillMonthAccountListApi,
  BillYearAmountListApi
} from '@/api/tools'

export default {
  name: 'dashboard-bill',
  components: {
    ChartPie,
    LineChar
  },
  data () {
    return {
      MonthData: {},
      titleCommunity: ['openEuler', 'MindSpore', 'openGauss', 'openLooKeng', 'osInfra', 'openEuler国际站', 'OM看板', '昇思'],
      titleAccount: ['openeuler', 'hwstaff_h00223369', 'hwstaff_x00350071', 'hwstaff_zengchen1024', 'freesky-edward', 'hwstaff_intl_openEuler', 'hwstaff_z00223460', 'leon_wang'],
      account: ['openeuler', 'hwstaff_h00223369', 'hwstaff_x00350071', 'hwstaff_zengchen1024', 'freesky-edward', 'hwstaff_intl_openEuler', 'hwstaff_z00223460', 'leon_wang'],
      billCycle: '',
      searchBillCycle: '',
      billCycleColumns: [],
      year: '',
      searchYear: '',
      yearColumns: [],
      pieData0: [],
      pieData1: [],
      pieData2: [],
      pieData3: [],
      pieData4: [],
      pieData5: [],
      pieData6: [],
      pieData7: []
    }
  },
  mounted () {
    this.getAllBillCycle()
    this.getAllYear()
    this.initMonthData()
    this.initYearData()
  },
  methods: {
    getAllYear () {
      AllYearListApi().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.yearColumns = res.data.data
        }
      })
    },
    getAllBillCycle () {
      AllBillCycleListApi().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.billCycleColumns = res.data.data
        }
      })
    },
    initYearData () {
      const timeOne = new Date()
      let year = timeOne.getUTCFullYear()
      this.year = year
      this.searchYear = year
      this.getYearAmountData()
    },
    initMonthData () {
      const timeOne = new Date()
      let year = timeOne.getUTCFullYear()
      let month = timeOne.getUTCMonth()
      if (month.toString().length === 1) {
        month = '0' + month
      }
      const last_month = year + '-' + month
      this.billCycle = last_month
      this.searchBillCycle = last_month
      this.getPieData()
    },
    handleYearSearch () {
      this.year = this.searchYear
      this.getYearAmountData()
    },
    handleMonthSearch () {
      this.billCycle = this.searchBillCycle
      this.getPieData()
    },
    getYearAmountData () {
      let year = this.year
      BillYearAmountListApi(year).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.MonthData = res.data.data
        }
      })
    },
    getPieData () {
      this.getPie0Data()
      this.getPie1Data()
      this.getPie2Data()
      this.getPie3Data()
      this.getPie4Data()
      this.getPie5Data()
      this.getPie6Data()
      this.getPie7Data()
    },
    getPie0Data () {
      let account = this.account[0]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData0 = res.data.data
        }
      })
    },
    getPie1Data () {
      let account = this.account[1]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData1 = res.data.data
        }
      })
    },
    getPie2Data () {
      let account = this.account[2]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData2 = res.data.data
        }
      })
    },
    getPie3Data () {
      let account = this.account[3]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData3 = res.data.data
        }
      })
    },
    getPie4Data () {
      let account = this.account[4]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData4 = res.data.data
        }
      })
    },
    getPie5Data () {
      let account = this.account[5]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData5 = res.data.data
        }
      })
    },
    getPie6Data () {
      let account = this.account[6]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData6 = res.data.data
        }
      })
    },
    getPie7Data () {
      let account = this.account[7]
      let bill_cycle = this.billCycle
      BillMonthAccountListApi(account, bill_cycle).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.pieData7 = res.data.data
        }
      })
    }
  }
}
</script>

<style lang="less">
.dashboard-bill-search-con {
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
</style>
