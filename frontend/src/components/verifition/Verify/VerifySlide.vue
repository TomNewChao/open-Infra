<template>
  <div style="position: relative">
    <div
      v-if="type === '2'"
      class="verify-img-out"
      :style="{ height: parseInt(setSize.imgHeight) + vSpace + 'px' }"
    >
      <div
        class="verify-img-panel"
        :style="{ width: setSize.imgWidth, height: setSize.imgHeight }"
      >
        <img
          :src="'data:image/png;base64,' + backImgBase"
          alt=""
          style="width: 100%; height: 100%; display: block"
        />
        <div v-show="showRefresh" class="verify-refresh" @click="refresh">
          <i class="iconfont icon-refresh"></i>
        </div>
        <transition name="tips">
          <span
            v-if="tipWords"
            class="verify-tips"
            :class="passFlag ? 'suc-bg' : 'err-bg'"
          >{{ tipWords }}</span
          >
        </transition>
      </div>
    </div>
    <!-- 公共部分 -->
    <div
      class="verify-bar-area"
      :style="{
        width: setSize.imgWidth,
        height: barSize.height,
        'line-height': barSize.height,
      }"
    >
      <span class="verify-msg" v-text="text"></span>
      <div
        class="verify-left-bar"
        :style="{
          width: leftBarWidth !== undefined ? leftBarWidth : barSize.height,
          height: barSize.height,
          'border-color': leftBarBorderColor,
          transaction: transitionWidth,
        }"
      >
        <span class="verify-msg" v-text="finishText"></span>
        <div
          class="verify-move-block"
          :style="{
            width: barSize.height,
            height: barSize.height,
            'background-color': moveBlockBackgroundColor,
            left: moveBlockLeft,
            transition: transitionLeft,
          }"
          @touchstart="start"
          @mousedown="start"
        >
          <i
            :class="['verify-icon iconfont', iconClass]"
            :style="{ color: iconColor }"
          ></i>
          <div
            v-if="type === '2'"
            class="verify-sub-block"
            :style="{
              width: Math.floor((parseInt(setSize.imgWidth) * 47) / 310) + 'px',
              height: setSize.imgHeight,
              top: '-' + (parseInt(setSize.imgHeight) + vSpace) + 'px',
              'background-size': setSize.imgWidth + ' ' + setSize.imgHeight,
            }"
          >
            <img
              :src="'data:image/png;base64,' + blockBackImgBase"
              alt=""
              style="
                width: 100%;
                height: 100%;
                display: block;
                -webkit-user-drag: none;
              "
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script type="text/babel">
/**
 * VerifySlide
 * @description 滑块
 * */
