const Auth = {
    // Check if user is logged in
    isAuthenticated() {
        return !!this.getToken();
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

    // Get auth headers for API requests
    getAuthHeaders() {
        const token = this.getToken();
        return token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        } : {
            'Content-Type': 'application/json'
        };
    },

    // Login - store tokens and user data
    login(tokens, user) {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user_data', JSON.stringify(user));
        
        // Trigger event for navbar to update
        window.dispatchEvent(new Event('auth-change'));
    },

    // Logout - clear everything
    async logout() {
        const refreshToken = this.getRefreshToken();
        
        // Try to blacklist token on server
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
        
        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        
        // Trigger event for navbar to update
        window.dispatchEvent(new Event('auth-change'));
    },

    // Refresh token if expired
    async refreshToken() {
        const refresh = this.getRefreshToken();
        if (!refresh) return false;

        try {
            const response = await fetch('/api/auth/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }
        
        // If refresh fails, logout
        await this.logout();
        return false;
    },

    // Get user display name
    getUserDisplayName() {
        const user = this.getUser();
        if (!user) return null;
        return user.full_name || user.email.split('@')[0];
    }
};

// Make Auth globally available
window.Auth = Auth;