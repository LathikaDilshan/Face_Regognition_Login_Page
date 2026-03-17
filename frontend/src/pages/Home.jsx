import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

function Home() {
    const navigate = useNavigate();
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    useEffect(() => {
        // Simple client-side auth check
        const token = api.getToken();
        if (!token) {
            navigate('/login');
        }
    }, [navigate]);

    const handleLogout = async () => {
        setIsLoggingOut(true);
        try {
            // Call the `/api/logout/` endpoint to invalidate the token on the server
            await api.logout();
        } catch (error) {
            console.error("Logout failed on server:", error);
            // Even if server fails (e.g., token already invalid), we should clear it locally
        } finally {
            // Always remove token from local storage and redirect to login
            api.removeToken();
            navigate('/login');
        }
    };

    return (
        <div className="home-container">
            <header className="home-header">
                <div className="header-logo">
                    <h1>FaceRec Auth</h1>
                </div>
                <div className="header-actions">
                    <button 
                        onClick={handleLogout} 
                        disabled={isLoggingOut} 
                        className="logout-btn content-button"
                    >
                        {isLoggingOut ? 'Logging out...' : 'Logout'}
                    </button>
                </div>
            </header>
            
            <main className="home-content">
                {/* Space reserved for future content */}
            </main>
        </div>
    );
}

export default Home;
