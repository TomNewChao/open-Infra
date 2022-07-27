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
    </FormItem>
  </Form>
</template>
<script>
  import {scanPortApi, downloadScanPortExcelApi, queryProgressScanPortApi} from '@/api/tools';
  import {blobDownload} from '@/libs/download.js';
  export default {
    data() {
      return {
        formValidate: {
          ak: '',
          sk: '',
          account: '',
        },
        ruleValidate: {
          ak: [
            {required: true, message: 'The ak cannot be empty', trigger: 'blur'}
          ],
          sk: [
            {required: true, message: 'The sk cannot be empty', trigger: 'blur'}
          ],
          account: [
            {required: true, message: 'The account cannot be empty', trigger: 'blur'}
          ]
        }
      }
    },
    methods: {
      handleSubmit(name) {
        this.$refs[name].validate((valid) => {
          if (valid) {
            this.$Message.success('Success!');
          } else {
            this.$Message.error('Fail!');
          }
        })
      },
      handleReset(name) {
        this.$refs[name].resetFields();
      },
      exportExcel() {
        let selectName = [];
        for (let i = 0; i < this.tableData.length; i++) {
          selectName.push(this.tableData[i].account)
        }
        if (selectName.length === 0) {
          this.$Message.info('请至少选择一个Account。');
        } else {
          downloadScanPortExcelApi(selectName).then(res => {
            if (res.data.err_code !== 0) {
              this.$Message.info(res.data.description)
            } else {
              this.startTimer();
              this.loading = true
            }
          })
        }
      },
      queryExcel() {
        queryProgressScanPortApi().then(res => {
          if (res.headers['content-type'] === 'application/octet-stream') {
            let strDate = getStrDate();
            const fileName = "IP端口扫描统计表_" + strDate + ".xlsx";
            blobDownload(res.data, fileName);
            if (this.timer) {
              clearInterval(this.timer);
              this.timer = null;
              this.loading = false
            }
          }
        })
      },
      scanPort() {
        scanPortApi().then(res => {
          this.tableData = res.data.data
        })
      },
      startTimer() {
        if (this.timer) {
          clearInterval(this.timer);
          this.timer = null
        }
        this.timer = setInterval(() => {
          setTimeout(this.queryExcel, 0)
        }, 3000)
      }
    }
  }
</script>
