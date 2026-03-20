import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { api } from '../utils/api';

function Login() {
    const [activeTab, setActiveTab] = useState('password'); // 'password' or 'face'
    const [formData, setFormData] = useState({
        username: '',
        position: '',
        password: ''
    });
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    
    // Webcam scanning states and refs
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isScanning, setIsScanning] = useState(false);
    const [scanProgress, setScanProgress] = useState(0);
    const [capturedImages, setCapturedImages] = useState([]);
    const [webcamActive, setWebcamActive] = useState(false);

    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Show success message if redirected from register
        if (location.state?.message) {
            setSuccessMsg(location.state.message);
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    useEffect(() => {
        if (activeTab === 'face') {
            startWebcam();
        } else {
            stopWebcam();
            setCapturedImages([]);
        }
        return () => stopWebcam();
    }, [activeTab]);

    const startWebcam = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setWebcamActive(true);
            }
        } catch (err) {
            console.error("Error accessing webcam:", err);
            setError("Could not access webcam. Please ensure permissions are granted.");
        }
    };

    const stopWebcam = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
            setWebcamActive(false);
        }
    };

    const captureImages = async () => {
        if (!videoRef.current || !canvasRef.current || isScanning) return;
        
        setIsScanning(true);
        setScanProgress(0);
        setCapturedImages([]);
        setError(null);

        const images = [];
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        const video = videoRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Capture 7 images
        for (let i = 0; i < 7; i++) {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
            images.push(blob);
            
            setScanProgress(i + 1);
            await new Promise(resolve => setTimeout(resolve, 300));
        }
        
        setCapturedImages(images);
        setIsScanning(false);
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (activeTab === 'face' && capturedImages.length !== 7) {
            setError("Please complete the face scan to log in.");
            return;
        }

        setIsLoading(true);
        setError(null);
        setSuccessMsg(null);

        try {
            const submitData = new FormData();
            submitData.append('username', formData.username);
            submitData.append('position', formData.position);
            
            if (activeTab === 'password') {
                submitData.append('password', formData.password);
            } else {
                capturedImages.forEach((blob, index) => {
                    submitData.append('images', blob, `login_face_${index}.jpg`);
                });
            }

            const response = await api.login(submitData);
            
            if (response && response.access_token) {
                api.setToken(response.access_token);
                stopWebcam();
                navigate('/');
            } else {
                 throw new Error("Invalid response format from server");
            }
        } catch (err) {
            setError(err.message || 'Login failed. Please check your credentials.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card" style={{ maxWidth: '600px' }}>
                <h2>Welcome Back</h2>
                <p>Log in to your account</p>
                
                {successMsg && <div className="success-message">{successMsg}</div>}
                {error && <div className="error-message">{error}</div>}
                
                <div style={{ display: 'flex', marginBottom: '1.5rem', borderBottom: '1px solid #ddd' }}>
                    <button 
                        type="button"
                        onClick={() => setActiveTab('password')}
                        style={{ flex: 1, padding: '10px', background: 'none', border: 'none', borderBottom: activeTab === 'password' ? '2px solid #007bff' : 'none', fontWeight: activeTab === 'password' ? 'bold' : 'normal', cursor: 'pointer' }}
                    >
                        Password
                    </button>
                    <button 
                        type="button"
                        onClick={() => setActiveTab('face')}
                        style={{ flex: 1, padding: '10px', background: 'none', border: 'none', borderBottom: activeTab === 'face' ? '2px solid #007bff' : 'none', fontWeight: activeTab === 'face' ? 'bold' : 'normal', cursor: 'pointer' }}
                    >
                        Face Scan
                    </button>
                </div>
                
                <form onSubmit={handleSubmit} className="auth-form" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="position">Position</label>
                        <input
                            type="text"
                            id="position"
                            name="position"
                            value={formData.position}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    
                    {activeTab === 'password' ? (
                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required={activeTab === 'password'}
                            />
                        </div>
                    ) : (
                        <div className="form-group" style={{ textAlign: 'center' }}>
                            <label>Face Authentication</label>
                            <div style={{ position: 'relative', width: '100%', maxWidth: '320px', margin: '0 auto', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#000' }}>
                                <video 
                                    ref={videoRef} 
                                    autoPlay 
                                    playsInline 
                                    muted 
                                    style={{ width: '100%', display: webcamActive ? 'block' : 'none' }}
                                />
                                {!webcamActive && (
                                    <div style={{ padding: '40px 0', color: '#fff' }}>Webcam initializing or blocked</div>
                                )}
                            </div>
                            <canvas ref={canvasRef} style={{ display: 'none' }} />
                            
                            <div style={{ marginTop: '10px' }}>
                                <button 
                                    type="button" 
                                    onClick={captureImages} 
                                    disabled={isScanning || !webcamActive}
                                    className="content-button"
                                    style={{ backgroundColor: capturedImages.length === 7 ? '#28a745' : '' }}
                                >
                                    {isScanning ? `Scanning (${scanProgress}/7)...` : capturedImages.length === 7 ? 'Face Scanned Successfully ✓' : 'Scan Face'}
                                </button>
                            </div>
                        </div>
                    )}

                    <button type="submit" disabled={isLoading || (activeTab === 'face' && capturedImages.length !== 7)} className="submit-btn content-button">
                        {isLoading ? 'Logging in...' : 'Log In'}
                    </button>
                </form>
                
                <div className="auth-footer">
                    Don't have an account? <Link to="/register">Sign up</Link>
                </div>
            </div>
        </div>
    );
}

export default Login;
