import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../utils/api';

function Register() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        position: '',
        password: ''
    });

    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    // Webcam scanning states and refs
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isScanning, setIsScanning] = useState(false);
    const [scanProgress, setScanProgress] = useState(0);
    const [capturedImages, setCapturedImages] = useState([]);
    const [webcamActive, setWebcamActive] = useState(false);

    useEffect(() => {
        // Start webcam when component mounts
        startWebcam();
        return () => {
            stopWebcam();
        };
    }, []);

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

        // Set canvas to match video dimensions
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        for (let i = 0; i < 15; i++) {
            // Draw current video frame to canvas
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert to blob
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
            images.push(blob);
            
            setScanProgress(i + 1);
            
            // Wait 300ms between captures
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
        
        if (capturedImages.length < 15) {
            setError("Please scan your face before registering.");
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const submitData = new FormData();
            submitData.append('username', formData.username);
            submitData.append('email', formData.email);
            submitData.append('position', formData.position);
            submitData.append('password', formData.password);

            // Append all 15 images
            capturedImages.forEach((blob, index) => {
                submitData.append('images', blob, `face_${index}.jpg`);
            });

            await api.register(submitData);
            
            stopWebcam();
            navigate('/login', { state: { message: 'Registration successful! Please log in.' } });
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card" style={{ maxWidth: '600px' }}>
                <h2>Create Account</h2>
                <p>Register to access the platform</p>
                
                {error && <div className="error-message">{error}</div>}
                
                <form onSubmit={handleSubmit} className="auth-form" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    
                    {/* Face Scanning Section */}
                    <div className="form-group" style={{ textAlign: 'center' }}>
                        <label>Face Registration</label>
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
                                style={{ backgroundColor: capturedImages.length === 15 ? '#28a745' : '' }}
                            >
                                {isScanning ? `Scanning (${scanProgress}/15)...` : capturedImages.length === 15 ? 'Face Scanned Successfully ✓' : 'Scan Face'}
                            </button>
                        </div>
                    </div>

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
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
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
                    
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" disabled={isLoading || capturedImages.length < 15} className="submit-btn content-button">
                        {isLoading ? 'Registering...' : 'Sign Up'}
                    </button>
                </form>
                
                <div className="auth-footer">
                    Already have an account? <Link to="/login">Log in</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
