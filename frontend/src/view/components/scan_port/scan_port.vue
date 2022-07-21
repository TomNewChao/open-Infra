<template>
  <div>
    <el-table ref="multipleTable" :data="tableData" tooltip-effect="dark" style="width: 100%"
              @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55">
      </el-table-column>
      <el-table-column prop="name" label="账户" width="120">
      </el-table-column>
      <el-table-column prop="date" label="更新时间" width="120">
      </el-table-column>
      <el-table-column prop="comment" label="备注" show-overflow-tooltip>
      </el-table-column>
    </el-table>
    <div class="button-download">
      <el-button type="primary" @click="submitForm">下载</el-button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [{
        date: '2016-05-03',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄dfdsjfaskjdlfkljsdjkalfjkolsdkjlkjl'
      }, {
        date: '2016-05-02',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-04',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-01',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-08',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-06',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-07',
        name: '王小虎',
        comment: '上海市普陀区金沙江路 1518 弄'
      }],
      multipleSelection: []
    }
  },

  mounted() {
    this.getAccount();
  },

  methods: {
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    submitForm() {
      for (let i = 0; i < this.multipleSelection.length; i++) {
        console.log(this.multipleSelection[i])
      }
    },
    getAccount() {

    },
  }
}
</script>


<style>
.button-download {
  padding: 10px
}
</style>
