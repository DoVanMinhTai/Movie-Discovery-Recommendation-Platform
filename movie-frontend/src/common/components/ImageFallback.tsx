import React, { useState } from 'react';

interface ImageFallbackProps extends React.ImgHTMLAttributes<HTMLImageElement> {
    src?: string;
    fallbackSrc?: string;
    alt?: string;
}

const ImageFallback: React.FC<ImageFallbackProps> = ({
    src,
    fallbackSrc = "/image_fallback.png",
    alt,
    className,
    ...props
}) => {
    const [imgSrc, setImgSrc] = useState<string | undefined>(src);
    const [hasError, setHasError] = useState(false);

    const handleError = () => {
        if (!hasError) {
            setImgSrc(fallbackSrc);
            setHasError(true);
        } else if (imgSrc !== "/image_fallback.png") {
            // Trường hợp cả src và fallbackSrc đều lỗi (nếu fallbackSrc là link ngoài)
            // Hoặc ép buộc hiển thị file local nếu vẫn lỗi
            setImgSrc("/image_fallback.png");
        }
    };

    return (
        <img
            {...props}
            src={imgSrc || "/image_fallback.png"}
            alt={alt}
            onError={handleError}
            className={className}
        />
    );
};

export default ImageFallback;
