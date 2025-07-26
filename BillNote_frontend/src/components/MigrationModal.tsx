import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { historyService } from '@/services/history'
import { useTaskStore } from '@/store/taskStore'
import toast from 'react-hot-toast'

interface MigrationModalProps {
  isOpen: boolean
  onClose: () => void
  localStorageCount: number
}

export const MigrationModal: React.FC<MigrationModalProps> = ({
  isOpen,
  onClose,
  localStorageCount
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const refreshHistory = useTaskStore(state => state.refreshHistory)

  const handleMigrate = async () => {
    setIsLoading(true)
    try {
      const success = await historyService.migrateLocalStorageToDatabase()
      if (success) {
        toast.success('历史记录迁移成功！')
        // 刷新历史记录显示
        await refreshHistory()
        onClose()
      } else {
        toast.error('历史记录迁移失败，请稍后重试')
      }
    } catch (error) {
      console.error('迁移失败:', error)
      toast.error('历史记录迁移失败，请稍后重试')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSkip = () => {
    // 标记用户已拒绝迁移，避免重复询问
    localStorage.setItem('migration-skipped', 'true')
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>发现历史记录</DialogTitle>
          <DialogDescription>
            检测到浏览器中有 {localStorageCount} 条历史记录。
            <br />
            <br />
            迁移到数据库后，您的历史记录将：
            <ul className="mt-2 ml-4 list-disc text-sm">
              <li>永久保存，不会因清理浏览器数据而丢失</li>
              <li>支持跨设备同步</li>
              <li>提供更好的搜索和管理功能</li>
            </ul>
            <br />
            建议立即迁移以保护您的数据安全。
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleSkip}
            disabled={isLoading}
          >
            暂不迁移
          </Button>
          <Button
            onClick={handleMigrate}
            disabled={isLoading}
          >
            {isLoading ? '迁移中...' : '立即迁移'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 