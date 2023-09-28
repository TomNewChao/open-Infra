<template>
  <div>
    <Row :gutter="20">
      <i-col :xs="12" :md="8" :lg="4" v-for="(info, i) in infoCardData" :key="`info-${i}`"
             style="height: 120px;padding-bottom: 10px;">
        <info-card shadow :color="info.color" :icon="info.icon" :icon-size="36">
          <count-to :end="info.count" count-class="count-style"/>
          <p><a :href="info.url">{{ info.title }}</a></p>
        </info-card>
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
  </div>
</template>

<script>
import InfoCard from '_c/info-card'
import CountTo from '_c/count-to'
import teamResp from '@/assets/images/team-resp.png'
import teamWork from '@/assets/images/team-work.png'
import { indexApiList } from '@/api/indexmenu'

export default {
  name: 'home',
  components: {
    InfoCard,
    CountTo
  },
  data () {
    return {
      teamResp,
      teamWork,
      carouselValue: '',
      infoCardData: [
        { title: '运维账户', icon: 'md-person-add', count: 0, color: '#2d8cf0', url: '/#/resources/account' },
        { title: '在线服务统计', icon: 'md-locate', count: 0, color: '#19be6b', url: '/#/resources/rs_service_info' },
        { title: '弹性公网ip统计', icon: 'md-map', count: 0, color: '#9A66E4', url: '/#/resources/eip' },
        { title: 'CCE集群', icon: 'md-help-circle', count: 21, color: '#ff9900', url: '' },
        { title: 'ECS节点', icon: 'md-share', count: 398, color: '#ed3f14', url: '' },
        { title: '裸金属节点', icon: 'md-chatbubbles', count: 15, color: '#E46CBB', url: '' }
      ]
    }
  },
  mounted () {
    this.getIndexData()
  },
  methods: {
    getIndexData () {
      indexApiList().then(res => {
        if (res.data.code !== 0) {
          this.$Message.info(res.data.description)
        } else {
          let data = res.data.data
          this.infoCardData[0]['count'] = data['account']
          this.infoCardData[1]['count'] = data['service']
          this.infoCardData[2]['count'] = data['eip']
        }
      })
    }
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
