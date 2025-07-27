import request from '@/utils/request'
import type { Folder } from '@/store/taskStore'

// 文件夹API响应类型
export interface FolderRecord {
  id: string
  name: string
  parent_id?: string
  is_expanded: boolean
  created_at: string
  updated_at: string
}

// API请求类型
export interface CreateFolderRequest {
  id: string
  name: string
  parent_id?: string
  is_expanded?: boolean
}

export interface UpdateFolderRequest {
  name?: string
  parent_id?: string
  is_expanded?: boolean
}

export interface MoveHistoryRequest {
  task_id: string
  folder_id?: string
}

// 将API响应转换为前端Folder类型
export function convertFolderRecordToFolder(record: FolderRecord): Folder {
  return {
    id: record.id,
    name: record.name,
    parentId: record.parent_id,
    isExpanded: record.is_expanded,
    createdAt: record.created_at,
  }
}

// 将前端Folder类型转换为API请求
export function convertFolderToCreateRequest(folder: Folder): CreateFolderRequest {
  return {
    id: folder.id,
    name: folder.name,
    parent_id: folder.parentId,
    is_expanded: folder.isExpanded,
  }
}

export const folderService = {
  // 获取所有文件夹
  async getAllFolders(): Promise<Folder[]> {
    try {
      const response = await request.get('/folders')
      console.log('获取文件夹API响应:', response)
      
      // request.ts 的响应拦截器已经解包了数据，直接返回的是 data 部分
      if (Array.isArray(response)) {
        console.log('解析文件夹数据:', response)
        return response.map(convertFolderRecordToFolder)
      } else {
        console.error('获取文件夹列表失败: 数据格式错误', response)
        return []
      }
    } catch (error) {
      console.error('获取文件夹列表出错:', error)
      return []
    }
  },

  // 创建文件夹
  async createFolder(folder: Folder): Promise<boolean> {
    try {
      const request_data = convertFolderToCreateRequest(folder)
      await request.post('/folders', request_data)
      console.log(`文件夹创建成功: ${folder.name}`)
      return true
    } catch (error) {
      console.error(`创建文件夹失败 ${folder.name}:`, error)
      return false
    }
  },

  // 更新文件夹
  async updateFolder(folderId: string, updates: UpdateFolderRequest): Promise<boolean> {
    try {
      await request.put(`/folders/${folderId}`, updates)
      console.log(`文件夹更新成功: ${folderId}`)
      return true
    } catch (error) {
      console.error(`更新文件夹失败 ${folderId}:`, error)
      return false
    }
  },

  // 删除文件夹
  async deleteFolder(folderId: string): Promise<boolean> {
    try {
      await request.delete(`/folders/${folderId}`)
      console.log(`文件夹删除成功: ${folderId}`)
      return true
    } catch (error) {
      console.error(`删除文件夹失败 ${folderId}:`, error)
      return false
    }
  },

  // 移动历史记录到文件夹
  async moveHistoryToFolder(taskId: string, folderId?: string): Promise<boolean> {
    try {
      const request_data: MoveHistoryRequest = {
        task_id: taskId,
        folder_id: folderId,
      }
      await request.post('/folders/move-history', request_data)
      console.log(`历史记录移动成功: ${taskId} -> ${folderId || 'root'}`)
      return true
    } catch (error) {
      console.error(`移动历史记录失败 ${taskId}:`, error)
      return false
    }
  },

  // 重命名文件夹
  async renameFolder(folderId: string, newName: string): Promise<boolean> {
    return this.updateFolder(folderId, { name: newName })
  },

  // 切换文件夹展开状态
  async toggleFolder(folderId: string, isExpanded: boolean): Promise<boolean> {
    return this.updateFolder(folderId, { is_expanded: isExpanded })
  },

  // 移动文件夹到新的父文件夹
  async moveFolder(folderId: string, newParentId?: string): Promise<boolean> {
    return this.updateFolder(folderId, { parent_id: newParentId })
  },
}