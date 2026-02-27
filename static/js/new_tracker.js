function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}
(function () {
    const gradingSystem = document.getElementById('grading_system');
    const gradeSelect = document.getElementById('grade');
    const vOptions = Array.from(document.querySelectorAll('.v-option'));
    const fontOptions = Array.from(document.querySelectorAll('.font-option'));

    function setSystem(system) {
        if (system === 'v_grade') {
            // show/enable V, hide/disable Font
            document.querySelector('.v-grade-options').style.display = 'block';
            document.querySelector('.font-grade-options').style.display = 'none';

            // pick first enabled v option if current selection was font or invalid
            if (!gradeSelect.value || gradeSelect.value.toUpperCase().startsWith('V') === false) {
                const first = vOptions.find(o => !o.disabled);
                if (first) gradeSelect.value = first.value;
            }
        } else {
            // show/enable Font, hide/disable V
            document.querySelector('.v-grade-options').style.display = 'none';
            document.querySelector('.font-grade-options').style.display = 'block';

            // pick first enabled font option if current selection was v or invalid
            if (!gradeSelect.value || gradeSelect.value.toUpperCase().startsWith('V')) {
                const first = fontOptions.find(o => !o.disabled);
                if (first) gradeSelect.value = first.value;
            }
        }
        // ensure required still works
        gradeSelect.required = true;
    }

    // initial setup on load
    setSystem(gradingSystem.value);

    // listen for changes
    gradingSystem.addEventListener('change', (e) => {
        setSystem(e.target.value);
    });
})();
//file picker logic
(function () {
    const add_media_btn = document.getElementById('add_media_btn');
    const media_input = document.getElementById('media_files');
    const selected_files_div = document.getElementById('selected_files');
    let selected_files = [];

    // Expose so the submit handler below can access the files
    window.getSelectedFiles = () => selected_files;

    function updateFileInput() {
        const dt = new DataTransfer();
        selected_files.forEach(file => dt.items.add(file));
        media_input.files = dt.files;
    }

    function displayFiles() {
        selected_files_div.innerHTML = '';
        if (selected_files.length === 0) {
            return;
        }
        selected_files.forEach((file, index) => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';

            const fileName = document.createElement('span');
            fileName.textContent = file.name;
            fileName.className = 'file-name';

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-file-btn';
            removeBtn.textContent = '×';
            removeBtn.addEventListener('click', () => {
                selected_files.splice(index, 1);
                updateFileInput();
                displayFiles();
            });

            fileDiv.appendChild(fileName);
            fileDiv.appendChild(removeBtn);
            selected_files_div.appendChild(fileDiv);
        });



    }
    add_media_btn.addEventListener('click', () => {
        media_input.click();
    });

    media_input.addEventListener('change', (e) => {
        const newFiles = Array.from(e.target.files);

        newFiles.forEach(file => {
            // avoid duplicates
            if (!selected_files.some(f => f.name === file.name && f.size === file.size)) {
                selected_files.push(file);
            }
        });
        updateFileInput();
        displayFiles();

    })
})();

