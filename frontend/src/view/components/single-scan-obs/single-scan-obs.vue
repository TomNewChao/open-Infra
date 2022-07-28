<template>
  <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="100">
    <FormItem label="ACCOUNT" prop="account">
      <Input v-model="formValidate.account" placeholder="Enter the account of Huawei cloud"></Input>
    </FormItem>
    <FormItem label="AK" prop="ak">
      <Input v-model="formValidate.ak" placeholder="Enter the ak of Huawei cloud"></Input>
    </FormItem>
    <FormItem label="SK" prop="sk">
      <Input v-model="formValidate.sk" placeholder="Enter the sk of Huawei cloud"></Input>
    </FormItem>
    <FormItem>
      <Button type="primary" @click="handleSubmit('formValidate')">Submit</Button>
      <Button @click="handleReset('formValidate')" style="margin-left: 8px">Reset</Button>
      <Progress :percent="progressValue" :stroke-width="32" status="active" :text-inside="true" CLASS="progress"/>
    </FormItem>
  </Form>
</template>
<script>
import { downloadSingleScanObsExcelApi, queryProgressSingleScanObsApi } from '@/api/tools'
import { blobDownload } from '@/libs/download.js'
import { getStrDate } from '@/libs/tools.js'

export default {
  data () {
    return {
      timer: null,
      progressValue: 0,
      formValidate: {
        ak: '',
        sk: '',
        account: ''
      },
      ruleValidate: {
        ak: [
          { required: true, message: 'The ak cannot be empty', trigger: 'blur' }
        ],
        sk: [
          { required: true, message: 'The sk cannot be empty', trigger: 'blur' }
        ],
        account: [
          { required: true, message: 'The account cannot be empty', trigger: 'blur' }
        ]
      }
    }
  },
  beforeDestroy () {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
      this.loading = false
      this.progressValue = 0
    }
  },
  methods: {
    handleSubmit (name) {
      this.$refs[name].validate((valid) => {
        if (valid) {
          let ak = this.formValidate.ak
          let sk = this.formValidate.sk
          let account = this.formValidate.account
          downloadSingleScanObsExcelApi(ak, sk, account).then(res => {
            if (res.data.err_code !== 0) {
              this.$Message.info(res.data.description)
            } else {
              this.startTimer()
              this.loading = true
              this.$Message.success('Success')
            }
          })
        } else {
          this.$Message.error('Fail')
        }
      })
    },
    handleReset (name) {
      this.$refs[name].resetFields()
    },
    queryExcel () {
      let ak = this.formValidate.ak
      let sk = this.formValidate.sk
      let account = this.formValidate.account
      queryProgressSingleScanObsApi(ak, sk, account).then(res => {
        this.progressValue = this.progressValue + 3
        if (this.progressValue > 99) {
          this.progressValue = 99
        }
        console.log(res.headers)
        if (res.headers['content-type'] === 'application/octet-stream') {
          console.log('aaaaaaaaaaaaaaaaaaaaaaaaaa')
          console.log(res.data)
          let strDate = getStrDate()
          const fileName = 'IP端口扫描统计表_' + strDate + '.xlsx'
          blobDownload(res.data, fileName)
          if (this.timer) {
            clearInterval(this.timer)
            this.timer = null
            this.loading = false
            this.progressValue = 100
          }
        }
      })
    },
    startTimer () {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
        this.progressValue = 0
      }
      this.timer = setInterval(() => {
        setTimeout(this.queryExcel, 0)
      }, 3000)
    }
  }
}
</script>
<style>
.progress {
  margin-top: 20px;
}

</style>
