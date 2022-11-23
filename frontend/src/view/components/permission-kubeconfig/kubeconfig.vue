<template>
  <div>
    <Card>
      <Button class="ivu-btn-one" @click="getKubeConfig" type="primary">+修改KubeConfig</Button>
      <Button class="ivu-btn-second" @click="deleteKubeConfig" type="primary">-删除KubeConfig</Button>
      <Drawer
        title="修改KubeConfig"
        v-model="kubeConfigDrawerValue"
        width="720"
        :mask-closable="false"
        :styles="kubeConfigDrawerStyles"
      >
        <Form :model="kubeConfigFormData">
          <Row :gutter="32">
            <Col span="12">
              <FormItem label="用户名:" label-position="top">
                <label v-text="kubeConfigFormData.username"></label>
              </FormItem>
              <FormItem label="邮箱:" label-position="top">
                <label v-text="kubeConfigFormData.email"></label>
              </FormItem>
              <FormItem label="服务名:" label-position="top">
                <label v-text="kubeConfigFormData.service_name"></label>
              </FormItem>
              <FormItem label="角色" label-position="top">
                <RadioGroup v-model="kubeConfigFormData.role">
                  <Radio label="admin"></Radio>
                  <Radio label="developer"></Radio>
                  <Radio label="viewer"></Radio>
                </RadioGroup>
              </FormItem>
              <FormItem label="过期天数(单位：天)" label-position="top">
                <Input v-model="kubeConfigFormData.expired_time" placeholder="请输入过期天数"/>
              </FormItem>
            </Col>
          </Row>
        </Form>
        <div class="alarm-email-drawer-footer">
          <Button style="margin-right: 8px" @click="clearKubeConfigContent">Cancel</Button>
          <Button type="primary" @click="putKubeConfig">Submit</Button>
        </div>
      </Drawer>

      <div class="kube-config-search-con search-con-top">
        <Select v-model="kubeConfigSearchKey" class="search-col">
          <Option v-for="item in kubeConfigFilterColumns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="alarmEmailSearchValue"/>
        <Button @click="kubeConfigSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
      </div>
      <Table border ref="selection" search-place="top" :data="kubeConfigTableData" :columns="kubeConfigColumns"
             @on-sort-change="kubeConfigSort"/>
      <Page show-sizer show-total :total="kubeConfigPageTotal" :current="kubeConfigPageNum"
            :page-size="kubeConfigPageSize"
            @on-change="handlerKubeConfigPage"
            @on-page-size-change="handlerKubeConfigPageSize"/>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import './index.less'
import {
  kubeConfigDeletePostApi, kubeConfigGetApi,
  kubeConfigListApi, kubeConfigPutApi,
} from '@/api/tools'

