<style lang="less">
@import './login.less';
</style>

<template>
  <div class="login">
    <div class="login-con">
      <Card icon="log-in" title="欢迎登录" :bordered="false">
        <div class="form-con">
          <login-form @on-success-valid="handleSubmit"></login-form>
        </div>
      </Card>
    </div>
    <Verify
      ref="verify"
      mode="pop"
      captcha-type="blockPuzzle"
      :img-size="GetVerifyImgSize()"
      @success="verifySuccess"
    ></Verify>
  </div>
</template>

<script>
import LoginForm from '_c/login-form'
import Verify from '_c/verifition/Verify'
import { mapActions } from 'vuex'

export default {
  components: {
    LoginForm,
    Verify
  },
  data () {
    return {
    }
  },
  methods: {
    ...mapActions([
      'handleLogin',
      'getUserInfo'
    ]),
    handleSubmit ({ username, password }) {
      this.$refs.verify.show()
    },

    verifySuccess ({ username, password }) {
      this.handleLogin({ username, password }).then(res => {
        this.getUserInfo().then(res => {
          this.$router.push({
            name: this.$config.homeName
          })
        })
      }).catch(res => {
        this.$Message.info(res)
      })
    },

    GetVerifyImgSize () {
      let width = 400
      const height = 200
      const innerWidth = window.innerWidth
      if (innerWidth - 28 < 400) {
        width = innerWidth - 30
      }
      return {
        width: width + 'px',
        height: height + 'px'
      }
    }

  }
}
</script>

<style>

</style>
