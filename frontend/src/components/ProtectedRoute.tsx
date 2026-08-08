import { Navigate, Outlet, useLocation } from 'react-router-dom'
export function ProtectedRoute() { const location = useLocation(); return localStorage.getItem('nutrilens_token') ? <Outlet /> : <Navigate to="/login" replace state={{ from: location }} /> }