import { aesEncrypt } from '../utils/ase.js'
import { resetSize } from '../utils/util.js'
import { reqCaptcha, reqCheckCaptcha } from '@/api/user'
import { useI18n, useI18nStr } from '@/config'
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
  nextTick,
  toRefs,
  getCurrentInstance
} from 'vue'
//  "captchaType":"blockPuzzle",
export default {
  name: 'VerifySlide',
  props: {
    captchaType: {
      type: String
    },
    type: {
      type: String,
      default: '1'
    },
    // 弹出式pop，固定fixed
    mode: {
      type: String,
      default: 'fixed'
    },
    vSpace: {
      type: Number,
      default: 5
    },
    explain: {
      type: String,
      default: '向右滑动完成验证'
    },
    imgSize: {
      type: Object,
      default () {
        return {
          width: '310px',
          height: '155px'
        }
      }
    },
    blockSize: {
      type: Object,
      default () {
        return {
          width: '50px',
          height: '50px'
        }
      }
    },
    barSize: {
      type: Object,
      default () {
        return {
          width: '310px',
          height: '40px'
        }
      }
    }
  },
  setup (props, context) {
    const { mode, captchaType, vSpace, imgSize, barSize, type, blockSize } =
      toRefs(props)
    const i18n = useI18n()
    const explain = computed(() => i18n.value.SWIPE_RIGHT)
    const { proxy } = getCurrentInstance()
    const secretKey = ref(''), // 后端返回的ase加密秘钥
      passFlag = ref(''), // 是否通过的标识
      backImgBase = ref(''), // 验证码背景图片
      blockBackImgBase = ref(''), // 验证滑块的背景图片
      backToken = ref(''), // 后端返回的唯一token值
      startMoveTime = ref(''), // 移动开始的时间
      endMovetime = ref(''), // 移动结束的时间
      tipsBackColor = ref(''), // 提示词的背景颜色
      tipWords = ref(''),
      text = ref(''),
      finishText = ref(''),
      setSize = reactive({
        imgHeight: 0,
        imgWidth: 0,
        barHeight: 0,
        barWidth: 0
      }),
      top = ref(0),
      left = ref(0),
      moveBlockLeft = ref(undefined),
      leftBarWidth = ref(undefined),
      // 移动中样式
      moveBlockBackgroundColor = ref(undefined),
      leftBarBorderColor = ref('#ddd'),
      iconColor = ref(undefined),
      iconClass = ref('icon-right'),
      status = ref(false), // 鼠标状态
      isEnd = ref(false), // 是够验证完成
      showRefresh = ref(true),
      transitionLeft = ref(''),
      transitionWidth = ref(''),
      startLeft = ref(0)

    const barArea = computed(() => {
      return proxy.$el.querySelector('.verify-bar-area')
    })

    // 请求背景图片和验证图片
    function getPictrue () {
      const data = {
        captchaType: captchaType.value
      }
      reqCaptcha(data).then((res) => {
        if (res.code === '0') {
          backImgBase.value = res.repData.originalImageBase64
          blockBackImgBase.value = res.repData.jigsawImageBase64
          backToken.value = res.repData.token
          secretKey.value = res.repData.secretKey
        } else {
          tipWords.value = res.repMsg
        }
      })
    }

    const refresh = () => {
      showRefresh.value = true
      finishText.value = ''

      transitionLeft.value = 'left .3s'
      moveBlockLeft.value = 0

      leftBarWidth.value = undefined
      transitionWidth.value = 'width .3s'

      leftBarBorderColor.value = '#ddd'
      moveBlockBackgroundColor.value = '#fff'
      iconColor.value = '#000'
      iconClass.value = 'icon-right'
      isEnd.value = false

      getPictrue()
      setTimeout(() => {
        transitionWidth.value = ''
        transitionLeft.value = ''
        text.value = explain.value
      }, 300)
    }

    // 鼠标按下
    function start (e) {
      e = e || window.event
      let x
      if (!e.touches) {
        // 兼容PC端
        x = e.clientX
      } else {
        // 兼容移动端
        x = e.touches[0].pageX
      }
      startLeft.value = Math.floor(
        x - barArea.value.getBoundingClientRect().left
      )
      startMoveTime.value = +new Date() //  开始滑动的时间
      if (isEnd.value === false) {
        const colors = {
          openeuler: '#002fa7',
          opengauss: '#7d32ea',
          mindspore: '#0d8dff'
        }
        // const color = colors[import.meta.env?.VITE_COMMUNITY || 'openeuler']
        const color = colors['openeuler']
        text.value = ''
        moveBlockBackgroundColor.value = color
        leftBarBorderColor.value = color
        iconColor.value = '#fff'
        e.stopPropagation()
        status.value = true
      }
    }

    // 鼠标移动
    function move (e) {
      e = e || window.event
      if (status.value && isEnd.value === false) {
        let x
        if (!e.touches) {
          // 兼容PC端
          x = e.clientX
        } else {
          // 兼容移动端
          x = e.touches[0].pageX
        }
        const barAreaLeft = barArea.value.getBoundingClientRect().left
        let blockLeft = x - barAreaLeft // 小方块相对于父元素的left值
        if (
          blockLeft >=
          barArea.value.offsetWidth -
          parseInt(parseInt(blockSize.value.width) / 2) -
          2
        ) {
          blockLeft =
            barArea.value.offsetWidth -
            parseInt(parseInt(blockSize.value.width) / 2) -
            2
        }
        if (blockLeft <= 0) {
          blockLeft = parseInt(parseInt(blockSize.value.width) / 2)
        }
        // 拖动后小方块的left值
        moveBlockLeft.value = blockLeft - startLeft.value + 'px'
        leftBarWidth.value = blockLeft - startLeft.value + 'px'
      }
    }

    // 鼠标松开
    function end () {
      endMovetime.value = +new Date()
      // 判断是否重合
      if (status.value && isEnd.value === false) {
        let moveLeftDistance = parseInt(
          (moveBlockLeft.value || '').replace('px', '')
        )
        moveLeftDistance =
          (moveLeftDistance * 310) / parseInt(setSize.imgWidth)
        const data = {
          captchaType: captchaType.value,
          pointJson: secretKey.value
            ? aesEncrypt(
              JSON.stringify({ x: moveLeftDistance, y: 5.0 }),
              secretKey.value
            )
            : JSON.stringify({ x: moveLeftDistance, y: 5.0 }),
          token: backToken.value
        }
        reqCheckCaptcha(data)
          .then((res) => {
            if (res.code === '0') {
              moveBlockBackgroundColor.value = '#6dc335'
              leftBarBorderColor.value = '#6dc335'
              iconColor.value = '#fff'
              iconClass.value = 'icon-check'
              showRefresh.value = false
              isEnd.value = true
              if (mode.value === 'pop') {
                setTimeout(() => {
                  proxy.$parent.clickShow = false
                  refresh()
                }, 1500)
              }
              passFlag.value = true
              tipWords.value = useI18nStr('VERIFY_SUCCESS', [
                `${((endMovetime.value - startMoveTime.value) / 1000).toFixed(
                  2
                )}`
              ]).value
              const captchaVerification = secretKey.value
                ? aesEncrypt(
                  backToken.value +
                  '---' +
                  JSON.stringify({ x: moveLeftDistance, y: 5.0 }),
                  secretKey.value
                )
                : backToken.value +
                '---' +
                JSON.stringify({ x: moveLeftDistance, y: 5.0 })
              setTimeout(() => {
                tipWords.value = ''
                proxy.$parent.closeBox()
                proxy.$parent.$emit('success', { captchaVerification })
              }, 1000)
            } else {
              moveBlockBackgroundColor.value = '#f3524d'
              leftBarBorderColor.value = '#f3524d'
              iconColor.value = '#fff'
              iconClass.value = 'icon-close'
              passFlag.value = false
              setTimeout(function () {
                refresh()
              }, 1000)
              proxy.$parent.$emit('error', proxy)
              tipWords.value = i18n.value.VERIFY_FAILED
              setTimeout(() => {
                tipWords.value = ''
              }, 1000)
            }
          })
          .catch(() => {
            moveBlockBackgroundColor.value = '#f3524d'
            leftBarBorderColor.value = '#f3524d'
            iconColor.value = '#fff'
            iconClass.value = 'icon-close'
            passFlag.value = false
            setTimeout(function () {
              refresh()
            }, 1000)
            proxy.$parent.$emit('error', proxy)
            tipWords.value = i18n.value.VERIFY_FAILED
            setTimeout(() => {
              tipWords.value = ''
            }, 1000)
          })
        status.value = false
      }
    }

    function init () {
      text.value = explain.value
      getPictrue()
      nextTick(() => {
        const { imgHeight, imgWidth, barHeight, barWidth } = resetSize(proxy)
        setSize.imgHeight = imgHeight
        setSize.imgWidth = imgWidth
        setSize.barHeight = barHeight
        setSize.barWidth = barWidth
        proxy.$parent.$emit('ready', proxy)
      })

      window.removeEventListener('touchmove', function (e) {
        move(e)
      })
      window.removeEventListener('mousemove', function (e) {
        move(e)
      })

      // 鼠标松开
      window.removeEventListener('touchend', function () {
        end()
      })
      window.removeEventListener('mouseup', function () {
        end()
      })

      window.addEventListener('touchmove', function (e) {
        move(e)
      })
      window.addEventListener('mousemove', function (e) {
        move(e)
      })

      // 鼠标松开
      window.addEventListener('touchend', function () {
        end()
      })
      window.addEventListener('mouseup', function () {
        end()
      })
    }

    watch(type, () => {
      init()
    })
    onMounted(() => {
      // 禁止拖拽
      init()
      proxy.$el.onselectstart = function () {
        return false
      }
    })
    return {
      secretKey, // 后端返回的ase加密秘钥
      passFlag, // 是否通过的标识
      backImgBase, // 验证码背景图片
      blockBackImgBase, // 验证滑块的背景图片
      backToken, // 后端返回的唯一token值
      startMoveTime, // 移动开始的时间
      endMovetime, // 移动结束的时间
      tipsBackColor, // 提示词的背景颜色
      tipWords,
      text,
      finishText,
      setSize,
      top,
      left,
      moveBlockLeft,
      leftBarWidth,
      // 移动中样式
      moveBlockBackgroundColor,
      leftBarBorderColor,
      iconColor,
      iconClass,
      status, // 鼠标状态
      isEnd, // 是够验证完成
      showRefresh,
      transitionLeft,
      transitionWidth,
      barArea,
      refresh,
      start
    }
  }
}
</script>
