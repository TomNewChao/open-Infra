<template>
  <div>
    <Button type="primary" icon="logo-facebook" @click="openUpTimeStatus">切换至Uptime-Status管理中心</Button>
  </div>
</template>
<script>
export default {
  methods: {
    openUpTimeStatus() {
      window.open("https://uptime-status.osinfra.cn/");
    }
  }
}
</script>

