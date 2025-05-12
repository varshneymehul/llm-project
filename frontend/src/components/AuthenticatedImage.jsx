import { useState, useEffect } from "react";
import axios from "axios";

function AuthenticatedImage({ src, alt, className, token }) {
  const [imageData, setImageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchImage = async () => {
      try {
        setLoading(true);
        const response = await axios.get(src, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: 'blob',
        });
        
        // Create a URL for the blob
        const imageUrl = URL.createObjectURL(response.data);
        setImageData(imageUrl);
        setError(null);
      } catch (err) {
        console.error("Failed to load image:", err);
        setError(`Failed to load image: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    if (src) {
      fetchImage();
    }

    // Clean up the URL object when component unmounts
    return () => {
      if (imageData) {
        URL.revokeObjectURL(imageData);
      }
    };
  }, [src, token]);

  if (loading) {
    return <div className="bg-gray-800 animate-pulse h-48 w-full rounded"></div>;
  }

  if (error) {
    return (
      <div className="bg-red-900 text-white p-4 rounded text-center">
        {error}
      </div>
    );
  }

  return <img src={imageData} alt={alt} className={className} />;
}

export default AuthenticatedImage;