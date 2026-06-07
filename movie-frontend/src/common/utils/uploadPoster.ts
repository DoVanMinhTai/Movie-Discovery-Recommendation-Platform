import { PutObjectCommand } from "@aws-sdk/client-s3";
import { s3Client, BUCKET_NAME } from "./supabaseClient";

export async function uploadPoster(file: File): Promise<string> {
    if (file.type !== "image/jpeg" && file.type !== "image/png" && file.type !== "image/jpg") {
        throw new Error("File phải là ảnh (JPG/PNG) và nhỏ hơn 5MB");
    }
    if (file.size > 5 * 1024 * 1024) {
        throw new Error("File phải là ảnh (JPG/PNG) và nhỏ hơn 5MB");
    }

    const ext = file.name.split(".").pop() || "jpg";
    const key = `posters/${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;

    const arrayBuffer = await file.arrayBuffer();
    const body = new Uint8Array(arrayBuffer);

    const command = new PutObjectCommand({
        Bucket: BUCKET_NAME,
        Key: key,
        Body: body,
        ContentType: file.type,
    });

    await s3Client.send(command);

    return `https://howsuhbubvsdafxtymdm.supabase.co/storage/v1/object/public/Image/${key}`;
}
