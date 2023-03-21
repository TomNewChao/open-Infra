<template>
  <div>
    <Card>
      <div class="service-info-search-con search-con-top">
        <Select v-model="searchKeyServiceInfo" class="search-col">
          <Option v-for="item in searchColumnsServiceInfo" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="searchValueServiceInfo"/>
        <Button @click="handleServiceInfoSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
        <Button type="primary" @click="handleSla" class="sla-export">导出SLA数据</Button>
      </div>
      <Drawer
        class="serviceDetail"
        title="服务详情"
        v-model="isServiceDetail"
        width="60%"
        :mask-closable="false"
      >
        <Form :model="serviceDetail">
          <h3>服务信息</h3>
          <Row :gutter="32" class="detail-info">
            <Col span="12">
              <FormItem label="服务名称:">
                <label v-text="serviceDetail.service_name"></label>
              </FormItem>
              <FormItem label="命名空间:">
                <label v-text="serviceDetail.namespace"></label>
              </FormItem>
              <FormItem label="集群名称:">
                <label v-text="serviceDetail.cluster"></label>
              </FormItem>
              <FormItem label="区域:">
                <label v-text="serviceDetail.region"></label>
              </FormItem>
            </Col>
          </Row>
          <h3>服务SLA</h3>
          <Row :gutter="32" class="detail-sla">
            <tables ref="tables" search-place="top" :stripe=true v-model="serviceDetail.service_sla"
                    :columns="columnsSlaInfo"/>
          </Row>
          <h3>服务镜像</h3>
          <Row :gutter="32">
            <tables ref="tables" search-place="top" :stripe=true v-model="serviceDetail.service_image"
                    :columns="columnsImageInfo"/>
          </Row>
        </Form>
      </Drawer>
      <tables ref="tables" search-place="top" :stripe=true v-model="tableDataServiceInfo" :columns="columnsServiceInfo"
              @on-filter-change="handleServiceFilter"
              @on-sort-change="handleServiceInfoSort"
              @on-row-click="handleRowClick"/>
      <Page :total="pageTotalServiceInfo" :current="pageNumServiceInfo" :page-size="pageSizeServiceInfo" :pageSizeOpts="pageSizeOpts"
            show-sizer show-total
            @on-change="handleServiceInfoPage"
            @on-page-size-change="handleServiceInfoPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import {
  exportSlaData,
  ServiceClusterListApi,
  ServiceInfoListApi,
  ServiceDetailApi,
  ServiceRegionListApi
} from '@/api/tools'
import { getStrDate } from '@/libs/tools'
import { blobDownload } from '@/libs/download'

