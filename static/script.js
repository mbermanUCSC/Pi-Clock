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
            addNote: document.getElementById('add-note-button'),
            cancelNote: document.getElementById('cancel-note-button'),
        },
        filesContainer: document.getElementById('files-container'),
        filesList: document.getElementById('files-list'),
        fileInput: document.getElementById('file-input'),
        notesList: document.getElementById('notes-list'),
        noteInput: document.getElementById('note-input'),
    };

    var curr_editing = null;
    
    // NOTES
    function updateNoteList() {
        fetch('/notes')
            .then(response => response.json())
            .then(notes => {
                const noteListUl = uiElements.notesList.querySelector('ul'); 
                noteListUl.innerHTML = ''; // Clear existing <li> elements

                notes.forEach(note => {
                    const li = document.createElement('li'); // Create a new <li> element for each note
                    li.textContent = note;

                    // Create buttons
                    const editBtn = document.createElement('button');
                    editBtn.textContent = 'Edit';
                    editBtn.onclick = function() { editNote(note); };

                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = 'Delete';
                    deleteBtn.onclick = function() { deleteNote(note); };

                    // Append buttons to the li element
                    li.appendChild(editBtn);
                    li.appendChild(deleteBtn);

                    noteListUl.appendChild(li); // Append the <li> to the <ul>
                });
            })
            .catch(error => {
                document.querySelector('#notes-list ul').innerHTML = '<li>Failed to load notes.</li>';
            });
    }
    updateNoteList();

    // add a note
    uiElements.buttons.addNote.addEventListener('click', () => {
        if (curr_editing) {
            // delete the note being edited
            deleteNote(curr_editing, true);
            curr_editing = null;
        }
        const note = uiElements.noteInput.value;
        if (note) {
            // send a request to the server to add the note
            fetch('/notes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ note }),
            })
            .then(response => {
                if (response.ok) {
                    updateNoteList();
                    uiElements.noteInput.value = '';
                }
            });
        }
    });

    // cancel editing a note
    uiElements.buttons.cancelNote.addEventListener('click', () => {
        const allNotes = document.querySelectorAll('#notes-list ul li');
        allNotes.forEach(noteElem => {
            noteElem.classList.remove('editing-note');
        });
        curr_editing = null;
        uiElements.noteInput.value = '';
    });

    // delete a note
    function deleteNote(note, editing=false) {
        // confirm the user wants to delete the note
        if (editing) {
            if (!confirm(`Are you sure you want to override "${note}"?`)) {
                return;
        }
        }
        else{
            if (!confirm(`Are you sure you want to delete "${note}"?`)) {
                return;
            }
        }

        // send a request to the server to delete the note
        fetch(`/notes/${note}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    updateNoteList();
                }
            });
    }

    // edit a note
    function editNote(note) {
        console.log('Editing note', note);
        curr_editing = note;
    
        // Find all note elements and remove editing style
        const allNotes = document.querySelectorAll('#notes-list ul li');
        allNotes.forEach(noteElem => {
            noteElem.classList.remove('editing-note');
        });
    
        // Find the specific note element and add editing style
        const noteListUl = uiElements.notesList.querySelector('ul');
        const notes = noteListUl.getElementsByTagName('li');
        Array.from(notes).forEach(noteElem => {
            if (noteElem.textContent.includes(note)) { // Assumes textContent includes the note content only
                noteElem.classList.add('editing-note');
                uiElements.noteInput.value = note;  // Set the input field to the note being edited
            }
        });
    }
    



    // FILES
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
                            // if music file, add the song with a music player
                            if (fileType === 'audio') {
                                const audio = document.createElement('audio');
                                audio.controls = true;
                                // replace %20 with space
                                audio.src = `/download/${file.replace(/%20/g, ' ')}`;
                                li.appendChild(audio);
                                break;
                            }
                            // if image file, add the image (very 10% of the original size)
                            if (fileType === 'image') {
                                const img = document.createElement('img');
                                img.src = `/download/${file.replace(/%20/g, ' ')}`;
                                img.style.width = '10%';
                                li.appendChild(img);
                                break;
                            }

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

    // when a file is selected, upload it
    uiElements.fileInput.addEventListener('change', function() {
        const files = uiElements.fileInput.files;

        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                updateFileList();
                // Clear the file input
                uiElements.fileInput.value = '';
                
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
