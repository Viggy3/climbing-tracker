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
(function (){
        const add_media_btn = document.getElementById('add_media_btn');
        const media_input = document.getElementById('media_files');
        const selected_files_div = document.getElementById('selected_files');
        let selected_files = [];


        function updateFileInput() {
            const dt = new DataTransfer();
            selected_files.forEach(file => dt.items.add(file));
            media_input.files = dt.files;
        }

        function displayFiles(){
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

    media_input.addEventListener('change', (e)=> {
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
    (function() {
        let removalList = [];
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

        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', async (event) => {
                showLoading();
                if (removalList.length > 0 ){
                    showLoading();
                    for (const mediaId of removalList) {

                        try {
                            const delete_url = `/api/delete_media/${mediaId}`;
                            const response = await fetch(delete_url, {
                                method: 'DELETE',
                            });
                            if (!response.ok) {
                                console.error(`Failed to delete media ID ${mediaId}:`, response.statusText);
                            } else {
                                console.log(`Successfully deleted media ID ${mediaId}`);
                            }
                            
                        } catch (error) {
                            hideLoading();
                            console.error(`Error deleting media ID ${mediaId}:`, error);
                        }
                    }
                    hideLoading();
                }
            });
        }
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