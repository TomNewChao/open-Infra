<template>
  <div>
    <Card>
      <Button @click="queryAlarmName" type="primary">+增加邮箱</Button>
      <Button class="ivu-btn-second" @click="deleteAlarmEmail" type="primary">-删除邮箱</Button>
      <Drawer
        title="添加邮箱"
        v-model="alarmEmailDrawerValue"
        width="720"
        :mask-closable="false"
        :styles="alarmEmailDrawerStyles"
      >
        <Form :model="alarmEmailFormData">
          <Row :gutter="32">
            <Col span="12">
              <FormItem label="邮件" label-position="top">
                <Input v-model="alarmEmailFormData.email" placeholder="请输入邮件"/>
              </FormItem>
              <FormItem label="手机号码" label-position="top">
                <Input v-model="alarmEmailFormData.phoneNumber" placeholder="请输入手机号码"/>
              </FormItem>
              <FormItem label="报警名称" label-position="top">
                <Select v-model="alarmEmailFormData.alarmName" multiple style="width:600px" placeholder="请选择报警名称">
                  <Option v-for="item in alarmNameItem" :value="item.id" :key="item.id">{{ item.name }}</Option>
                </Select>
              </FormItem>
            </Col>
          </Row>
          <FormItem label="报警详细信息关键字" label-position="top">
            <Input v-model="alarmEmailFormData.alarmKeywords"
                   placeholder="请输入报警详细信息关键字:   为空代表监控选中报警名称的所有报警"/>
          </FormItem>
          <FormItem label="备注" label-position="top">
            <Input type="textarea" v-model="alarmEmailFormData.desc" :rows="4"
                   placeholder="请输入备注信息"/>
          </FormItem>
        </Form>
        <div class="alarm-email-drawer-footer">
          <Button style="margin-right: 8px" @click="clearAlarmEmailContent">Cancel</Button>
          <Button type="primary" @click="createAlarmEmail">Submit</Button>
        </div>
      </Drawer>
      <div class="alarm-email-search-con search-con-top">
        <Select v-model="alarmEmailSearchKey" class="search-col">
          <Option v-for="item in alarmEmailFilterColumns" :value="item.key" :key="item.key">{{ item.title }}</Option>
        </Select>
        <Input clearable placeholder="输入关键字搜索" class="search-input" v-model="alarmEmailSearchValue"/>
        <Button @click="handlerAlarmEmailSearch" class="search-btn" type="primary">
          <Icon type="search"/>&nbsp;&nbsp;搜索
        </Button>
      </div>
      <Table border ref="selection" search-place="top" :data="alarmEmailTableData" :columns="alarmEmailColumns" @on-sort-change="handlerAlarmEmailSort"/>
      <Page :total="alarmEmailPageTotal" :current="alarmEmailPageNum" :page-size="alarmEmailPageSize" show-sizer
            show-total @on-change="handlerAlarmEmailPage"
            @on-page-size-change="handlerAlarmEmailPageSize"/>
    </Card>
  </div>
</template>

<script>
  import Tables from '_c/tables'
  import './index.less'
  import {alarmEmailDeletePostApi, alarmEmailListApi, alarmEmailPostApi} from '@/api/tools'
  import {getStrDate} from "@/libs/tools";

  export default {
    name: 'tables_page',
    components: {
      Tables
    },
    data() {
      return {
        alarmEmailDrawerValue: false,
        alarmEmailDrawerStyles: {
          height: 'calc(100% - 55px)',
          overflow: 'auto',
          paddingBottom: '53px',
          position: 'static'
        },
        alarmEmailFormData: {
          email: '',
          phoneNumber: '',
          alarmName: '',
          alarmKeywords: '',
          desc: ''
        },
        alarmNameItem : [],
        alarmEmailSearchKey: '',
        alarmEmailSearchValue: '',
        alarmEmailPageTotal: 0,
        alarmEmailPageNum: 1,
        alarmEmailPageSize: 10,
        alarmEmailOrderBy: 'create_time',
        alarmEmailOrderType: 1,
        alarmEmailFilterColumns: [
          {title: '邮件', key: 'email'},
          {title: '报警名称', key: 'alarm_name'},
          {title: '报警详细关键字', key: 'alarm_detail_keywords'},
        ],
        alarmEmailColumns: [
          {
            type: 'selection',
            width: 60,
            align: 'center'
          },
          {title: '邮件', key: 'email', sortable: 'custom'},
          {title: '手机号', key: 'phone_number'},
          {title: '报警名称', key: 'alarm_name'},
          {title: '报警详细关键字', key: 'alarm_detail_keywords'},
          {title: '备注', key: 'desc'},
          {title: '创建时间', key: 'create_time', sortable: 'custom', sortType: "desc"}
        ],
        alarmEmailTableData: []
      }
    },
    mounted() {
      this.queryAlarmEmailList()
    },
    methods: {
      handlerAlarmEmailSort(column){
        this.alarmEmailOrderBy = column.key
        this.alarmEmailOrderType = column.order === "asc" ? 0:1
        this.queryAlarmEmailList()
      },
      handlerAlarmEmailSearch() {
        this.queryAlarmEmailList()
      },
      handlerAlarmEmailPage(value) {
        this.alarmEmailPageNum = value
        this.queryAlarmEmailList()
      },
      handlerAlarmEmailPageSize(value) {
        this.alarmEmailPageSize = value
        this.queryAlarmEmailList()
      },
      queryAlarmEmailList() {
        alarmEmailListApi(this.alarmEmailPageNum, this.alarmEmailPageSize, this.alarmEmailOrderBy, this.alarmEmailOrderType, this.alarmEmailSearchKey, this.alarmEmailSearchValue).then(res => {
          if (res.data.err_code !== 0) {
            this.$Message.info(res.data.description)
          } else {
            this.alarmEmailTableData = res.data.data.data
            this.alarmEmailPageTotal = res.data.data.total
            this.alarmEmailPageNum = res.data.data.page
            this.alarmEmailPageSize = res.data.data.size
          }
        })
      },
      queryAlarmName(){
        // check data
        this.alarmEmailDrawerValue = true

      },
      createAlarmEmail() {
        let email = this.alarmEmailFormData.email
        let desc = this.alarmEmailFormData.desc
        alarmEmailPostApi(email, desc).then(res => {
          if (res.data.err_code === 0) {
            this.queryAlarmEmailList()
          }
          this.$Message.info(res.data.description)
        })
        this.alarmEmailDrawerValue = false
        this.alarmEmailFormData.email = ''
        this.alarmEmailFormData.desc = ''
      },
      clearAlarmEmailContent() {
        this.alarmEmailDrawerValue = false
        this.alarmEmailFormData.email = ''
        this.alarmEmailFormData.desc = ''
      },
      deleteAlarmEmail() {
        let selectEmailArray = this.$refs.selection.getSelection()
        let selectEmailList = []
        for (let i = 0; i < selectEmailArray.length; i++) {
          selectEmailList.push(selectEmailArray[i].email)
        }
        if (selectEmailList.length === 0) {
          this.$Message.info('请至少选择一个邮箱。')
        } else {
          alarmEmailDeletePostApi(selectEmailList).then(res => {
            if (res.data.err_code === 0) {
              this.queryAlarmEmailList()
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

  .ivu-btn-second {
    margin-left: 20px;
  }
</style>
