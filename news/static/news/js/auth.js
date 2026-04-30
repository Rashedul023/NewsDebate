const Auth = {
    // Check if user is logged in with VALID token
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;
        return this.isTokenValid();  // ← CRITICAL: Check expiration!
    },

    // Get access token
    getToken() {
        return localStorage.getItem('access_token');
    },

    // Get refresh token
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    // Get user data
    getUser() {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    },

    //Check if token is expired
    isTokenValid() {
        const token = this.getToken();
        if (!token) return false;
        
        try {
            // Decode JWT token (it's base64 encoded)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const exp = payload.exp * 1000; // Convert to milliseconds
            const now = Date.now();
            
            if (now >= exp) {
                console.log('⏰ Token expired, clearing session');
                this.clearSession();
                return false;
            }
            return true;
        } catch (error) {
            console.error('Token decode error:', error);
            this.clearSession();
            return false;
        }
    },

    // Clear session without API call (for expired tokens)
    clearSession() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        window.dispatchEvent(new Event('auth-change'));
    },

    // Get auth headers for API requests
    getAuthHeaders() {
        const token = this.getToken();
        if (!token) return { 'Content-Type': 'application/json' };
        
        // Check token validity before returning headers
        if (!this.isTokenValid()) {
            return { 'Content-Type': 'application/json' };
        }
        
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    },

    // Login - store tokens and user data
    login(tokens, user) {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user_data', JSON.stringify(user));
        window.dispatchEvent(new Event('auth-change'));
    },

    // Logout - clear everything
    async logout() {
        const refreshToken = this.getRefreshToken();
        
        if (refreshToken) {
            try {
                await fetch('/api/auth/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.getToken()}`
                    },
                    body: JSON.stringify({ refresh: refreshToken })
                });
            } catch (error) {
                console.warn('Logout API error:', error);
            }
        }
        
        this.clearSession();
        window.location.href = '/';
    },

    // Refresh token if expired
    async refreshToken() {
        const refresh = this.getRefreshToken();
        if (!refresh) return false;

        try {
            const response = await fetch('/api/auth/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                console.log('Token refreshed');
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }
        
        this.clearSession();
        return false;
    },

    // Get user display name
    getUserDisplayName() {
        const user = this.getUser();
        if (!user) return null;
        // Only show name if token is valid
        if (!this.isTokenValid()) return null;
        return user.full_name || user.email.split('@')[0];
    }
};

// Make Auth globally available
window.Auth = Auth;