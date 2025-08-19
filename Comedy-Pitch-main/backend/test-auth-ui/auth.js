// Global variables
let ui;
let firebaseConfig;
let currentUser = null;

// Backend API base URL
const API_BASE = window.location.origin + '/api';

// Initialize the app
document.addEventListener('DOMContentLoaded', async function() {
    await checkBackendStatus();
    await loadFirebaseConfig();
    initFirebaseAuth();
});

// Check if backend is running
async function checkBackendStatus() {
    const statusElement = document.getElementById('server-status');
    try {
        const response = await fetch('/');
        if (response.ok) {
            statusElement.textContent = 'Backend: Online';
            statusElement.className = 'status online';
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        statusElement.textContent = 'Backend: Offline';
        statusElement.className = 'status offline';
        showMessage('Backend server is not running. Please start the server first.', 'error');
    }
}

// Load Firebase configuration from backend
async function loadFirebaseConfig() {
    try {
        const response = await fetch(`/api/auth/config`);
        if (!response.ok) {
            throw new Error(`Failed to load Firebase config, status: ${response.status}`);
        }
        firebaseConfig = await response.json();
        console.log('✅ Firebase config loaded successfully');
    } catch (error) {
        console.error('❌ Error loading Firebase config:', error);
        showMessage('Failed to load Firebase configuration. Is the backend server running?', 'error');
    }
}

// Initialize Firebase Authentication
function initFirebaseAuth() {
    if (!firebaseConfig) {
        showMessage('Firebase configuration not loaded. Cannot initialize authentication.', 'error');
        return;
    }

    try {
        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);
        
        // Initialize Firebase UI
        ui = new firebaseui.auth.AuthUI(firebase.auth());
        
        // Auth state observer
        firebase.auth().onAuthStateChanged(function(user) {
            if (user) {
                // User is signed in
                currentUser = user;
                showUserInfo(user);
                showApiTesting();
                hideFirebaseUI();
            } else {
                // User is signed out
                currentUser = null;
                hideUserInfo();
                hideApiTesting();
                showFirebaseUI();
            }
        });
        
        showMessage('Firebase Authentication initialized successfully!', 'success');
    } catch (error) {
        console.error('Error initializing Firebase:', error);
        showMessage('Failed to initialize Firebase. Please check your configuration.', 'error');
    }
}

// Show Firebase UI for authentication
function showFirebaseUI() {
    // Instead of FirebaseUI, show our custom auth choice
    showAuthChoice();
}

// Show authentication choice
function showAuthChoice() {
    document.getElementById('custom-signin-form').classList.add('hidden');
    document.getElementById('custom-signup-form').classList.add('hidden');
    document.getElementById('password-reset-section').classList.remove('hidden');
    document.getElementById('auth-choice').classList.remove('hidden');
}

// Show sign-in form
function showSignInForm() {
    document.getElementById('auth-choice').classList.add('hidden');
    document.getElementById('custom-signup-form').classList.add('hidden');
    document.getElementById('custom-signin-form').classList.remove('hidden');
    document.getElementById('signin-result').innerHTML = '';
}

// Show sign-up form
function showSignUpForm() {
    document.getElementById('auth-choice').classList.add('hidden');
    document.getElementById('custom-signin-form').classList.add('hidden');
    document.getElementById('custom-signup-form').classList.remove('hidden');
    document.getElementById('signup-result').innerHTML = '';
}

