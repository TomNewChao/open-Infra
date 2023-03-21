<template>
  <div>
    <Button type="primary" icon="logo-facebook" @click="fortress">切换至堡垒机管理管理中心</Button>
  </div>

</template>
<script>
export default {
  methods: {
    fortress() {
      window.open("https://jumpserver.osinfra.cn");
    }
  }
}
</script>

