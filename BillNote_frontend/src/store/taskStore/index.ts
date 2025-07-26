import { create } from 'zustand'
import { delete_task, generateNote } from '@/services/note.ts'
import { historyService } from '@/services/history.ts'
import { v4 as uuidv4 } from 'uuid'
import toast from 'react-hot-toast'


export type TaskStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILD'

export interface AudioMeta {
  cover_url: string
  duration: number
  file_path: string
  platform: string
  raw_info: any
  title: string
  video_id: string
}

export interface Segment {
  start: number
  end: number
  text: string
}

export interface Transcript {
  full_text: string
  language: string
  raw: any
  segments: Segment[]
}
export interface Markdown {
  ver_id: string
  content: string
  style: string
  model_name: string
  created_at: string
}

export interface Task {
  id: string
  markdown: string|Markdown [] //为了兼容之前的笔记
  transcript: Transcript
  status: TaskStatus
  audioMeta: AudioMeta
  platform: string
  createdAt: string
  formData: {
    video_url: string
    link: undefined | boolean
    screenshot: undefined | boolean
    platform: string
    quality: string
    model_name: string
    provider_id: string
    style?: string
  }
}

interface TaskStore {
  tasks: Task[]
  currentTaskId: string | null
  isLoading: boolean
  isInitialized: boolean
  
  // 初始化方法
  initialize: () => Promise<void>
  
  // 任务管理方法
  addPendingTask: (taskId: string, platform: string, formData: any) => void
  updateTaskContent: (id: string, data: Partial<Omit<Task, 'id' | 'createdAt'>>) => void
  removeTask: (id: string) => Promise<void>
  clearTasks: () => void
  setCurrentTask: (taskId: string | null) => void
  getCurrentTask: () => Task | null
  retryTask: (id: string, payload?: any) => Promise<void>
  
  // 数据库操作方法
  loadHistoryFromDatabase: () => Promise<void>
  refreshHistory: () => Promise<void>
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  currentTaskId: null,
  isLoading: false,
  isInitialized: false,

  // 初始化：加载数据库历史记录
  initialize: async () => {
    const state = get()
    if (state.isInitialized) return

    set({ isLoading: true })
    
    try {
      // 从数据库加载历史记录
      await state.loadHistoryFromDatabase()
      
      set({ isInitialized: true })
    } catch (error) {
      console.error('初始化taskStore失败:', error)
      toast.error('加载历史记录失败')
    } finally {
      set({ isLoading: false })
    }
  },

  // 从数据库加载历史记录
  loadHistoryFromDatabase: async () => {
    try {
      const history = await historyService.getAllHistory()
      set({ tasks: history })
    } catch (error) {
      console.error('从数据库加载历史记录失败:', error)
      toast.error('加载历史记录失败')
    }
  },

  // 刷新历史记录
  refreshHistory: async () => {
    const state = get()
    await state.loadHistoryFromDatabase()
  },

  addPendingTask: (taskId: string, platform: string, formData: any) => {
    const newTask: Task = {
      formData: formData,
      id: taskId,
      status: 'PENDING',
      markdown: '',
      platform: platform,
      transcript: {
        full_text: '',
        language: '',
        raw: null,
        segments: [],
      },
      createdAt: new Date().toISOString(),
      audioMeta: {
        cover_url: '',
        duration: 0,
        file_path: '',
        platform: '',
        raw_info: null,
        title: '',
        video_id: '',
      },
    }

    set(state => ({
      tasks: [newTask, ...state.tasks],
      currentTaskId: taskId, // 默认设置为当前任务
    }))
  },

  updateTaskContent: (id, data) => {
    set(state => ({
      tasks: state.tasks.map(task => {
        if (task.id !== id) return task

        if (task.status === 'SUCCESS' && data.status === 'SUCCESS') return task

        // 如果是 markdown 字符串，封装为版本
        if (typeof data.markdown === 'string') {
          const prev = task.markdown
          const newVersion: Markdown = {
            ver_id: `${task.id}-${uuidv4()}`,
            content: data.markdown,
            style: task.formData.style || '',
            model_name: task.formData.model_name || '',
            created_at: new Date().toISOString(),
          }

          let updatedMarkdown: Markdown[]
          if (Array.isArray(prev)) {
            updatedMarkdown = [newVersion, ...prev]
          } else {
            updatedMarkdown = [
              newVersion,
              ...(typeof prev === 'string' && prev
                  ? [{
                    ver_id: `${task.id}-${uuidv4()}`,
                    content: prev,
                    style: task.formData.style || '',
                    model_name: task.formData.model_name || '',
                    created_at: new Date().toISOString(),
                  }]
                  : []),
            ]
          }

          return {
            ...task,
            ...data,
            markdown: updatedMarkdown,
          }
        }

        return { ...task, ...data }
      }),
    }))
  },

  getCurrentTask: () => {
    const currentTaskId = get().currentTaskId
    return get().tasks.find(task => task.id === currentTaskId) || null
  },

  retryTask: async (id: string, payload?: any) => {
    if (!id){
      toast.error('任务不存在')
      return
    }
    const task = get().tasks.find(task => task.id === id)
    console.log('retry',task)
    if (!task) return

    const newFormData = payload || task.formData
    await generateNote({
      ...newFormData,
      task_id: id,
    })

    set(state => ({
      tasks: state.tasks.map(t =>
          t.id === id
              ? {
                ...t,
                formData: newFormData, // ✅ 显式更新 formData
                status: 'PENDING',
              }
              : t
      ),
    }))
  },

  removeTask: async (id: string) => {
    const task = get().tasks.find(t => t.id === id)

    // 先从本地状态中移除
    set(state => ({
      tasks: state.tasks.filter(task => task.id !== id),
      currentTaskId: state.currentTaskId === id ? null : state.currentTaskId,
    }))

    // 从数据库删除历史记录
    try {
      await historyService.deleteHistory(id)
    } catch (error) {
      console.error('删除数据库历史记录失败:', error)
      toast.error('删除历史记录失败')
    }

    // 调用后端删除接口（如果找到了任务）
    if (task) {
      try {
        await delete_task({
          video_id: task.audioMeta.video_id,
          platform: task.platform,
        })
      } catch (error) {
        console.error('删除后端任务记录失败:', error)
      }
    }
  },

  clearTasks: () => set({ tasks: [], currentTaskId: null }),

  setCurrentTask: (taskId: string | null) => set({ currentTaskId: taskId }),
}))

// 在应用启动时自动初始化
if (typeof window !== 'undefined') {
  // 延迟初始化，确保应用完全加载
  setTimeout(() => {
    useTaskStore.getState().initialize()
  }, 100)
}
