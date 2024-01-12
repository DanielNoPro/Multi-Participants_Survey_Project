export const TOKEN_STORAGE_KEY = 'token'

export const setToken = (data) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(data))
}

export const getToken = () => {
    if (typeof window !== 'undefined') {
        // Perform localStorage action
        let token = localStorage.getItem(TOKEN_STORAGE_KEY)

        if (token) {
            token = JSON.parse(token)
        }

        return token
    } else {
        console.log('You are on the server')
    }
}

export const getRefresh = () => {
    if (typeof window !== 'undefined') {
        let token = localStorage.getItem('refresh')
        if (token) {
            token = JSON.parse(token)
        }
        return token
    } else {
        console.log('You are on the server')
    }
}

export const clearToken = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem('claim')
    localStorage.removeItem('refresh')
}