import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { getAuthData } from '../AuthUtils';

interface Props {
    allowedRoles: string[];
}

const ProtectedRoute = ({ allowedRoles }: Props) => {
    const auth = getAuthData();
    const location = useLocation();

    if (!auth) {
        return <Navigate to="/login" replace />;
    }

    if (!allowedRoles.includes(auth.role)) {
        return <Navigate to="/" replace />;
    }

    if (auth.role !== 'ADMIN' && auth.isNewUser && location.pathname !== '/onboarding') {
        return <Navigate to="/onboarding" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;