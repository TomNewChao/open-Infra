<template>
  <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="100">
    <FormItem label="PROJECT_ID" prop="project_id">
      <Input v-model="formValidate.project_id" placeholder="Enter the project id of Huawei cloud"></Input>
    </FormItem>
    <FormItem label="ZONE" prop="zone">
      <Input v-model="formValidate.zone" placeholder="Enter the zone of Huawei cloud"></Input>
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
import { downloadSingleScanPortExcelApi, queryProgressSingleScanPortApi } from '@/api/tools'
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
        project_id: '',
        zone: ''
      },
      ruleValidate: {
        ak: [
          { required: true, message: 'The ak cannot be empty', trigger: 'blur' }
        ],
        sk: [
          { required: true, message: 'The sk cannot be empty', trigger: 'blur' }
        ],
        project_id: [
          { required: true, message: 'The project_id cannot be empty', trigger: 'blur' }
        ],
        zone: [
          { required: true, message: 'The zone cannot be empty', trigger: 'blur' }
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
          let project_id = this.formValidate.project_id
          let zone = this.formValidate.zone
          downloadSingleScanPortExcelApi(ak, sk, project_id, zone).then(res => {
            if (res.data.err_code !== 0) {
              this.$Message.info(res.data.description)
            } else {
              this.startTimer()
              this.loading = true
              this.$Message.success('Success')
            }
          })
        } else {
          this.$Message.error('Param fault')
        }
      })
    },
    handleReset (name) {
      this.$refs[name].resetFields()
    },
    queryExcel () {
      let ak = this.formValidate.ak
      let sk = this.formValidate.sk
      let project_id = this.formValidate.project_id
      let zone = this.formValidate.zone
      queryProgressSingleScanPortApi(ak, sk, project_id, zone).then(res => {
        this.progressValue = this.progressValue + 3
        if (this.progressValue > 99) {
          this.progressValue = 99
        }
        if (res.headers['content-type'] === 'application/octet-stream') {
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