// Perform sign in
async function performSignIn() {
    const email = document.getElementById('signin-email').value.trim();
    const password = document.getElementById('signin-password').value;
    const resultDiv = document.getElementById('signin-result');
    
    if (!email || !password) {
        resultDiv.innerHTML = '<div style="color: #dc3545; margin-top: 10px;">Please enter both email and password</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div style="color: #007bff; margin-top: 10px;">Signing in...</div>';
    
    try {
        const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
        resultDiv.innerHTML = '<div style="color: #28a745; margin-top: 10px;">✅ Sign in successful!</div>';
        console.log('Sign in successful:', userCredential);
        // The auth state change will handle the UI update
    } catch (error) {
        console.error('Sign in error:', error);
        let errorMessage = error.message;
        if (error.code === 'auth/user-not-found') {
            errorMessage = 'No account found with this email. Try creating a new account.';
        } else if (error.code === 'auth/wrong-password') {
            errorMessage = 'Incorrect password. Please try again.';
        } else if (error.code === 'auth/invalid-email') {
            errorMessage = 'Invalid email address format.';
        }
        resultDiv.innerHTML = `<div style="color: #dc3545; margin-top: 10px;">❌ ${errorMessage}</div>`;
    }
}

// Perform sign up
async function performSignUp() {
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const resultDiv = document.getElementById('signup-result');
    
    if (!email || !password) {
        resultDiv.innerHTML = '<div style="color: #dc3545; margin-top: 10px;">Please enter both email and password</div>';
        return;
    }
    
    if (password.length < 6) {
        resultDiv.innerHTML = '<div style="color: #dc3545; margin-top: 10px;">Password must be at least 6 characters long</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div style="color: #007bff; margin-top: 10px;">Creating account...</div>';
    
    try {
        const userCredential = await firebase.auth().createUserWithEmailAndPassword(email, password);
        resultDiv.innerHTML = '<div style="color: #28a745; margin-top: 10px;">✅ Account created successfully!</div>';
        console.log('Sign up successful:', userCredential);
        // The auth state change will handle the UI update
    } catch (error) {
        console.error('Sign up error:', error);
        let errorMessage = error.message;
        if (error.code === 'auth/email-already-in-use') {
            errorMessage = 'An account with this email already exists. Try signing in instead.';
        } else if (error.code === 'auth/weak-password') {
            errorMessage = 'Password is too weak. Please choose a stronger password.';
        } else if (error.code === 'auth/invalid-email') {
            errorMessage = 'Invalid email address format.';
        }
        resultDiv.innerHTML = `<div style="color: #dc3545; margin-top: 10px;">❌ ${errorMessage}</div>`;
    }
}

// Sign in with Google
async function signInWithGoogle() {
    try {
        const provider = new firebase.auth.GoogleAuthProvider();
        const result = await firebase.auth().signInWithPopup(provider);
        console.log('Google sign-in successful:', result);
        showMessage('Google sign-in successful!', 'success');
        // The auth state change will handle the UI update
    } catch (error) {
        console.error('Google sign-in error:', error);
        showMessage(`Google sign-in failed: ${error.message}`, 'error');
    }
}

// Hide Firebase UI
function hideFirebaseUI() {
    document.getElementById('auth-choice').classList.add('hidden');
    document.getElementById('custom-signin-form').classList.add('hidden');
    document.getElementById('custom-signup-form').classList.add('hidden');
    document.getElementById('password-reset-section').classList.add('hidden');
}

// Show user information
function showUserInfo(user) {
    const userDetails = document.getElementById('user-details');
    userDetails.innerHTML = `
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>UID:</strong> ${user.uid}</p>
        <p><strong>Email Verified:</strong> ${user.emailVerified ? 'Yes' : 'No'}</p>
        <p><strong>Last Sign In:</strong> ${new Date(user.metadata.lastSignInTime).toLocaleString()}</p>
    `;
    document.getElementById('user-info').classList.remove('hidden');
    
    // Display the current token for copying
    displayCurrentToken();
}

// Hide user information
function hideUserInfo() {
    document.getElementById('user-info').classList.add('hidden');
}

// Show API testing section
function showApiTesting() {
    document.getElementById('api-testing').classList.remove('hidden');
}

// Hide API testing section
function hideApiTesting() {
    document.getElementById('api-testing').classList.add('hidden');
}

// Sign out function
function signOut() {
    firebase.auth().signOut().then(function() {
        showMessage('Signed out successfully', 'success');
    }).catch(function(error) {
        console.error('Sign out error:', error);
        showMessage('Error signing out', 'error');
    });
}

// Password reset function
async function resetPassword() {
    const email = document.getElementById('reset-email').value.trim();
    const resultDiv = document.getElementById('reset-result');
    
    if (!email) {
        resultDiv.innerHTML = '<div class="error">Please enter your email address</div>';
        return;
    }
    
    try {
        await firebase.auth().sendPasswordResetEmail(email);
        resultDiv.innerHTML = '<div class="success">Password reset email sent! Check your inbox.</div>';
        document.getElementById('reset-email').value = '';
    } catch (error) {
        console.error('Password reset error:', error);
        resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

// Get current user token for API testing
async function getCurrentUserToken() {
    if (!currentUser) {
        console.log('No user signed in');
        return null;
    }
    
    try {
        const token = await currentUser.getIdToken();
        console.log('Current user token retrieved successfully');
        return token;
    } catch (error) {
        console.error('Error getting token:', error);
        return null;
    }
}

// Display current user token for copying
async function displayCurrentToken() {
    const tokenDiv = document.getElementById('current-token-display');
    if (!currentUser) {
        tokenDiv.innerHTML = '<div style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px;">❌ No user signed in</div>';
        return;
    }
    
    try {
        const token = await currentUser.getIdToken();
        const shortToken = token.substring(0, 50) + '...';
        
        tokenDiv.innerHTML = `
            <div style="color: #155724; padding: 10px; background: #d4edda; border-radius: 4px;">
                <strong>🔑 Your Bearer Token:</strong><br>
                <small>${shortToken}</small><br>
                <button onclick="copyTokenToClipboard()" style="margin-top: 5px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    📋 Copy Full Token
                </button>
                <div id="copy-status" style="margin-top: 5px; font-size: 12px;"></div>
            </div>
        `;
        
        // Store the full token for copying
        window.currentUserToken = token;
        
    } catch (error) {
        console.error('Error getting token for display:', error);
        tokenDiv.innerHTML = '<div style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px;">❌ Error retrieving token</div>';
    }
}

// Copy token to clipboard
async function copyTokenToClipboard() {
    if (!window.currentUserToken) {
        document.getElementById('copy-status').innerHTML = '<span style="color: #dc3545;">❌ No token available</span>';
        return;
    }
    
    try {
        await navigator.clipboard.writeText(window.currentUserToken);
        document.getElementById('copy-status').innerHTML = '<span style="color: #28a745;">✅ Token copied to clipboard!</span>';
        
        // Clear the success message after 3 seconds
        setTimeout(() => {
            document.getElementById('copy-status').innerHTML = '';
        }, 3000);
        
    } catch (error) {
        console.error('Error copying token:', error);
        document.getElementById('copy-status').innerHTML = '<span style="color: #dc3545;">❌ Failed to copy token</span>';
    }
}

// Test token verification with backend
async function testTokenVerification() {
    const resultDiv = document.getElementById('token-verification-result');
    resultDiv.innerHTML = '<div style="color: #007bff; padding: 10px; background: #e3f2fd; border-radius: 4px;">Testing token verification...</div>';
    
    const token = await getCurrentUserToken();
    if (!token) {
        resultDiv.innerHTML = '<div style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px;">❌ No user signed in</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/verify-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (response.ok) {
            resultDiv.innerHTML = `<div style="color: #155724; padding: 10px; background: #d4edda; border-radius: 4px;">
                <strong>✅ Token verification successful!</strong><br>
                <small>User: ${result.user?.email || 'N/A'}</small>
            </div>`;
            console.log('Verification result:', result);
        } else {
            resultDiv.innerHTML = `<div style="color: #721c24; padding: 10px; background: #f8d7da; border-radius: 4px;">
                <strong>❌ Token verification failed</strong><br>
                <small>${result.detail || 'Unknown error'}</small>
            </div>`;
        }
    } catch (error) {
        console.error('Token verification error:', error);
        resultDiv.innerHTML = `<div style="color: #721c24; padding: 10px; background: #f8d7da; border-radius: 4px;">
            <strong>❌ Error verifying token</strong><br>
            <small>${error.message}</small>
        </div>`;
    }
}

// Test user profile endpoint
async function testUserProfile() {
    const resultDiv = document.getElementById('user-profile-result');
    resultDiv.innerHTML = '<div style="color: #007bff; padding: 10px; background: #e3f2fd; border-radius: 4px;">Retrieving user profile...</div>';
    
    const token = await getCurrentUserToken();
    if (!token) {
        resultDiv.innerHTML = '<div style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px;">❌ No user signed in</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (response.ok) {
            resultDiv.innerHTML = `<div style="color: #155724; padding: 10px; background: #d4edda; border-radius: 4px;">
                <strong>✅ Profile retrieved successfully!</strong><br>
                <small>Email: ${result.email || 'N/A'}</small><br>
                <small>UID: ${result.uid || 'N/A'}</small><br>
                <small>Verified: ${result.emailVerified ? 'Yes' : 'No'}</small>
            </div>`;
            console.log('Profile data:', result);
        } else {
            resultDiv.innerHTML = `<div style="color: #721c24; padding: 10px; background: #f8d7da; border-radius: 4px;">
                <strong>❌ Failed to get profile</strong><br>
                <small>${result.detail || 'Unknown error'}</small>
            </div>`;
        }
    } catch (error) {
        console.error('Profile retrieval error:', error);
        resultDiv.innerHTML = `<div style="color: #721c24; padding: 10px; background: #f8d7da; border-radius: 4px;">
            <strong>❌ Error getting profile</strong><br>
            <small>${error.message}</small>
        </div>`;
    }
}

// Test list users endpoint (admin function)
async function testListUsers() {
    const resultDiv = document.getElementById('list-users-result');
    resultDiv.innerHTML = '<div style="color: #007bff; padding: 10px; background: #e3f2fd; border-radius: 4px;">Retrieving users list...</div>';
    
    const token = await getCurrentUserToken();
    if (!token) {
        resultDiv.innerHTML = '<div style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px;">❌ No user signed in</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/users`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (response.ok) {
            const userCount = result.users ? result.users.length : (result.count || 0);
            resultDiv.innerHTML = `<div style="color: #155724; padding: 10px; background: #d4edda; border-radius: 4px;">
                <strong>✅ Users list retrieved!</strong><br>
                <small>Total users: ${userCount}</small><br>
                <small>Check browser console for full details</small>
            </div>`;
            console.log('Users:', result);
        } else {
            resultDiv.innerHTML = `<div style="color: #721c24; padding: 10px; background: #f8d7da; border-radius: 4px;">
                <strong>❌ Failed to get users</strong><br>
                <small>${result.detail || 'Unknown error'}</small>
            </div>`;
        }
    } catch (error) {
        console.error('Users list error:', error);
        resultDiv.innerHTML = `<div style="color: #721c24; padding: 10px; background: #f8d7da; border-radius: 4px;">
            <strong>❌ Error getting users list</strong><br>
            <small>${error.message}</small>
        </div>`;
    }
}

// Utility function to show messages
function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.margin = '10px 0';
    messageDiv.style.padding = '10px';
    messageDiv.style.borderRadius = '5px';
    messageDiv.style.border = '1px solid';
    
    if (type === 'success') {
        messageDiv.style.backgroundColor = '#d4edda';
        messageDiv.style.color = '#155724';
        messageDiv.style.borderColor = '#c3e6cb';
    } else if (type === 'error') {
        messageDiv.style.backgroundColor = '#f8d7da';
        messageDiv.style.color = '#721c24';
        messageDiv.style.borderColor = '#f5c6cb';
    }
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
} 