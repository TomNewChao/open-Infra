<template>
  <div>
    <el-form :model="dynamicValidateForm" ref="dynamicValidateForm" label-width="100px" class="demo-dynamic">
      <el-form-item v-for="(account, index) in dynamicValidateForm.account" :label="'账户' + index + ':'"
                    :key="account.key"
                    :prop="'account.' + index" :rules="{required: true, message: '账户信息不能为空', trigger: 'blur'}">
        <div class="demo-input-suffix">
          AK：
          <el-input v-model="account.ak">AK</el-input>
          SK:
          <el-input v-model="account.sk">SK</el-input>
          Project_id:
          <el-input v-model="account.project_id">SK</el-input>
          Zone:
          <el-input v-model="account.zone">SK</el-input>
        </div>
        <el-button @click.prevent="removeDomain(account)">删除</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('dynamicValidateForm')">下载</el-button>
        <el-button @click="addDomain">新增账户信息</el-button>
        <el-button @click="resetForm('dynamicValidateForm')">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
export default {
  data () {
    return {
      dynamicValidateForm: {
        account: [{
          ak: '',
          sk: '',
          project_id: '',
          zone: ''
        }]
      }
    }
  },
  methods: {
    submitForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          alert('submit!')
        } else {
          console.log('参数不合法，请重新检查！')
          return false
        }
      })
    },

    resetForm (formName) {
      this.$refs[formName].resetFields()
    },

    removeDomain (item) {
      var index = this.dynamicValidateForm.account.indexOf(item)
      if (index !== -1) {
        this.dynamicValidateForm.account.splice(index, 1)
      }
    },

    addDomain () {
      this.dynamicValidateForm.account.push({
        account: [{
          ak: '',
          sk: '',
          project_id: '',
          zone: ''
        }]
      })
    }
  } }
</script>

<style>
  .el-row {
    margin-bottom: 20px;

  &
  :last-child {
    margin-bottom: 0;
  }

  }
  .el-col {
    border-radius: 20px;
  }

  .bg-purple-dark {
    background: #99a9bf;
  }

  .bg-purple {
    background: #d3dce6;
  }

  .bg-purple-light {
    background: #e5e9f2;
  }

  .grid-content {
    border-radius: 4px;
    min-height: 36px;
  }

  .row-bg {
    padding: 10px 0;
    background-color: #f9fafc;
  }

</style>
