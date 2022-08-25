<template>
  <div>
    <Row :gutter="20">
      <i-col :xs="12" :md="8" :lg="4" v-for="(infor, i) in inforCardData" :key="`infor-${i}`"
             style="height: 120px;padding-bottom: 10px;">
        <infor-card shadow :color="infor.color" :icon="infor.icon" :icon-size="36">
          <count-to :end="infor.count" count-class="count-style"/>
          <p>{{ infor.title }}</p>
        </infor-card>
      </i-col>
    </Row>
    <Row>
      <Carousel autoplay loop :autoplay-speed=5000>
        <CarouselItem>
          <div class="home-carousel">
            <img :src="teamWork" alt="devOps" class="img-style">
          </div>
        </CarouselItem>
        <CarouselItem>
          <div class="home-carousel">
            <img :src="teamResp" alt="DevOpsResp" class="img-style">
          </div>
        </CarouselItem>
      </Carousel>
    </Row>
    <!--    <Row :gutter="20" style="margin-top: 10px;">-->
    <!--      <i-col :md="24" :lg="8" style="margin-bottom: 20px;">-->
    <!--        <Card shadow>-->
    <!--          <chart-pie style="height: 300px;" :value="pieData" text="社区访问量"></chart-pie>-->
    <!--        </Card>-->
    <!--      </i-col>-->
    <!--      <i-col :md="24" :lg="16" style="margin-bottom: 20px;">-->
    <!--        <Card shadow>-->
    <!--          <chart-bar style="height: 300px;" :value="barData" text="每周社区活跃量"/>-->
    <!--        </Card>-->
    <!--      </i-col>-->
    <!--    </Row>-->
    <!--    <Row>-->
    <!--      <Card shadow>-->
    <!--        <example style="height: 310px;"/>-->
    <!--      </Card>-->
    <!--    </Row>-->
  </div>
</template>

<script>
import InforCard from '_c/info-card'
import CountTo from '_c/count-to'
import { ChartPie, ChartBar } from '_c/charts'
import Example from './example.vue'
import teamResp from '@/assets/images/team-resp.png'
import teamWork from '@/assets/images/team-work.png'

export default {
  name: 'home',
  components: {
    InforCard,
    CountTo,
    ChartPie,
    ChartBar,
    Example
  },
  data () {
    return {
      teamResp,
      teamWork,
      carouselValue: '',
      inforCardData: [
        { title: '运维账户', icon: 'md-person-add', count: 6, color: '#2d8cf0' },
        { title: 'CCE集群', icon: 'md-locate', count: 21, color: '#19be6b' },
        { title: 'CCE节点', icon: 'md-help-circle', count: 56, color: '#ff9900' },
        { title: 'ECS节点', icon: 'md-share', count: 398, color: '#ed3f14' },
        { title: '裸金属节点', icon: 'md-chatbubbles', count: 15, color: '#E46CBB' },
        { title: 'jenkins节点', icon: 'md-map', count: 112, color: '#9A66E4' }
      ],
      pieData: [
        { value: 33500, name: 'openEuler' },
        { value: 31000, name: 'openGauss' },
        { value: 23400, name: 'os-infra' },
        { value: 13500, name: 'openLooKeng' },
        { value: 15480, name: 'MindSpore' }
      ],
      barData: {
        Mon: 13253,
        Tue: 34235,
        Wed: 26321,
        Thu: 12340,
        Fri: 24643,
        Sat: 1322,
        Sun: 1324
      }
    }
  },
  mounted () {
    //
  }
}
</script>

<style lang="less">
.count-style {
  font-size: 50px;
}

.img-style {
  margin: 0 auto;
  margin-left: 380px;
  width: 50%;
  height: 50%;
}
</style>
