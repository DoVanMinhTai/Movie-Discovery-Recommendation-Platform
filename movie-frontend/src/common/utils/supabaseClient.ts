import { S3Client } from "@aws-sdk/client-s3";

export const BUCKET_NAME = import.meta.env.VITE_SUPABASE_BUCKET || "Image";

export const s3Client = new S3Client({
    endpoint: import.meta.env.VITE_SUPABASE_S3_ENDPOINT,
    region: import.meta.env.VITE_SUPABASE_S3_REGION || "ap-southeast-1",
    credentials: {
        accessKeyId: import.meta.env.VITE_SUPABASE_S3_ACCESS_KEY,
        secretAccessKey: import.meta.env.VITE_SUPABASE_S3_SECRET_KEY,
    },
    forcePathStyle: true,
});
