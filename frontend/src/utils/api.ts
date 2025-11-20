// Use relative URLs by default to work with reverse proxy (nginx/ngrok)
// Set VITE_API_BASE_URL to absolute URL only for local development without nginx
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * Make an authenticated API request with Bearer token.
 * Follows RFC 6750: Bearer tokens are passed in Authorization header as "Bearer <token>"
 */
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = localStorage.getItem('auth_token')
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // RFC 6750: Bearer tokens MUST be sent in Authorization header
  // Format: Authorization: Bearer <token>
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  // RFC 6750: 401 responses include WWW-Authenticate header with error information
  if (response.status === 401) {
    // Token expired or invalid per RFC 6750, clear it and require re-authentication
    localStorage.removeItem('auth_token')
    
    // Extract error information from WWW-Authenticate header if available
    const wwwAuthenticate = response.headers.get('WWW-Authenticate')
    let errorMessage = 'Authentication required'
    
    if (wwwAuthenticate) {
      // Parse RFC 6750 error response: Bearer error="invalid_token", error_description="..."
      const errorMatch = wwwAuthenticate.match(/error="([^"]+)"/)
      const descMatch = wwwAuthenticate.match(/error_description="([^"]+)"/)
      
      if (errorMatch) {
        const errorCode = errorMatch[1]
        const errorDesc = descMatch ? descMatch[1] : errorCode
        errorMessage = errorDesc
      }
    }
    
    throw new Error(errorMessage)
  }

  return response
}

