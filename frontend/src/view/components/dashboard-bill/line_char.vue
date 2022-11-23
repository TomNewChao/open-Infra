<template>
  <div ref="dom" :class="className" :style="{height:height,width:width}"/>
</template>

<script>
import echarts from 'echarts'
import { on, off } from '@/libs/tools'

export default {
  name: 'LineChar',
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '100%'
    },
    autoResize: {
      type: Boolean,
      default: true
    },
    chartData: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      chart: null,
      enumAccount: ['openeuler', 'hwstaff_h00223369', 'hwstaff_x00350071', 'hwstaff_zengchen1024', 'freesky-edward', 'hwstaff_intl_openEuler', 'hwstaff_z00223460', 'leon_wang']
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
      this.chart.setOption({
        title: {
          'text': '账单统计'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: this.enumAccount
        },
        grid: {
          top: '20%',
          left: '2%',
          right: '2%',
          bottom: '1%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            name: '月份',
            boundaryGap: false,
            data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '账单（单位：RMB）'
          }
        ],
        series: [
          {
            name: 'openeuler',
            type: 'line',
            label: {
              show: true,
              position: 'top'
            },
            areaStyle: {
              normal: {
                color: '#2d8cf0'
              }
            },
            data: data['openeuler']
          },
          {
            name: 'hwstaff_h00223369',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#c4ccd3'
              }
            },
            data: data['hwstaff_h00223369']
          },
          {
            name: 'hwstaff_x00350071',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#61a0a8'
              }
            },
            data: data['hwstaff_x00350071']
          },
          {
            name: 'hwstaff_zengchen1024',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#91c7ae'
              }
            },
            data: data['hwstaff_zengchen1024']
          },
          {
            name: 'freesky-edward',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#749f83'
              }
            },
            data: data['freesky-edward']
          },
          {
            name: 'hwstaff_intl_openEuler',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#649163'
              }
            },
            data: data['hwstaff_intl_openEuler']
          },
          {
            name: 'hwstaff_z00223460',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#ca8622'
              }
            },
            data: data['hwstaff_z00223460']
          },
          {
            name: 'leon_wang',
            type: 'line',
            areaStyle: {
              normal: {
                color: '#bda29a'
              }
            },
            data: data['leon_wang']
          }
        ]
      })
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
