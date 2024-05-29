from flask import Flask, jsonify, render_template, request, send_from_directory
from datetime import datetime
import os
import subprocess


# ------------------------ #
# STARTUP & HELPERS
# ------------------------ #

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

notes = []
def load_notes():
    if os.path.exists('notes.txt'):
        with open('notes.txt') as f:
            for line in f:
                notes.append(line.strip())
load_notes()

def save_notes():
    with open('notes.txt', 'w') as f:
        for note in notes:
            f.write(note + '\n')

@app.route('/')
def home():
    return render_template('index.html')



# ------------------------ #
# PI METHODS
# ------------------------ #

# reset
@app.route('/reset')
def reset():
    return jsonify(success=True, message="System reset.")

# restart
@app.route('/restart')
def restart():
    try:
        subprocess.run(["sudo", "reboot", "now"], check=True)
        return jsonify(success=True, message="System is rebooting.")
    except subprocess.CalledProcessError:
        return jsonify(success=False, message="Failed to reboot."), 500

# power
@app.route('/power')
def power():
    try:
        subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        return jsonify(success=True, message="System is shutting down.")
    except subprocess.CalledProcessError:
        return jsonify(success=False, message="Failed to shut down."), 500



# ------------------------ #
# NOTES
# ------------------------ #

@app.route('/notes')
def get_notes():
    return jsonify(notes)


@app.route('/notes/<note>', methods=['DELETE'])
def delete_note(note):
    if note in notes:
        notes.remove(note)
        save_notes()
        return jsonify({'message': 'Note deleted'})
    else:
        return jsonify({'error': 'Note not found'}), 404

# add note
@app.route('/notes', methods=['POST'])
def add_note():
    note = request.json.get('note')
    notes.append(note)
    save_notes()
    return jsonify({'message': 'Note added'})



# ------------------------ #
# FILES
# ------------------------ #

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

# fetch(`/download/${fileName}`)
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# delete
@app.route('/delete/<filename>', methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.remove(file_path)
    return jsonify({'message': 'file deleted'})

# upload
@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files')  # Get all files from the form-data
    for file in files:
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    
    return jsonify({'message': 'Files uploaded successfully'})




# ------------------------ #
# MAIN 
# ------------------------ #
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


