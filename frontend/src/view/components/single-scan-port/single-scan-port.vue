<template>
  <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="100">
    <FormItem label="AK" prop="ak">
      <Input v-model="formValidate.ak" placeholder="Enter the ak of Huawei cloud" class="scan-port-input"></Input>
    </FormItem>
    <FormItem label="SK" prop="sk">
      <Input v-model="formValidate.sk" placeholder="Enter the sk of Huawei cloud" class="scan-port-input"></Input>
    </FormItem>
    <FormItem>
      <Button type="primary" @click="handleSubmit('formValidate')">导出</Button>
      <!--      <Button @click="handleReset('formValidate')" style="margin-left: 8px">Reset</Button>-->
      <Progress :percent="scanPortProgressValue" :stroke-width="28" status="active" :text-inside="true"/>
    </FormItem>
  </Form>
</template>
<script>
import { downloadSingleScanPortExcelApi, queryProgressSingleScanPortApi } from '@/api/tools'
import { blobDownload } from '@/libs/download.js'
import { getStrDate } from '@/libs/tools.js'

export default {
  data () {
    return {
      timer: null,
      scanPortProgressValue: 0,
      formValidate: {
        ak: '',
        sk: ''
      },
      ruleValidate: {
        ak: [
          { required: true, message: 'The ak cannot be empty', trigger: 'blur' }
        ],
        sk: [
          { required: true, message: 'The sk cannot be empty', trigger: 'blur' }
        ]
      }
    }
  },
  beforeDestroy () {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
      this.scanPortProgressValue = 0
    }
  },
  methods: {
    handleSubmit (name) {
      this.$refs[name].validate((valid) => {
        if (valid) {
          let ak = this.formValidate.ak
          let sk = this.formValidate.sk
          this.scanPortProgressValue = 0
          downloadSingleScanPortExcelApi(ak, sk).then(res => {
            if (res.data.err_code !== 0) {
              this.$Message.info(res.data.description)
            } else {
              this.startTimer()
              this.$Message.success('成功')
            }
          })
        } else {
          this.$Message.error('参数错误，请重新输入')
        }
      })
    },
    handleReset (name) {
      this.$refs[name].resetFields()
    },
    queryExcel () {
      let ak = this.formValidate.ak
      let sk = this.formValidate.sk
      queryProgressSingleScanPortApi(ak, sk).then(res => {
        this.scanPortProgressValue = this.scanPortProgressValue + 3
        if (this.scanPortProgressValue > 99) {
          this.scanPortProgressValue = 99
        }
        if (res.headers['content-type'] === 'application/octet-stream') {
          let strDate = getStrDate()
          const fileName = 'IP端口扫描统计表_' + strDate + '.xlsx'
          blobDownload(res.data, fileName)
          if (this.timer) {
            clearInterval(this.timer)
            this.timer = null
            this.scanPortProgressValue = 100
          }
        }
      })
    },
    startTimer () {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      this.timer = setInterval(() => {
        setTimeout(this.queryExcel, 0)
      }, 3000)
    }
  }
}
</script>
<style>
.ivu-progress-outer {
  margin-top: 32px;
}

.scan-port-input {
  width: 500px;
}
</style>
