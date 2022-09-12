<template>
  <div>
    <Button type="primary" icon="logo-facebook" @click="openGrafana">切换至Grafana管理中心</Button>
  </div>

</template>
<script>
  export default {
    methods: {
      openGrafana() {
        window.open("https://grafana.osinfra.cn");
      }
    }
  }
</script>