function uploadWithProgress(url, file, onProgress) {
    return new Promise((resolve, reject) => {
        const overlay = document.getElementById('upload-overlay');
        const progressBar = document.getElementById('upload-progress-bar');
        const progressText = document.getElementById('upload-progress-text');
        const label = document.getElementById('upload-overlay-label');
        const cancelBtn = document.getElementById('upload-cancel-btn');

        // Show overlay
        overlay.style.display = 'flex';
        label.textContent = `Uploading ${file.name}...`;
        progressBar.style.width = '0%';
        progressText.textContent = '0%';

        const xhr = new XMLHttpRequest();
        xhr.open('PUT', url);
        xhr.setRequestHeader('Content-Type', file.type);

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = `${percent}%`;
                progressText.textContent = `${percent}%`;
                onProgress(percent);
            }
        });

        xhr.addEventListener('load', () => {
            progressBar.style.width = '100%';
            progressText.textContent = '100%';
            label.textContent = 'Upload complete!';
            resolve(xhr);
        });

        xhr.addEventListener('error', () => {
            overlay.style.display = 'none';
            reject(new Error('Upload failed'));
        });

        // Cancel button
        cancelBtn.onclick = () => {
            xhr.abort();
            overlay.style.display = 'none';
            reject(new Error('Upload cancelled'));
        };

        xhr.send(file);
    });
}
(function () {
    const form = document.querySelector('form');
    const submitBtn = document.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (e) => {

        e.preventDefault();

        // Disable the submit button to prevent multiple clicks
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-small"></span> Uploading...';

        const selecetedFiles = window.getSelectedFiles ? window.getSelectedFiles() : [];


        try {
            //generate a new id for the climb before submitting the form so that media can be associated with it
            const idRes = await fetch('/api/new_tracker_id')
            const { tracker_id } = await idRes.json();

            const uploadedMedia = [];

            //for each file get a presigned url and upload it directly to s3
            for (const file of selecetedFiles) {
                const url = await fetch('/api/get_upload_url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: file.name, content_type: file.type, tracker_id })
                })

                const { upload_url, key } = await url.json();
                console.log('upload_url:', upload_url);
                console.log('file:', file.name, file.type);
                //upload the file directly to s3
                await uploadWithProgress(upload_url, file, (percent) => {
                    submitBtn.innerHTML = `<span class="spinner-small"></span> Uploading... ${percent}%`;
                });

                let thumbnail_key = null;
                if (file.type.startsWith('video/')) {
                    const thumbnailBlob = await generateVideoThumbnail(file);
                    if (thumbnailBlob) {
                    const thumbRes = await fetch('/api/get_upload_url', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename: 'thumbnail.jpg', content_type: 'image/jpeg', tracker_id })
                    });
                    const { upload_url: thumbUrl, key: thumbKey } = await thumbRes.json();
                    await fetch(thumbUrl, {
                        method: 'PUT',
                        body: thumbnailBlob,
                        headers: { 'Content-Type': 'image/jpeg' }
                    });
                    thumbnail_key = thumbKey;

                    console.log('Generated thumbnail for video:', file.name);
                    }
                }
                
                console.log(upload_url);
                uploadedMedia.push({
                    filename: file.name,
                    key: key,
                    content_type: file.type,
                    size: file.size,
                    thumbnail_key: thumbnail_key
                });
            }

            const formData = new FormData(form);
            const res = await fetch('/api/create_tracker', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tracker_id: tracker_id,
                    climb_name: formData.get('climb_name'),
                    grade: formData.get('grade'),
                    grading_system: formData.get('grading_system'),
                    date: formData.get('date'),
                    description: formData.get('description'),
                    attempts: formData.get('attempts'),
                    complete: formData.get('complete') === 'on',
                    media_files: uploadedMedia
                })
            });

            const result = await res.json();
            if (result.success) {
                // Show success toast
                const toast = document.getElementById('upload-toast');
                toast.style.display = 'block';
                setTimeout(() => {
                    toast.style.display = 'none';
                    window.location.href = '/user/my_tracker';
                }, 2000);
            }
            else {
                alert('Error saving climb: ' + (result.error || 'Unknown error'));
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit';
            }
        }
        catch (err) {
            console.error('Error:', err);
            alert('An error occurred while saving the climb. Please try again.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit';
        }
    });

})();

async function generateVideoThumbnail(file) {
    return new Promise((resolve) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        video.muted = true; // mute to avoid autoplay issues
        video.playsInline = true; // for mobile compatibility
        
        video.onloadedmetadata = () => {
            console.log('metadata loaded, duration:', video.duration, 'codec may be HEVC');
            video.currentTime = 0.1; // seek to 0.1s to ensure we get a frame 
        };

        const cleanup = () => {
            URL.revokeObjectURL(video.src);
        }

        const timeout = setTimeout(() => {
            console.warn('Thumbnail generation timed out, possibly due to unsupported codec');
            cleanup();
            resolve(null); // resolve with null if thumbnail generation takes too long
        }, 5000); // 5 second timeout
        
        video.onseeked = () => {
            console.log('seeked successfully, generating thumbnail');
            clearTimeout(timeout);
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            canvas.toBlob((blob) => {
                cleanup();
                resolve(blob);
            }, 'image/jpeg', 0.75);
        };
        video.onerror = () => {
            console.error('video error:', video.error?.code, video.error?.message);
            clearTimeout(timeout);
            cleanup();
            resolve(null); // resolve with null if there's an error loading the video
        }

        video.src = URL.createObjectURL(file);
        video.load();
    });
}