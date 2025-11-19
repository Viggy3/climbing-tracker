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

(function(){
    form.addEventListener('submit', () => {
        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-small"></span> Uploading...';
            showLoading();
        }
    });
});