export default {
  name: 'tables_page',
  components: {
    Tables
  },
  data() {
    return {
      putSelectId: 0,
      kubeConfigDrawerValue: false,
      kubeConfigDrawerStyles: {
        height: 'calc(100% - 55px)',
        overflow: 'auto',
        paddingBottom: '53px',
        position: 'static'
      },
      kubeConfigFormData: {
        username: '',
        email: '',
        service_name: '',
        role: '',
        expired_time: ''
      },
      RoleList : [
        {"name": "admin" , "value": "admin"},
        {"name": "developer" , "value": "developer"},
        {"name": "viewer" , "value": "viewer"},
      ],
      kubeConfigSearchKey: '',
      alarmEmailSearchValue: '',
      kubeConfigPageTotal: 0,
      kubeConfigPageNum: 1,
      kubeConfigPageSize: 10,
      kubeConfigOrderBy: 'create_time',
      kubeConfigOrderType: 1,
      kubeConfigFilterColumns: [
        {title: '用户名', key: 'username'},
        {title: '邮件', key: 'email'},
        {title: '服务名', key: 'service_name'},
        {title: '角色', key: 'role'},
        {title: '执行结果', key: 'send_ok'},
      ],
      kubeConfigColumns: [
        {
          type: 'selection',
          width: 60,
          align: 'center'
        },
        {title: '用户名', key: 'username'},
        {title: '邮件', key: 'email'},
        {title: '服务名', key: 'service_name'},
        {title: '角色', key: 'role'},
        {title: '执行结果', key: 'send_ok'},
        {title: '过期天数', key: 'expired_time', sortable: 'custom'},
        {title: '创建时间', key: 'create_time', sortable: 'custom', sortType: "desc"},
        {title: '审核时间', key: 'review_time', sortable: 'custom'},
        {title: '修改时间', key: 'modify_time', sortable: 'custom'}
      ],
      kubeConfigTableData: []
    }
  },
  mounted() {
    this.queryKubeConfigList()
  },
  methods: {
    kubeConfigSort(column) {
      this.kubeConfigOrderBy = column.key
      this.kubeConfigOrderType = column.order === "asc" ? 0 : 1
      this.queryKubeConfigList()
    },
    kubeConfigSearch() {
      this.queryKubeConfigList()
    },
    handlerKubeConfigPage(value) {
      this.kubeConfigPageNum = value
      this.queryKubeConfigList()
    },
    handlerKubeConfigPageSize(value) {
      this.kubeConfigPageSize = value
      this.queryKubeConfigList()
    },

    clearKubeConfigContent() {
      this.kubeConfigDrawerValue = false
      this.kubeConfigFormData.username = ''
      this.kubeConfigFormData.email = ''
      this.kubeConfigFormData.service_name = ''
      this.kubeConfigFormData.role = ''
      this.kubeConfigFormData.expired_time = ''
    },

    queryKubeConfigList() {
      kubeConfigListApi(this.kubeConfigPageNum, this.kubeConfigPageSize, this.kubeConfigOrderBy,
        this.kubeConfigOrderType, this.kubeConfigSearchKey, this.alarmEmailSearchValue).then(res => {
        if (res.data.err_code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          this.kubeConfigTableData = res.data.data.data
          this.kubeConfigPageTotal = res.data.data.total
          this.kubeConfigPageNum = res.data.data.page
          this.kubeConfigPageSize = res.data.data.size
        }
      })
    },

    deleteKubeConfig() {
      let selectKubeConfigArray = this.$refs.selection.getSelection()
      let selectKubeConfigList = []
      for (let i = 0; i < selectKubeConfigArray.length; i++) {
        selectKubeConfigList.push(selectKubeConfigArray[i].id)
      }
      if (selectKubeConfigList.length === 0) {
        this.$Message.info('请至少选择一条信息。')
      } else {
        kubeConfigDeletePostApi(selectKubeConfigList).then(res => {
          if (res.data.err_code === 0) {
            this.queryKubeConfigList()
          }
          this.$Message.info(res.data.description)
        })
      }
    },

    getKubeConfig() {
      let selectKubeConfigArray = this.$refs.selection.getSelection()
      let selectKubeConfigList = []
      for (let i = 0; i < selectKubeConfigArray.length; i++) {
        selectKubeConfigList.push(selectKubeConfigArray[i].id)
      }
      if (selectKubeConfigList.length === 0) {
        this.$Message.info('请至少选择一条信息。')
      } else if (selectKubeConfigList.length > 1) {
        this.$Message.info('只能选择一条信息进行修改。')
      } else {
        let id = selectKubeConfigList[0]
        kubeConfigGetApi(id).then(res => {
          if (res.data.err_code !== 0) {
            this.$Message.info(res.data.description)
          } else {
            let respData = res.data.data
            this.putSelectId = respData.id
            this.kubeConfigFormData.username = respData.username
            this.kubeConfigFormData.email = respData.email
            this.kubeConfigFormData.service_name = respData.service_name
            this.kubeConfigFormData.role = respData.role
            this.kubeConfigFormData.expired_time = respData.expired_time
            this.kubeConfigDrawerValue = true
          }
        })
      }
    },

    putKubeConfig() {
      let expired_time = this.kubeConfigFormData.expired_time
      let role = this.kubeConfigFormData.role
      let id = this.putSelectId
      kubeConfigPutApi(expired_time, role, id).then(res => {
        if (res.data.err_code === 0) {
          this.queryKubeConfigList()
        }
        this.$Message.info(res.data.description)
      })
      this.putSelectId = 0
      this.clearKubeConfigContent()

    }
  }
}
</script>
<style>
.ivu-page {
  margin-top: 30px;
  text-align: center;
}

.alarm-email-drawer-footer {
  width: 100%;
  position: absolute;
  bottom: 0;
  left: 0;
  border-top: 1px solid #e8e8e8;
  padding: 10px 16px;
  text-align: right;
  background: #fff;
}

.ivu-btn-one {
  margin-left: 1px;
}

.ivu-btn-second {
  margin-left: 20px;
}


</style>
