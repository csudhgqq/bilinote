import request from '@/utils/request'
import type { Task, TaskStatus, AudioMeta, Transcript, Markdown } from '@/store/taskStore'

// 历史记录API响应类型
export interface HistoryRecord {
  id: number
  task_id: string
  status: string
  platform: string
  title?: string
  cover_url?: string
  duration?: number
  file_path?: string
  video_id?: string
  raw_info?: any
  transcript_full_text?: string
  transcript_language?: string
  transcript_raw?: any
  transcript_segments?: Array<{
    start: number
    end: number
    text: string
  }>
  markdown_content?: string
  markdown_versions?: Markdown[]
  form_data?: any
  created_at: string
  updated_at: string
}

export interface HistoryResponse {
  code: number
  msg: string
  data: HistoryRecord[]
}

export interface HistoryDetailResponse {
  code: number
  msg: string
  data: HistoryRecord
}

export interface DeleteHistoryResponse {
  code: number
  msg: string
  data: null
}

// 将HistoryRecord转换为Task格式
export function convertHistoryToTask(history: HistoryRecord): Task {
  // 处理transcript segments
  const segments = history.transcript_segments?.map(seg => ({
    start: seg.start,
    end: seg.end,
    text: seg.text
  })) || []

  // 处理markdown内容
  let markdown: string | Markdown[]
  if (history.markdown_versions && history.markdown_versions.length > 0) {
    markdown = history.markdown_versions
  } else {
    markdown = history.markdown_content || ''
  }

  return {
    id: history.task_id,
    status: history.status as TaskStatus,
    platform: history.platform,
    markdown: markdown,
    transcript: {
      full_text: history.transcript_full_text || '',
      language: history.transcript_language || '',
      raw: history.transcript_raw,
      segments: segments,
    },
    audioMeta: {
      title: history.title || '',
      cover_url: history.cover_url || '',
      duration: history.duration || 0,
      file_path: history.file_path || '',
      video_id: history.video_id || '',
      platform: history.platform,
      raw_info: history.raw_info,
    },
    createdAt: history.created_at,
    formData: history.form_data || {
      video_url: '',
      link: false,
      screenshot: false,
      platform: history.platform,
      quality: 'medium',
      model_name: '',
      provider_id: '',
    },
  }
}

// 将Task转换为HistoryRecord格式用于保存
export function convertTaskToHistory(task: Task): Partial<HistoryRecord> {
  // 处理markdown版本
  let markdown_content = ''
  let markdown_versions: Markdown[] = []
  
  if (typeof task.markdown === 'string') {
    markdown_content = task.markdown
  } else if (Array.isArray(task.markdown)) {
    markdown_versions = task.markdown
    markdown_content = task.markdown.length > 0 ? task.markdown[0].content : ''
  }

  return {
    task_id: task.id,
    status: task.status,
    platform: task.platform,
    title: task.audioMeta.title,
    cover_url: task.audioMeta.cover_url,
    duration: task.audioMeta.duration,
    file_path: task.audioMeta.file_path,
    video_id: task.audioMeta.video_id,
    raw_info: task.audioMeta.raw_info,
    transcript_full_text: task.transcript.full_text,
    transcript_language: task.transcript.language,
    transcript_raw: task.transcript.raw,
    transcript_segments: task.transcript.segments?.map(seg => ({
      start: seg.start,
      end: seg.end,
      text: seg.text
    })),
    markdown_content: markdown_content,
    markdown_versions: markdown_versions.length > 0 ? markdown_versions : undefined,
    form_data: task.formData,
  }
}

