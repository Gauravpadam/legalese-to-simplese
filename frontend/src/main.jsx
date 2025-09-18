import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import Home from './pages/Home'
import Upload from './pages/Upload'
import Analysis from './pages/Analysis'
// import TestIntegration from './pages/TestIntegration.jsx'
import AnalysisContextProvider from './contexts/AnalysisProvider';

const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/upload', element: <Upload /> },
  { path: '/analysis', element: <Analysis /> },
  
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AnalysisContextProvider>
    <RouterProvider router={router} />
    </AnalysisContextProvider>
  </StrictMode>,
)
