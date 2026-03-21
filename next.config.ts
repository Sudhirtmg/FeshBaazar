// import type { NextConfig } from "next";

// const nextConfig: NextConfig = {};

// export default nextConfig;



// for live
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: "https://freshbazaar-api.onrender.com/api/:path*"
            },
        ];
    },
};

export default nextConfig;