
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

export function exportToCSV(data, columns, filename = 'export.csv') {
  if (!data || !data.length) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  try {
    // 处理表头
    const headers = columns.map(col => col.label).join(',')
    
    // 处理数据
    const rows = data.map(row => {
      return columns.map(col => {
        let val = row[col.prop]
        
        // 处理日期格式
        if (col.format && typeof col.format === 'function') {
          val = col.format(val)
        } else if (col.type === 'date') {
          val = val ? dayjs(val).format('YYYY-MM-DD') : ''
        } else if (col.type === 'datetime') {
          val = val ? dayjs(val).format('YYYY-MM-DD HH:mm:ss') : ''
        }
        
        // 处理特殊字符
        if (val === null || val === undefined) val = ''
        val = String(val).replace(/"/g, '""')
        return `"${val}"`
      }).join(',')
    })

    const csvContent = '\uFEFF' + [headers, ...rows].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}
