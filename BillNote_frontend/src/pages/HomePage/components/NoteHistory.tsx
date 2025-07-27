import { useTaskStore } from '@/store/taskStore'
import { ScrollArea } from '@/components/ui/scroll-area.tsx'
import { Badge } from '@/components/ui/badge.tsx'
import { cn } from '@/lib/utils.ts'
import { Trash, FolderPlus, ChevronDown, ChevronRight, Folder, FolderOpen, MoreHorizontal, Edit, FolderX, GripVertical } from 'lucide-react'
import { Button } from '@/components/ui/button.tsx'
import PinyinMatch from 'pinyin-match'
import Fuse from 'fuse.js'
import { 
  DndContext, 
  DragEndEvent, 
  DragOverlay, 
  DragStartEvent,
  DropAnimation,
  defaultDropAnimationSideEffects,
  pointerWithin
} from '@dnd-kit/core'
import { useDraggable, useDroppable } from '@dnd-kit/core'

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip.tsx'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog.tsx'
import { Input } from '@/components/ui/input.tsx'
import LazyImage from "@/components/LazyImage.tsx";
import {FC, useState ,useEffect } from 'react'

interface NoteHistoryProps {
  onSelect: (taskId: string) => void
  selectedId: string | null
}

const NoteHistory: FC<NoteHistoryProps> = ({ onSelect, selectedId }) => {
  const tasks = useTaskStore(state => state.tasks)
  const folders = useTaskStore(state => state.folders)
  const removeTask = useTaskStore(state => state.removeTask)
  const addFolder = useTaskStore(state => state.addFolder)
  const removeFolder = useTaskStore(state => state.removeFolder)
  const renameFolder = useTaskStore(state => state.renameFolder)
  const toggleFolder = useTaskStore(state => state.toggleFolder)
  const moveTaskToFolder = useTaskStore(state => state.moveTaskToFolder)
  const isLoading = useTaskStore(state => state.isLoading)
  const isInitialized = useTaskStore(state => state.isInitialized)
  const refreshHistory = useTaskStore(state => state.refreshHistory)
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'api/'
  const [rawSearch, setRawSearch] = useState('')
  const [search, setSearch] = useState('')
  const [newFolderName, setNewFolderName] = useState('')
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null)
  const [editingFolderName, setEditingFolderName] = useState('')
  const [showNewFolderDialog, setShowNewFolderDialog] = useState(false)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [draggedTask, setDraggedTask] = useState<any>(null)
  const fuse = new Fuse(tasks, {
    keys: ['audioMeta.title'],
    threshold: 0.4 // 匹配精度（越低越严格）
  })
  
  useEffect(() => {
    const timer = setTimeout(() => {
      if (rawSearch === '') return
      setSearch(rawSearch)
    }, 300) // 300ms 防抖

    return () => clearTimeout(timer)
  }, [rawSearch])
  
  const filteredTasks = search.trim()
      ? fuse.search(search).map(result => result.item)
      : tasks

  // 辅助函数：构建树状结构
  const buildTreeStructure = () => {
    const rootFolders = folders.filter(f => !f.parentId)
    const rootTasks = filteredTasks.filter(t => !t.folderId)
    
    const buildFolderTree = (folderId?: string | null) => {
      return folders
        .filter(f => f.parentId === folderId)
        .map(folder => ({
          ...folder,
          children: buildFolderTree(folder.id),
          tasks: filteredTasks.filter(t => t.folderId === folder.id)
        }))
    }
    
    return {
      rootFolders: buildFolderTree(null),
      rootTasks
    }
  }

  const { rootFolders, rootTasks } = buildTreeStructure()

  // 新建文件夹
  const handleCreateFolder = () => {
    if (newFolderName.trim()) {
      addFolder(newFolderName.trim())
      setNewFolderName('')
      setShowNewFolderDialog(false)
    }
  }

  // 重命名文件夹
  const handleRenameFolder = (folderId: string) => {
    if (editingFolderName.trim()) {
      renameFolder(folderId, editingFolderName.trim())
      setEditingFolderId(null)
      setEditingFolderName('')
    }
  }

  // 拖拽处理函数
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event
    setActiveId(active.id as string)
    
    // 找到被拖拽的任务
    const task = tasks.find(t => t.id === active.id)
    setDraggedTask(task)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    
    setActiveId(null)
    setDraggedTask(null)
    
    if (!over) return
    
    const taskId = active.id as string
    const overId = over.id as string
    
    // 如果拖到文件夹上
    if (overId.startsWith('folder-')) {
      const folderId = overId.replace('folder-', '')
      moveTaskToFolder(taskId, folderId)
    }
    // 如果拖到根目录上
    else if (overId === 'root') {
      moveTaskToFolder(taskId, undefined)
    }
  }

  const dropAnimation: DropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: {
        active: {
          opacity: '0.5',
        },
      },
    }),
  }

  // 可拖拽的任务组件
  const DraggableTask = ({ task, depth = 0 }: { task: any; depth?: number }) => {
    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      isDragging,
    } = useDraggable({
      id: task.id,
    })

    const style = transform ? {
      transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      marginLeft: `${depth * 16}px`,
    } : {
      marginLeft: `${depth * 16}px`,
    }

    return (
      <div
        ref={setNodeRef}
        style={style}
        onClick={() => onSelect(task.id)}
        className={cn(
          'flex cursor-pointer flex-col rounded-md border border-neutral-200 p-3 ml-4 relative',
          selectedId === task.id && 'border-primary bg-primary-light',
          isDragging && 'opacity-50'
        )}
      >
        {/* 拖动手柄 */}
        <div 
          {...listeners}
          {...attributes}
          className="absolute left-1 top-1/2 transform -translate-y-1/2 cursor-grab hover:bg-neutral-100 rounded p-1"
          onClick={(e) => e.stopPropagation()}
        >
          <GripVertical className="h-4 w-4 text-neutral-400" />
        </div>
        <div className="ml-6">
          {renderTaskContent(task)}
        </div>
      </div>
    )
  }

  // 渲染任务内容
  const renderTaskContent = (task: any) => (
    <>
      <div className={cn('flex items-center gap-4')}>
        {/* 封面图 */}
        {task.platform === 'local' ? (
          <img
            src={
              task.audioMeta.cover_url ? `${task.audioMeta.cover_url}` : '/placeholder.png'
            }
            alt="封面"
            className="h-10 w-12 rounded-md object-cover"
          />
        ) : (
          <LazyImage
            src={
              task.audioMeta.cover_url
                ? baseURL+`/image_proxy?url=${encodeURIComponent(task.audioMeta.cover_url)}`
                : '/placeholder.png'
            }
            alt="封面"
          />
        )}

        {/* 标题 + 状态 */}
        <div className="flex w-full items-center justify-between gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="line-clamp-2 max-w-[180px] flex-1 overflow-hidden text-sm text-ellipsis">
                  {task.audioMeta.title || '未命名笔记'}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>{task.audioMeta.title || '未命名笔记'}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
      <div className={'mt-2 flex items-center justify-between text-[10px]'}>
        <div className="shrink-0">
          {task.status === 'SUCCESS' && (
            <div className={'bg-primary w-10 rounded p-0.5 text-center text-white'}>
              已完成
            </div>
          )}
          {task.status !== 'SUCCESS' && task.status !== 'FAILD' ? (
            <div className={'w-10 rounded bg-green-500 p-0.5 text-center text-white'}>
              等待中
            </div>
          ) : (
            <></>
          )}
          {task.status === 'FAILD' && (
            <div className={'w-10 rounded bg-red-500 p-0.5 text-center text-white'}>失败</div>
          )}
        </div>

        <div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  onClick={e => {
                    e.stopPropagation()
                    removeTask(task.id)
                  }}
                  className="shrink-0"
                >
                  <Trash className="text-muted-foreground h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>删除</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </>
  )

  // 可放置的文件夹组件
  const DroppableFolder = ({ folder, depth = 0 }: { folder: any; depth?: number }) => {
    const { isOver, setNodeRef } = useDroppable({
      id: `folder-${folder.id}`,
    })

    return (
      <div key={folder.id} style={{ marginLeft: `${depth * 16}px` }}>
        <div 
          ref={setNodeRef}
          className={cn(
            "flex items-center gap-2 p-2 hover:bg-neutral-50 rounded-md",
            isOver && "bg-blue-50 border-2 border-blue-200 border-dashed"
          )}
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleFolder(folder.id)}
            className="p-1 h-6 w-6"
          >
            {folder.isExpanded ? 
              <ChevronDown className="h-4 w-4" /> : 
              <ChevronRight className="h-4 w-4" />
            }
          </Button>
          
          {folder.isExpanded ? 
            <FolderOpen className="h-4 w-4 text-blue-500" /> : 
            <Folder className="h-4 w-4 text-blue-500" />
          }
          
          {editingFolderId === folder.id ? (
            <Input
              value={editingFolderName}
              onChange={(e) => setEditingFolderName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRenameFolder(folder.id)
                if (e.key === 'Escape') {
                  setEditingFolderId(null)
                  setEditingFolderName('')
                }
              }}
              onBlur={() => handleRenameFolder(folder.id)}
              className="h-6 px-2 text-sm"
              autoFocus
            />
          ) : (
            <span 
              className="flex-1 text-sm font-medium cursor-pointer"
              onClick={() => toggleFolder(folder.id)}
            >
              {folder.name} ({folder.tasks.length})
            </span>
          )}
          
          <div className="flex gap-1">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setEditingFolderId(folder.id)
                      setEditingFolderName(folder.name)
                    }}
                    className="p-1 h-6 w-6"
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>重命名</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFolder(folder.id)}
                    className="p-1 h-6 w-6"
                  >
                    <FolderX className="h-3 w-3 text-red-500" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>删除文件夹</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
        
        {folder.isExpanded && (
          <div className="ml-4">
            {folder.children.map((child: any) => (
              <DroppableFolder key={child.id} folder={child} depth={depth + 1} />
            ))}
            {folder.tasks.map((task: any) => (
              <DraggableTask key={task.id} task={task} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    )
  }

  // 显示加载状态
  if (!isInitialized || isLoading) {
    return (
      <div className="flex items-center justify-center py-6">
        <div className="text-sm text-neutral-500">正在加载历史记录...</div>
      </div>
    )
  }

  if (filteredTasks.length === 0 && folders.length === 0) {
    return (
      <DndContext
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        collisionDetection={pointerWithin}
      >
        <div className="mb-2 flex gap-2">
          <input
            type="text"
            placeholder="搜索笔记标题..."
            className="flex-1 rounded border border-neutral-300 px-3 py-1 text-sm outline-none focus:border-primary"
            value={rawSearch}
            onChange={e => setRawSearch(e.target.value)}
          />
          <Dialog open={showNewFolderDialog} onOpenChange={setShowNewFolderDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <FolderPlus className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>新建文件夹</DialogTitle>
              </DialogHeader>
              <div className="flex gap-2">
                <Input
                  placeholder="文件夹名称"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateFolder()}
                />
                <Button onClick={handleCreateFolder}>创建</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
        <div className="rounded-md border border-neutral-200 bg-neutral-50 py-6 text-center">
          <p className="text-sm text-neutral-500">暂无记录</p>
        </div>
      </DndContext>
    )
  }


  // 根目录放置区域
  const RootDropZone = ({ children }: { children: React.ReactNode }) => {
    const { isOver, setNodeRef } = useDroppable({
      id: 'root',
    })

    return (
      <div 
        ref={setNodeRef}
        className={cn(
          "flex flex-col gap-1",
          isOver && "bg-blue-50 border-2 border-blue-200 border-dashed rounded-md p-2"
        )}
      >
        {children}
      </div>
    )
  }

  return (
    <DndContext
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      collisionDetection={pointerWithin}
    >
      <div className="mb-2 flex gap-2">
        <input
          type="text"
          placeholder="搜索笔记标题..."
          className="flex-1 rounded border border-neutral-300 px-3 py-1 text-sm outline-none focus:border-primary"
          value={rawSearch}
          onChange={e => setRawSearch(e.target.value)}
        />
        <Dialog open={showNewFolderDialog} onOpenChange={setShowNewFolderDialog}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <FolderPlus className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>新建文件夹</DialogTitle>
            </DialogHeader>
            <div className="flex gap-2">
              <Input
                placeholder="文件夹名称"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreateFolder()}
              />
              <Button onClick={handleCreateFolder}>创建</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      
      <ScrollArea className="flex-1">
        <RootDropZone>
          {/* 渲染根目录下的文件夹 */}
          {rootFolders.map(folder => (
            <DroppableFolder key={folder.id} folder={folder} />
          ))}
          
          {/* 渲染根目录下的任务 */}
          {rootTasks.length > 0 && (
            <div className="mt-2">
              {rootTasks.map(task => (
                <DraggableTask key={task.id} task={task} />
              ))}
            </div>
          )}
        </RootDropZone>
      </ScrollArea>
      
      <DragOverlay dropAnimation={dropAnimation}>
        {activeId && draggedTask ? (
          <div className="flex cursor-pointer flex-col rounded-md border border-neutral-200 p-3 opacity-90 shadow-lg">
            {renderTaskContent(draggedTask)}
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

export default NoteHistory
