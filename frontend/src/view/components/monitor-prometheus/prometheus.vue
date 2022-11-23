<template>
  <div>
    <Button type="primary" icon="logo-facebook" @click="openPrometheus">切换至Prometheus管理中心</Button>
  </div>

</template>
<script>
  export default {
    methods: {
      openPrometheus() {
        window.open("https://monitor.osinfra.cn");
      }
    }
  }
</script>

