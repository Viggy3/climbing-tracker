document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("media-modal");
    const modalContent = modal.querySelector(".media-modal-content");
    const background = modal.querySelector(".media-modal-background");



    document.querySelectorAll(".media-thumb").forEach((thumb) => {
        thumb.addEventListener("click", () => {
             console.log("Clicked thumb:", thumb.tagName, thumb.className);
            modalContent.innerHTML = ""; // Clear previous content
            
            if (thumb.tagName.toLowerCase() === "img") {
                const img = document.createElement("img");
                img.src = thumb.src;
                img.className = "modal-media";
                modalContent.appendChild(img);
            } else if (thumb.classList.contains("video-wrapper")) {
                // Video wrapper div - find the video inside
                const videoElement = thumb.querySelector("video");
                if (videoElement) {
                    // Create new video element instead of cloning
                    const video = document.createElement("video");
                    video.className = "modal-media";
                    video.controls = true;
                    video.preload = "metadata";
                    
                    // Copy all source elements
                    const sources = videoElement.querySelectorAll("source");
                    sources.forEach(source => {
                        const new_source = document.createElement("source");
                        new_source.src = source.src;
                        new_source.type = source.type;
                        video.appendChild(new_source);
                    });
                    
                    // If no sources, set src directly
                    if (sources.length === 0 && videoElement.src) {
                        video.src = videoElement.src;
                    }
                    
                    modalContent.appendChild(video);
                    
                    // Load the video to ensure controls work
                    video.load();
                }
            } else if (thumb.tagName.toLowerCase() === "video") {
                // Direct video element (backup case)
                const video = document.createElement("video");
                video.className = "modal-media";
                video.controls = true;
                video.preload = "metadata";
                video.src = thumb.src || thumb.querySelector("source")?.src;
                modalContent.appendChild(video);
                video.load();
            }

            modal.classList.remove("hidden");
        });
    });


    background.addEventListener("click", () => {
        modal.classList.add("hidden");
        modalContent.innerHTML = ""; // Clear content on close
    });
        
});
            