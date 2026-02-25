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
    const gradeSelect = document.getElementById('edit_climb_grade');
    const vOptions = Array.from(document.querySelectorAll('.v-option'));
    const fontOptions = Array.from(document.querySelectorAll('.font-option'));

    function setSystem(system) {
        if (system === 'v_grade') {
            // show V grade options, hide Font grade options
            document.querySelector('.v-grade-options').style.display = 'block';
            document.querySelector('.font-grade-options').style.display = 'none';

            // pick first V option if current selection was font or invalid
            if (!gradeSelect.value || !gradeSelect.value.toUpperCase().startsWith('V')) {
                gradeSelect.value = 'VB';
            }
        } else {
            // show Font grade options, hide V grade options
            document.querySelector('.v-grade-options').style.display = 'none';
            document.querySelector('.font-grade-options').style.display = 'block';

            // pick first Font option if current selection was V or invalid
            if (!gradeSelect.value || gradeSelect.value.toUpperCase().startsWith('V')) {
                gradeSelect.value = '3';
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
(function () {
    const add_media_btn = document.getElementById('add_media_btn');
    const media_input = document.getElementById('media_files');
    const selected_files_div = document.getElementById('selected_files');
    let selected_files = [];

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
            if (!selected_files.some(f => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified)) {
                selected_files.push(file);
            }
        });
        updateFileInput();
        displayFiles();

    })
})();

// Handle removal of existing media
(function () {
    let removalList = [];

    window.getRemovalList = () => removalList;

    const removeButtons = document.querySelectorAll('.remove-existing-media-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const mediaId = button.getAttribute('data-media-id');
            console.log(`Request to remove media ID: ${mediaId}`);

            const mediaItem = button.closest('.media-item');
            if (!removalList.includes(mediaId)) {
                removalList.push(mediaId);
            }

            if (mediaItem) {
                mediaItem.classList.add('marked-for-deletion');
            }

            button.style.display = 'none';

            const undoBtn = document.createElement('button');
            undoBtn.type = 'button';
            undoBtn.textContent = '↶';
            undoBtn.className = 'undo-remove-btn';
            undoBtn.title = 'Undo removal';


            undoBtn.addEventListener('click', () => {
                const index = removalList.indexOf(mediaId);
                if (index > -1) {
                    removalList.splice(index, 1);
                }
                mediaItem.classList.remove('marked-for-deletion');
                button.style.display = 'inline-block';
                undoBtn.remove();
            });

            mediaItem.appendChild(undoBtn);
        });
    });

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
            overlay.style.display = 'none';
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

(function() {
    const form = document.querySelector('form');
    const submitBtn = document.querySelector('button[type="submit"]');

    //get tracker id from URL
    const trackerId = window.location.pathname.split('/').pop();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-small"></span> Saving...';
        console.log('Submitting form for tracker ID:', trackerId);
        try {
            console.log('Selected files to upload:', window.getSelectedFiles());
            // first delete any media marked for removal
            for (const mediaId of window.getRemovalList()) {
                await fetch(`/api/delete_media/${mediaId}`, {method: 'DELETE'});
            }

            // then submit any new media files directly to the tracker
            const uploadedMedia = [];
            for (const file of window.getSelectedFiles()) {
                const URLRes = await fetch('/api/get_upload_url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: file.name, content_type: file.type, trackerId })
                });
                const { upload_url, key } = await URLRes.json();
                console.log('upload_url:', upload_url);
                console.log('file:', file.name, file.type);
                await uploadWithProgress(upload_url, file, (percent) => {
                    submitBtn.innerHTML = `<span class="spinner-small"></span> Uploading... ${percent}%`;
                });
                console.log(upload_url);
                
                let thumbnail_key = null;
                if (file.type.startsWith('video/')) {
                    const thumbnailBlob = await generateVideoThumbnail(file);
                    const thumbRes = await fetch('/api/get_upload_url', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename: 'thumbnail.jpg', content_type: 'image/jpeg', tracker_id: trackerId })
                    });
                    const { upload_url: thumbUrl, key: thumbKey } = await thumbRes.json();
                    await fetch(thumbUrl, {
                        method: 'PUT',
                        body: thumbnailBlob,
                        headers: { 'Content-Type': 'image/jpeg' }
                    });
                    thumbnail_key = thumbKey;
                }

                
                uploadedMedia.push({
                    filename: file.name,
                    key: key,
                    content_type: file.type,
                    size: file.size,
                    thumbnail_key: thumbnail_key
                });
            }

            // finally submit the form data to update the tracker

            const formData = new FormData(form);
            const res = await fetch(`/api/update_tracker/${trackerId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    edit_climb_grade: formData.get('edit_climb_grade'),
                    edit_climb_description: formData.get('edit_climb_description'),
                    edit_climb_attempts: formData.get('edit_climb_attempts'),
                    edit_climb_complete: formData.get('edit_climb_complete') === 'on',
                    media_files: uploadedMedia
                })
            });

            const result = await res.json();

            if (result.success) {   
                const toast = document.getElementById('upload-toast');
                toast.style.display = 'block';
                setTimeout(() => {
                    toast.style.display = 'none';
                    window.location.href = '/user/my_tracker';
                }, 2000);
            } else {
                alert('Error saving: ' + (result.error || 'Unknown error'));
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save Changes';
            }
        }

        catch (err) {
            console.error(err);
            alert('Save failed. Please try again.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save Changes';
        }
    });
})();

function deleteTracker(trackerId) {
    const confirmed = confirm('Are you sure you want to delete this entire tracker? This will remove all climb data and media files. This action cannot be undone.');

    if (confirmed) {
        showLoading('Deleting tracker...');
        fetch(`/api/delete_tracker/${trackerId}`, {
            method: 'DELETE',
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/user/my_tracker'; // Redirect to trackers page after deletion
                } else {
                    console.error('Failed to delete tracker:', response.statusText);
                    alert('Failed to delete tracker. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error deleting tracker:', error);
                alert('An error occurred while deleting the tracker. Please try again.');
            });
    }
}

async function generateVideoThumbnail(file) {
    return new Promise((resolve) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        
        video.src = URL.createObjectURL(file); // load from local file, not R2
        video.currentTime = 1; // seek to 1 second
        
        video.oncanplay = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            canvas.toBlob((blob) => {
                URL.revokeObjectURL(video.src); // cleanup memory
                resolve(blob);
            }, 'image/jpeg', 0.8);
        };
    });
}