export const historyService = {
  // 获取所有历史记录
  async getAllHistory(limit = 100, offset = 0): Promise<Task[]> {
    try {
      const response = await request.get('/get_all_history', {
        params: { limit, offset }
      })
      
      // response已经被拦截器处理，直接返回data
      if (Array.isArray(response)) {
        return response.map(convertHistoryToTask)
      } else {
        console.error('获取历史记录失败: 数据格式错误')
        return []
      }
    } catch (error) {
      console.error('获取历史记录出错:', error)
      return []
    }
  },

  // 获取特定任务的历史记录
  async getHistoryByTaskId(taskId: string): Promise<Task | null> {
    try {
      const response = await request.get(`/get_history/${taskId}`)
      
      if (response && typeof response === 'object') {
        return convertHistoryToTask(response as unknown as HistoryRecord)
      } else {
        console.error('获取历史记录详情失败: 数据格式错误')
        return null
      }
    } catch (error) {
      console.error('获取历史记录详情出错:', error)
      return null
    }
  },

  // 删除历史记录
  async deleteHistory(taskId: string): Promise<boolean> {
    try {
      await request.delete(`/delete_history/${taskId}`)
      return true
    } catch (error) {
      console.error('删除历史记录出错:', error)
      return false
    }
  },

  // 保存单条任务到数据库
  async saveTaskToDatabase(task: Task): Promise<boolean> {
    try {
      const historyData = convertTaskToHistory(task)
      
      // 使用upsert接口，存在则更新，不存在则创建
      await request.post('/upsert_history', historyData)
      console.log(`任务保存成功: ${task.id}`)
      return true
    } catch (error: any) {
      console.error(`保存任务失败 ${task.id}:`, error)
      throw error
    }
  },

  // 保存localStorage数据到数据库
  async migrateLocalStorageToDatabase(): Promise<boolean> {
    try {
      // 从localStorage获取数据
      const localData = localStorage.getItem('task-storage')
      if (!localData) {
        console.log('localStorage中没有找到历史数据')
        return true
      }

      const parsedData = JSON.parse(localData)
      const tasks = parsedData?.state?.tasks || []
      
      if (tasks.length === 0) {
        console.log('localStorage中没有历史记录')
        return true
      }

      console.log(`发现 ${tasks.length} 条localStorage历史记录，开始迁移...`)

      // 批量保存到数据库
      let successCount = 0
      let errorCount = 0
      let skippedCount = 0

      for (const task of tasks) {
        try {
          // 先检查记录是否已存在
          const existingRecord = await historyService.getHistoryByTaskId(task.id)
          if (existingRecord) {
            console.log(`跳过已存在的记录: ${task.id}`)
            skippedCount++
            continue
          }

          const historyData = convertTaskToHistory(task)
          
          // 调用后端的导入接口
          await request.post('/import_history', historyData)
          successCount++
          console.log(`导入成功: ${task.id}`)
        } catch (error) {
          errorCount++
          console.error(`保存任务出错 ${task.id}:`, error)
        }
      }

      console.log(`迁移完成: 成功 ${successCount} 条，跳过 ${skippedCount} 条，失败 ${errorCount} 条`)
      
      if (successCount > 0 || skippedCount > 0) {
        // 迁移成功后清空localStorage（可选）
        // localStorage.removeItem('task-storage')
        console.log('localStorage数据迁移处理完成')
        return true
      }
      
      return errorCount === 0
    } catch (error) {
      console.error('迁移localStorage数据失败:', error)
      return false
    }
  },

  // 检查是否需要迁移localStorage数据
  checkLocalStorageData(): { hasData: boolean; count: number } {
    try {
      // 检查localStorage中是否有数据
      const localData = localStorage.getItem('task-storage')
      if (!localData) return { hasData: false, count: 0 }

      const parsedData = JSON.parse(localData)
      const tasks = parsedData?.state?.tasks || []
      
      return { hasData: tasks.length > 0, count: tasks.length }
    } catch (error) {
      console.error('检查localStorage数据时出错:', error)
      return { hasData: false, count: 0 }
    }
  },

  // 检查用户是否已跳过迁移
  hasSkippedMigration(): boolean {
    return localStorage.getItem('migration-skipped') === 'true'
  }
} 