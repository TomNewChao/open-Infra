<template>
  <div>
    <Card>
      <Button @click="highRiskPortDrawerValue = true" type="primary">+增加高危端口</Button>
      <Button class="ivu-btn-second" @click="deleteHighRiskPort" type="primary">-删除高危端口</Button>
      <Drawer
        title="增加高危端口"
        v-model="highRiskPortDrawerValue"
        width="720"
        :mask-closable="false"
        :styles="highRiskPortDrawerStyles"
      >
        <Form :model="highRiskPortFormData">
          <Row :gutter="32">
            <Col span="12">
              <FormItem label="port" label-position="top">
                <Input v-model="highRiskPortFormData.port" placeholder="please enter port"/>
              </FormItem>
            </Col>
          </Row>
          <FormItem label="Description" label-position="top">
            <Input type="textarea" v-model="highRiskPortFormData.desc" :rows="4"
                   placeholder="please enter the description"/>
          </FormItem>
        </Form>
        <div class="high-risk-port-drawer-footer">
          <Button style="margin-right: 8px" @click="clearHighRiskPortContent">Cancel</Button>
          <Button type="primary" @click="createHighRiskPort">Submit</Button>
        </div>
      </Drawer>
      <div class="high-risk-search-con search-con-top">
        <Select v-model="highRiskPortSearchKey" class="search-col">
          <Option v-for="item in highRiskPortFilterColumns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="highRiskPortSearchValue"/>
        <Button @click="handleHighRiskSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
      </div>
      <Table border ref="selection" search-place="top" :data="highRiskPortTableData" :columns="highRiskColumns"/>
      <Page :total="highRiskPortPageTotal" :current="highRiskPortPageNum" :page-size="highRiskPortPageSize" show-sizer
            show-total @on-change="handlerHighRiskPage"
            @on-page-size-change="handlerHighRiskPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import {downloadScanObsExcelApi, highRiskPortApiDeletePost, highRiskPortApiList, highRiskPortApiPost} from '@/api/tools'
import {getStrDate} from "@/libs/tools";
import {blobDownload} from "@/libs/download";

export default {
  name: 'tables_page',
  components: {
    Tables
  },
  data() {
    return {
      highRiskPortDrawerValue: false,
      highRiskPortDrawerStyles: {
        height: 'calc(100% - 55px)',
        overflow: 'auto',
        paddingBottom: '53px',
        position: 'static'
      },
      highRiskPortFormData: {
        port: '',
        desc: ''
      },
      highRiskPortSearchKey: '',
      highRiskPortSearchValue: '',
      highRiskPortPageTotal: 10,
      highRiskPortPageNum: 1,
      highRiskPortPageSize: 10,
      highRiskPortOrderBy: 'create_time',
      highRiskPortOrderType: '1',
      highRiskPortFilterColumns: [
        {title: 'port', key: 'port'}
      ],
      highRiskColumns: [
        {
          type: 'selection',
          width: 60,
          align: 'center'
        },
        {title: 'port', key: 'port', sortable: true},
        {title: 'desc', key: 'desc'},
        {title: 'create_time', key: 'create_time', sortable: true}
      ],
      highRiskPortTableData: []
    }
  },
  mounted() {
    this.queryHighRiskPortList()
  },
  methods: {
    handleHighRiskSearch() {
      this.queryHighRiskPortList()
    },
    handlerHighRiskPage(value) {
      this.highRiskPortPageNum = value
      this.queryHighRiskPortList()
    },
    handlerHighRiskPageSize(value) {
      this.highRiskPortPageSize = value
      this.queryHighRiskPortList()
    },
    queryHighRiskPortList() {
      highRiskPortApiList(this.highRiskPortPageNum, this.highRiskPortPageSize, this.highRiskPortOrderBy, this.highRiskPortOrderType, this.highRiskPortSearchKey, this.highRiskPortSearchValue).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.highRiskPortTableData = res.data.data.data
          this.highRiskPortPageTotal = res.data.data.total
          this.highRiskPortPageNum = res.data.data.page
          this.highRiskPortPageSize = res.data.data.size
        }
      })
    },
    createHighRiskPort() {
      let port = this.highRiskPortFormData.port
      let desc = this.highRiskPortFormData.desc
      highRiskPortApiPost(port, desc).then(res => {
        if (res.data.err_code === 0) {
          this.queryHighRiskPortList()
        }
        this.$Message.info(res.data.description)
      })
      this.highRiskPortDrawerValue = false
      this.highRiskPortFormData.port = ''
      this.highRiskPortFormData.desc = ''
    },
    clearHighRiskPortContent() {
      this.highRiskPortDrawerValue = false
      this.highRiskPortFormData.port = ''
      this.highRiskPortFormData.desc = ''
    },
    deleteHighRiskPort(){
      let selectPortArray = this.$refs.selection.getSelection()
      let selectPortList = []
      for (let i = 0; i < selectPortArray.length; i++) {
        selectPortList.push(selectPortArray[i].port)
      }
      if (selectPortList.length === 0) {
        this.$Message.info('请至少选择一个Port。')
      } else {
        highRiskPortApiDeletePost(selectPortList).then(res => {
          if (res.data.err_code === 0) {
            this.queryHighRiskPortList()
          }
          this.$Message.info(res.data.description)
        })
      }
    }
  }
}
</script>
<style>
.ivu-page {
  margin-top: 30px;
  text-align: center;
}

.high-risk-port-drawer-footer {
  width: 100%;
  position: absolute;
  bottom: 0;
  left: 0;
  border-top: 1px solid #e8e8e8;
  padding: 10px 16px;
  text-align: right;
  background: #fff;
}

.ivu-btn-second{
  margin-left: 20px;
}
</style>
