// dict for classifying file types
const fileTypes = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'],
    'video': ['mp4', 'avi', 'mov', 'mkv', 'wmv'],
    'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
    'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'],
    'code': ['html', 'css', 'js', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'php'],
    'archive': ['zip', 'rar', '7z', 'tar', 'gz'],
    'disk': ['iso', 'img'],
    'database': ['sql', 'db', 'sqlite'],
    'executable': ['exe', 'msi'],
    'font': ['ttf', 'otf', 'woff', 'woff2'],
    'presentation': ['ppt', 'pptx'],
    'spreadsheet': ['xls', 'xlsx'],
    'text': ['txt'],
    'web': ['html', 'css', 'js'],
};


document.addEventListener('DOMContentLoaded', function() {
    const uiElements = {
        buttons: {
            reset: document.getElementById('reset-button'),
            restart: document.getElementById('restart-button'),
            power: document.getElementById('power-button'),
        },
        filesContainer: document.getElementById('files-container'),
        filesList: document.getElementById('files-list')
    };

    // Fetch files and display them
    function updateFileList() {
        fetch('/files')
            .then(response => response.json())
            .then(files => {
                const fileListUl = document.querySelector('#files-list ul'); // Select the <ul> within #files-list
                fileListUl.innerHTML = ''; // Clear existing <li> elements

                files.forEach(file => {
                    const li = document.createElement('li'); // Create a new <li> element for each file
                    li.textContent = file;

                    // Create buttons
                    const viewBtn = document.createElement('button');
                    viewBtn.textContent = 'Download';
                    viewBtn.onclick = function() { downloadFile(file); };

                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = 'Delete';
                    deleteBtn.onclick = function() { deleteFile(file); };

                    // Append buttons to the li element
                    li.appendChild(viewBtn);
                    li.appendChild(deleteBtn);

                    // Get the file extension to determine the file type
                    const fileExtension = file.split('.').pop();
                    let fileType = 'other';
                    for (const type in fileTypes) {
                        if (fileTypes[type].includes(fileExtension)) {
                            fileType = type;
                            break;
                        }
                    }

                    // Add text saying what type of file it is
                    const fileTypeSpan = document.createElement('span');
                    fileTypeSpan.textContent = fileType;
                    fileTypeSpan.className = 'file-type';
                    li.appendChild(fileTypeSpan);



                    fileListUl.appendChild(li); // Append the <li> to the <ul>
                });
            })
            .catch(error => {
                document.querySelector('#files-list ul').innerHTML = '<li>Failed to load files.</li>';
            });
    }
    updateFileList();

    // Example callback functions
    function downloadFile(fileName) {
        console.log('Downloading', fileName);
        // semd a request to the server to download the file
        fetch(`/download/${fileName}`)
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            a.click();
        });
    }

    function deleteFile(fileName) {
        console.log('Deleting', fileName);
        // confirm the user wants to delete the file
        if (!confirm(`Are you sure you want to delete ${fileName}?`)) {
            return;
        }
        // send a request to the server to delete the file
        fetch(`/delete/${fileName}`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                updateFileList();
            }
        });
    }


    // drag and drop for file upload on files-list
    //first, prevent the default behavior of the browser when a file is dragged over the page
    uiElements.filesContainer.addEventListener('dragover', function(event) {
        event.preventDefault();
    });


    // Add a drop event listener to the document
    uiElements.filesContainer.addEventListener('drop', function(event) {
        event.preventDefault();
        // Get the file(s) that were dropped
        const files = event.dataTransfer.files;

        // Create a FormData object to send the files
        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }

        // Send a POST request to the server
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                updateFileList();
            }
        });
    });


    uiElements.buttons.reset.addEventListener('click', () => {
       // fetch, resets the software
        fetch('/reset')
        .then(response => {
            if (response.ok) {
                alert('Software reset');
            }
        });
    });



    uiElements.buttons.restart.addEventListener('click', () => {
        // fetch, restarts the pi
        fetch('/restart')
        .then(response => {
            if (response.ok) {
                alert('Server restarting');
            }
        });
    });

    uiElements.buttons.power.addEventListener('click', () => {
        // fetch, powers off the pi
        fetch('/power')
        .then(response => {
            if (response.ok) {
                alert('Server shutting down');
            }
        });
    });
});
