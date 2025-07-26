import './App.css'
import { HomePage } from './pages/HomePage/Home.tsx'
import { useTaskPolling } from '@/hooks/useTaskPolling.ts'
import SettingPage from './pages/SettingPage/index.tsx'
import { BrowserRouter, Navigate, Routes } from 'react-router-dom'
import { Route } from 'react-router-dom'
import Index from '@/pages/Index.tsx'
import NotFoundPage from '@/pages/NotFoundPage'
import Model from '@/pages/SettingPage/Model.tsx'
import Transcriber from '@/pages/SettingPage/transcriber.tsx'
import ProviderForm from '@/components/Form/modelForm/Form.tsx'
import StepBar from '@/pages/HomePage/components/StepBar.tsx'
import Downloading from '@/components/Lottie/download.tsx'
import Prompt from '@/pages/SettingPage/Prompt.tsx'
import AboutPage from '@/pages/SettingPage/about.tsx'
import Downloader from '@/pages/SettingPage/Downloader.tsx'
import DownloaderForm from '@/components/Form/DownloaderForm/Form.tsx'
import { useEffect, useState } from 'react'
import { systemCheck } from '@/services/system.ts'
import { useCheckBackend } from '@/hooks/useCheckBackend.ts'
import BackendInitDialog from '@/components/BackendInitDialog'
import { MigrationModal } from '@/components/MigrationModal'
import { historyService } from '@/services/history'
import { useTaskStore } from '@/store/taskStore'

function App() {
  useTaskPolling(3000) // 每 3 秒轮询一次
  const { loading, initialized } = useCheckBackend()
  const [showMigrationModal, setShowMigrationModal] = useState(false)
  const [localStorageCount, setLocalStorageCount] = useState(0)
  const isTaskStoreInitialized = useTaskStore(state => state.isInitialized)

  // 在后端初始化完成后执行系统检查
  useEffect(() => {
    if (initialized) {
      systemCheck()
    }
  }, [initialized])

  // 检查是否需要显示迁移模态框
  useEffect(() => {
    if (initialized && isTaskStoreInitialized) {
      const { hasData, count } = historyService.checkLocalStorageData()
      const hasSkipped = historyService.hasSkippedMigration()
      
      if (hasData && !hasSkipped) {
        setLocalStorageCount(count)
        setShowMigrationModal(true)
      }
    }
  }, [initialized, isTaskStoreInitialized])

  // 如果后端还未初始化，显示初始化对话框
  if (!initialized) {
    return (
      <>
        <BackendInitDialog open={loading} />
      </>
    )
  }

  // 后端已初始化，渲染主应用
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />}>
            <Route index element={<HomePage />} />
            <Route path="settings" element={<SettingPage />}>
              <Route index element={<Navigate to="model" replace />} />
              <Route path="model" element={<Model />}>
                <Route path="new" element={<ProviderForm isCreate />} />
                <Route path=":id" element={<ProviderForm />} />
              </Route>
              <Route path="download" element={<Downloader />}>
                <Route path=":id" element={<DownloaderForm />} />
              </Route>
              <Route path="about" element={<AboutPage />}></Route>
              <Route path="*" element={<NotFoundPage />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
      
      {/* 迁移模态框 */}
      <MigrationModal
        isOpen={showMigrationModal}
        onClose={() => setShowMigrationModal(false)}
        localStorageCount={localStorageCount}
      />
    </>
  )
}

export default App