export default {
  name: 'service_info',
  components: {
    Tables
  },
  data () {
    return {
      pageSizeOpts: [10, 20, 50],
      searchKeyServiceInfo: '',
      searchValueServiceInfo: '',
      searchColumnsServiceInfo: [
        { title: '服务名称', key: 'service_name' },
        { title: '代码仓', key: 'repository' },
        { title: '基础镜像', key: 'base_image' },
        { title: '基础系统', key: 'base_os' }
      ],
      orderByServiceInfo: 'service_name',
      orderTypeServiceInfo: 1,
      pageNumServiceInfo: 1,
      pageSizeServiceInfo: 10,
      pageTotalServiceInfo: 10,
      ServiceCluster: '',
      ServiceRegion: '',
      isServiceDetail: false,
      serviceDetail: {},
      columnsServiceInfo: [
        { title: '服务名称', key: 'service_name', sortable: 'custom' },
        { title: '命名空间', key: 'namespace' },
        {
          title: '集群名称',
          key: 'cluster',
          filters: [],
          filterMultiple: false,
          filterMethod (value, row) {
            return value
          }
        },
        {
          title: '区域',
          key: 'region',
          filters: [],
          filterMultiple: false,
          filterMethod (value, row) {
            return value
          }
        },
        { title: '镜像', key: 'image' },
        { title: '代码仓', key: 'repository' },
        { title: '基础镜像', key: 'base_image' },
        { title: '基础系统', key: 'base_os' }
      ],
      columnsSlaInfo: [
        { title: '域名', key: 'url', sortable: 'custom' },
        { title: '别名', key: 'service_alias' },
        { title: '介绍', key: 'service_introduce' },
        { title: '社区', key: 'service_zone' },
        { title: '月度异常时间min', key: 'month_abnormal_time' },
        { title: '年度异常时间min', key: 'year_abnormal_time' },
        { title: '月度sla', key: 'month_sla' },
        { title: '年度sla', key: 'year_sla' },
        { title: '年度剩余sla', key: 'remain_time' }
      ],
      columnsImageInfo: [
        { title: '路径', key: 'image' },
        { title: '仓库', key: 'repository' },
        { title: '分支', key: 'branch' },
        { title: '开发者', key: 'developer' },
        { title: '邮箱', key: 'email' },
        { title: '基础镜像', key: 'base_image' },
        { title: '操作系统', key: 'base_os' },
        { title: '流水线', key: 'pipline_url' },
        { title: '镜像大小', key: 'num_download' },
        { title: '下载次数', key: 'size', sortable: 'custom' },
        { title: 'cpu限制', key: 'cpu_limit', sortable: 'custom' },
        { title: '内存限制', key: 'mem_limit', sortable: 'custom' }
      ],
      tableDataServiceInfo: []
    }
  },
  mounted () {
    this.handleServiceInfoList()
    this.handleServiceClusterItem()
    this.handleServiceRegionItem()
  },
  methods: {
    handleServiceInfoSearch () {
      this.handleServiceInfoList()
    },
    handleServiceInfoPage (value) {
      this.pageNumServiceInfo = value
      this.handleServiceInfoList()
    },
    handleServiceInfoPageSize (value) {
      this.pageSizeServiceInfo = value
      this.handleServiceInfoList()
    },
    handleServiceInfoSort (column) {
      this.orderByServiceInfo = column.key
      this.orderTypeServiceInfo = column.order === 'asc' ? 0 : 1
      this.handleServiceInfoList()
    },
    handleServiceInfoList () {
      ServiceInfoListApi(this.pageNumServiceInfo, this.pageSizeServiceInfo, this.orderByServiceInfo,
        this.orderTypeServiceInfo, this.searchKeyServiceInfo, this.searchValueServiceInfo,
        this.ServiceCluster, this.ServiceRegion).then(res => {
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
    handleSla () {
      exportSlaData().then(res => {
        if (res.headers['content-type'] === 'application/octet-stream') {
          let strDate = getStrDate()
          const fileName = 'Sla数据统计表_' + strDate + '.xlsx'
          blobDownload(res.data, fileName)
        }
      })
    },
    handleServiceClusterItem () {
      ServiceClusterListApi().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.columnsServiceInfo[2].filters = res.data.data
        }
      })
    },
    handleServiceRegionItem () {
      ServiceRegionListApi().then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.columnsServiceInfo[3].filters = res.data.data
        }
      })
    },
    handleServiceFilter (value) {
      if (value.key === 'cluster') {
        this.ServiceCluster = value._filterChecked[0]
      } else if (value.key === 'region') {
        this.ServiceRegion = value._filterChecked[0]
      }
      this.handleServiceInfoList()
    },
    handleRowClick (row, index) {
      const id = row.id
      ServiceDetailApi(id).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.serviceDetail = res.data.data
          this.isServiceDetail = true
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

.serviceDetail {
  height: calc(100% - 55px);
  overflow: auto;
  paddingBottom: 53px;
  position: static
}

.detail-info {
  margin-bottom: 20px;
}

.detail-sla {
  margin-bottom: 30px;
}

.ivu-form-item {
  margin-bottom: 5px;
}
</style>
