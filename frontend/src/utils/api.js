const BASE_URL = 'http://localhost:8000/api';

export const api = {
    // Utility to get token
    //localStorage is an object provided by the browser to:
    //Store data in the user's browser permanently (until manually cleared)
    getToken: () => localStorage.getItem('access_token'),
    
    // Utility to set token
    setToken: (token) => localStorage.setItem('access_token', token),
    
    // Utility to remove token
    removeToken: () => localStorage.removeItem('access_token'),

    // Helper for making requests
    async request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        
        let headers = {};
        
        // If data is FormData, do not set Content-Type so browser sets boundary automatically
        if (options.body && options.body instanceof FormData) {
            headers = { ...options.headers };
        } else {
            headers = {
                'Content-Type': 'application/json',
                ...options.headers,
            };
        }

        const token = this.getToken();
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Some endpoints like logout might just return 200 without a complex JSON body
        // Or if it fails, we want to try parsing the detail
        const contentType = response.headers.get("content-type");
        let data = null;
        if (contentType && contentType.indexOf("application/json") !== -1) {
             data = await response.json();
        }

        if (!response.ok) {
            const errorMsg = data?.detail || response.statusText || 'An error occurred';
            throw new Error(errorMsg);
        }

        return data;
    },

    // Authentication endpoints
    register: (userData) => {
        return api.request('/register/', {
            method: 'POST',
            body: userData
        });
    },

    login: (credentials) => {
        return api.request('/login/', {
            method: 'POST',
            body: credentials instanceof FormData ? credentials : JSON.stringify(credentials)
        });
    },

    logout: () => {
        return api.request('/logout/', {
            method: 'POST'
        });
    }
};
