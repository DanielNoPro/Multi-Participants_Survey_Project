/** @type {import('next').NextConfig} */
const nextConfig = {
    async redirects() {
        return [
            {
                source: '/',
                destination: '/dashboard/survey/',
                permanent: false,
            },
        ]
    },
}

module.exports = nextConfig
