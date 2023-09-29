def export(self):
    return jsonify(self.db.export_to_json())

def export_discussion(self):
    return jsonify({"discussion_text":self.get_discussion_to()})

def clear_uploads(self):
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
    ASCIIColors.info(" ║               Removing all uploads               ║")
    ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")        
    try:
        folder_path = self.lollms_paths.personal_uploads_path
        # Iterate over all files and directories in the folder
        for entry in folder_path.iterdir():
            if entry.is_file():
                # Remove file
                entry.unlink()
            elif entry.is_dir():
                # Remove directory (recursively)
                shutil.rmtree(entry)
        print(f"All files and directories inside '{folder_path}' have been removed successfully.")
        return {"status": True}
    except OSError as e:
        ASCIIColors.error(f"Couldn't clear the upload folder.\nMaybe some files are opened somewhere else.\Try doing it manually")
        return {"status": False, 'error': "Couldn't clear the upload folder.\nMaybe some files are opened somewhere else.\Try doing it manually"}

def selectdb(self):
    from tkinter import Tk, filedialog
    # Initialize Tkinter
    root = Tk()
    root.withdraw()

    # Show file selection dialog
    file_path = filedialog.askopenfilename()