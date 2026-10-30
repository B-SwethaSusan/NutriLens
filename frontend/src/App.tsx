import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { DietPlanPage } from './pages/DietPlanPage'
import { FoodPhotoPage } from './pages/FoodPhotoPage'
import { ProgressPage } from './pages/ProgressPage'
import { RemediesPage } from './pages/RemediesPage'
import { SettingsPage } from './pages/SettingsPage'
import { WorkspacePage } from './pages/WorkspacePage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="diet-plan" element={<DietPlanPage />} />
        <Route path="progress" element={<ProgressPage />} />
        <Route path="food-photo" element={<FoodPhotoPage />} />
        <Route path="remedies" element={<RemediesPage />} />
        {/* Documents and Chat used to be separate pages; merged into one
            workspace since Chat only ever answers from your Documents —
            keeping /documents and /chat as aliases so old links/bookmarks
            still work. */}
        <Route path="workspace" element={<WorkspacePage />} />
        <Route path="documents" element={<WorkspacePage />} />
        <Route path="chat" element={<WorkspacePage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
