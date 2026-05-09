const BASE_URL = "http://127.0.0.1:8000";

/**
 * Core request helper.
 * Automatically attaches JWT token and throws on non-2xx responses.
 */
async function apiRequest(endpoint, method = "GET", data = null) {
    const token = localStorage.getItem("access_token");

    const options = {
        method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, options);

    // Handle 401 globally: token expired or invalid
    if (response.status === 401) {
        localStorage.clear();
        window.location.href = determineLoginPage();
        return;
    }

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.detail || `Request failed (${response.status})`);
    }

    return result;
}

/** Determines which login page to redirect to based on current path */
function determineLoginPage() {
    const path = window.location.pathname;
    return path.includes('/admin/') ? '/admin/login.html' : '/user/login.html';
}

/**
 * Register a new citizen account.
 * POST /auth/register
 * Body: { full_name, email, password, role }
 */
async function registerUser(userData) {
    return await apiRequest("/auth/register", "POST", {
        full_name: userData.full_name,
        email: userData.email,
        password: userData.password,
        role: "user"  // always "user" for citizen registration
    });
}

/**
 * Login — citizen or admin.
 * POST /auth/login
 * Body: { email, password, role }
 * NOTE: role defaults to "user" if not provided; admin login page passes "admin"
 */
async function loginUser(userData) {
    const result = await apiRequest("/auth/login", "POST", {
        email: userData.email,
        password: userData.password,
        role: userData.role || "user"   // FIX: schema requires role field
    });

    localStorage.setItem("access_token", result.access_token);
    localStorage.setItem("user_role", result.user.role);
    localStorage.setItem("user_name", result.user.full_name);
    localStorage.setItem("user_id", result.user.id);

    return result;
}

/**
 * Logout — clear storage and redirect.
 */
function logoutUser() {
    localStorage.clear();
    window.location.href = "/index.html";
}

/**
 * Submit a new complaint.
 * POST /complaints/
 * Body: ComplaintCreate schema fields
 */
async function submitComplaint(complaintData) {
    return await apiRequest("/complaints/", "POST", {
        title: complaintData.title,
        description: complaintData.description,
        location: complaintData.location,
        city: complaintData.city,
        state: complaintData.state,
        pin_code: complaintData.pin_code,
        contact_number: complaintData.contact_number
    });
}

/**
 * Get a single complaint by ID.
 * GET /complaints/{id}
 */
async function getComplaint(id) {
    return await apiRequest(`/complaints/${id}`, "GET");
}

/**
 * Auth guard — call this at the top of every protected page.
 * Redirects to login if no token is present.
 * @param {string} requiredRole - 'user' or 'admin'
 */
function requireAuth(requiredRole = 'user') {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role');

    if (!token) {
        window.location.href = requiredRole === 'admin'
            ? '/admin/login.html'
            : '/user/login.html';
        return false;
    }

    if (requiredRole === 'admin' && role !== 'admin') {
        window.location.href = '/user/dashboard.html';
        return false;
    }

    if (requiredRole === 'user' && role === 'admin') {
        window.location.href = '/admin/dashboard.html';
        return false;
    }

    return true;
}
