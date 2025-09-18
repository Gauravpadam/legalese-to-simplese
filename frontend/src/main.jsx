import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import Home from './pages/Home.jsx'
import Upload from './pages/Upload.jsx'
import Analysis from './pages/Analysis.jsx'
// import TestIntegration from './pages/TestIntegration.jsx'

const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/upload', element: <Upload /> },
  { path: '/analysis', element: <Analysis /> },
  
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
