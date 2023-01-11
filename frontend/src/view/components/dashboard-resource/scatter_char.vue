<template>
  <div ref="dom" :class="className" :style="{height:height,width:width}"/>
</template>

<script>
import echarts from 'echarts'
import { on, off } from '@/libs/tools'

export default {
  name: 'ScatterChar',
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    title: {
      type: String,
      required: true
    },
    width: {
      type: String
      // default: '100%'
    },
    height: {
      type: String
      // default: '100%'
    },
    autoResize: {
      type: Boolean,
      default: true
    },
    chartData: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      chart: null
    }
  },
  watch: {
    chartData: {
      deep: true,
      handler (val) {
        this.setOptions(val)
      }
    }
  },
  methods: {
    resize () {
      this.chart.resize()
    },
    initChart () {
      this.chart = echarts.init(this.$refs.dom)
      this.setOptions(this.chartData)
    },
    setOptions (data) {
      let option = {
        title: {
          'text': '统计服务器一周的' + this.title + '资源分布图',
          'x': 'center'
        },
        xAxis: {
          'name': '一周的周期占比:%'
        },
        yAxis: {
          'name': this.title + '资源利用率:%'
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            return `${params.data[2]}</br>${params.marker}周期占比:${params.data[0]},使用率大于:${params.data[1]}`
          }
        },
        series: [
          {
            symbolSize: 5,
            data: data,
            type: 'scatter'
          }
        ]
      }
      this.chart.setOption(option)
    }
  },
  mounted () {
    this.$nextTick(() => {
      this.initChart()
      on(window, 'resize', this.resize)
    })
  },
  beforeDestroy () {
    off(window, 'resize', this.resize)
  }
}
</script>
