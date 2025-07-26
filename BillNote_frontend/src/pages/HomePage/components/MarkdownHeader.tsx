'use client'

import { useEffect, useState } from 'react'
import { Copy, Download, BrainCircuit, Database } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Badge } from '@/components/ui/badge'
import { toast } from 'react-hot-toast'
import type { Markdown, TaskStatus } from '@/store/taskStore'

interface NoteHeaderProps {
  currentTask?: {
    id: string
    markdown: Markdown[] | string
    audioMeta: {
      title: string
      cover_url: string
      duration: number
      file_path: string
      video_id: string
      platform: string
      raw_info: Record<string, unknown>
    }
    transcript: {
      full_text: string
      language: string
      raw: Record<string, unknown>
      segments: Array<{
        start: number
        end: number
        text: string
      }>
    }
    status: TaskStatus
    platform: string
    formData: {
      video_url: string
      link: boolean | undefined
      screenshot: boolean | undefined
      platform: string
      quality: string
      model_name: string
      provider_id: string
      style?: string | undefined
    }
    createdAt: string
  }
  isMultiVersion: boolean
  currentVerId: string
  setCurrentVerId: (id: string) => void
  modelName: string
  style: string
  noteStyles: { value: string; label: string }[]
  onCopy: () => void
  onDownload: () => void
  createAt?: string | Date
  showTranscribe: boolean
  setShowTranscribe: (show: boolean) => void
  viewMode: 'preview' | 'map'
  setViewMode: (mode: 'preview' | 'map') => void
}

export function MarkdownHeader({
  currentTask,
  isMultiVersion,
  currentVerId,
  setCurrentVerId,
  modelName,
  style,
  noteStyles,
  onCopy,
  onDownload,
  createAt,
  showTranscribe,
  setShowTranscribe,
  viewMode,
  setViewMode,
}: NoteHeaderProps) {
  const [copied, setCopied] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let timer: NodeJS.Timeout
    if (copied) {
      timer = setTimeout(() => setCopied(false), 2000)
    }
    return () => clearTimeout(timer)
  }, [copied])

  const handleCopy = () => {
    onCopy()
    setCopied(true)
  }

  const styleName = noteStyles.find(v => v.value === style)?.label || style

  // 确保markdown是数组类型
  const markdownVersions: Markdown[] = Array.isArray(currentTask?.markdown)
    ? currentTask.markdown
    : []

  const formatDate = (date: string | Date | undefined) => {
    if (!date) return ''
    const d = typeof date === 'string' ? new Date(date) : date
    if (isNaN(d.getTime())) return ''
    return d
      .toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
      .replace(/\//g, '-')
  }

  const handleSaveToDatabase = async () => {
    if (!currentTask) {
      toast.error('没有可保存的任务数据')
      return
    }

    setSaving(true)
    try {
      // 动态导入historyService，避免循环依赖
      const { historyService } = await import('@/services/history')
      
      // 检查记录是否已存在
      const existingRecord = await historyService.getHistoryByTaskId(currentTask.id)
      
      // 保存到数据库
      await historyService.saveTaskToDatabase(currentTask)
      
      if (existingRecord) {
        toast.success('记录已覆盖更新到数据库!')
      } else {
        toast.success('记录已保存到数据库!')
      }
    } catch (error: unknown) {
      console.error('保存到数据库失败:', error)
      const errorMessage = error instanceof Error ? error.message : '未知错误'
      toast.error(`保存失败: ${errorMessage}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b bg-white/95 px-4 py-2 backdrop-blur-sm">
      {/* 左侧区域：版本 + 标签 + 创建时间 */}
      <div className="flex flex-wrap items-center gap-3">
        {isMultiVersion && markdownVersions.length > 0 && (
          <Select value={currentVerId} onValueChange={setCurrentVerId}>
            <SelectTrigger className="h-8 w-[160px] text-sm">
              <div className="flex items-center">
                {(() => {
                  const idx = markdownVersions.findIndex(v => v.ver_id === currentVerId)
                  return idx !== -1 ? `版本（${currentVerId.slice(-6)}）` : ''
                })()}
              </div>
            </SelectTrigger>

            <SelectContent>
              {markdownVersions.map((v) => {
                const shortId = v.ver_id.slice(-6)
                return (
                  <SelectItem key={v.ver_id} value={v.ver_id}>
                    {`版本（${shortId}）`}
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        )}

        <Badge variant="secondary" className="bg-pink-100 text-pink-700 hover:bg-pink-200">
          {modelName}
        </Badge>
        <Badge variant="secondary" className="bg-cyan-100 text-cyan-700 hover:bg-cyan-200">
          {styleName}
        </Badge>

        {createAt && (
          <div className="text-muted-foreground text-sm">创建时间: {formatDate(createAt)}</div>
        )}
      </div>

      {/* 右侧操作按钮 */}
      <div className="flex items-center gap-1">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={() => {
                  setViewMode(viewMode === 'preview' ? 'map' : 'preview')
                }}
                variant="ghost"
                size="sm"
                className="h-8 px-2"
              >
                <BrainCircuit className="mr-1.5 h-4 w-4" />
                <span className="text-sm">{viewMode === 'preview' ? '思维导图' : 'markdown'}</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>思维导图</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button onClick={handleCopy} variant="ghost" size="sm" className="h-8 px-2">
                <Copy className="mr-1.5 h-4 w-4" />
                <span className="text-sm">{copied ? '已复制' : '复制'}</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>复制内容</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button onClick={onDownload} variant="ghost" size="sm" className="h-8 px-2">
                <Download className="mr-1.5 h-4 w-4" />
                <span className="text-sm">导出 Markdown</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>下载为 Markdown 文件</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={handleSaveToDatabase}
                variant="ghost"
                size="sm"
                className="h-8 px-2"
                disabled={saving || !currentTask}
              >
                <Database className="mr-1.5 h-4 w-4" />
                <span className="text-sm">{saving ? '保存中...' : '保存数据库'}</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>将当前笔记保存到数据库</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={() => {
                  setShowTranscribe(!showTranscribe)
                }}
                variant="ghost"
                size="sm"
                className="h-8 px-2"
              >
                <span className="text-sm">原文参照</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>原文参照</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  )
}
