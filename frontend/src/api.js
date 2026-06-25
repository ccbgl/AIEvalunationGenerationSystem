import axios from 'axios'

const api = axios.create({ baseURL: (import.meta.env.VITE_API_BASE || '/'), timeout: 15000 })

api.interceptors.request.use(config=>{
  const token = localStorage.getItem('token')
  if(token){
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  // debug: log outgoing requests and whether Authorization header is attached
  try{
    // eslint-disable-next-line no-console
    console.debug('[api] request', config.method, config.url, 'auth=', config.headers && config.headers.Authorization ? 'yes' : 'no')
  }catch(e){}
  return config
})

// Response interceptor: on 401 clear local auth state and redirect to login
api.interceptors.response.use(
  res => res,
  err => {
    try{
      const status = err?.response?.status
      if(status === 401){
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // use full-page redirect to ensure router state resets
        window.location.href = '/login'
      }
        if(status === 403){
          // show a user-friendly message for forbidden access
          try{
            const detail = err?.response?.data?.detail || 'You do not have permission to perform this action.'
            // use alert for simplicity; frontend can replace with toast later
            window.alert(detail)
          }catch(e){ console.warn('showing 403 message failed', e) }
          // optionally redirect to home
          // window.location.href = '/'
        }
      }catch(e){ console.warn('auth response interceptor error', e) }
      return Promise.reject(err)
    }
)

export default api
