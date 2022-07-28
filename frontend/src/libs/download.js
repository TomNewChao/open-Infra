/**
 * 传入二进制文件流，虚拟一个下载事件。
 * @value 二进制文件流
 * @name 该属性也可以设置一个值来规定下载文件的名称。所允许的值没有限制，浏览器将自动检测正确的文件扩展名并添加到文件 (.img, .pdf, .txt, .html, 等等)。
 */
export function blobDownload (value, name) {
  const elink = document.createElement('a') // 创建一个a标签
  elink.download = name
  elink.style.display = 'none' // 设置隐藏样式
  elink.href = URL.createObjectURL(new Blob([value])) // 用于创建 URL 的 File 对象、Blob 对象或者 MediaSource 对象。
  document.body.appendChild(elink) // 在页面中实例这个a标签
  elink.click() // 执行这个a标签的点击事件，下载。
  URL.revokeObjectURL(elink.href) // 释放URL 对象
  document.body.removeChild(elink) // 在页面中移除这个标签。
}
