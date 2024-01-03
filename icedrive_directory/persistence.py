import json
import uuid
import os

class DirectoryPersistence:            
    def __init__(self, filename):
        self.filename = filename
        self.directories = {}	

        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, "r") as dirs_fd:
                self.directories = json.load(dirs_fd)
        else:
            self.directories = {"root_directories": {}, "directories": {}}

    def save_to_json(self):
        with open(self.filename, "w") as dirs_fd:
            json.dump(self.directories, dirs_fd, indent=4)

    def get_directory_for_user(self, username):
        if username not in self.directories["root_directories"]:
            dir_uuid = str(uuid.uuid4())
            self.directories["root_directories"][username] = dir_uuid
            self.directories["directories"][dir_uuid] = {
                "files": {},
                "subdirs": {},
            }
            self.save_to_json()
        
        return self.directories["root_directories"][username]
    
    def get_subdirs_for_dir(self, parent_dir):
        if parent_dir not in self.directories["directories"]:
            raise Exception()
        dir_struct = self.directories["directories"][parent_dir]
        return dir_struct["subdirs"]
    
    def get_parent_for_dir(self, directory):
        for directory_id, dir_struct in self.directories["directories"].items():
            subdir_uuids = [subdir_id for subdir_id in dir_struct["subdirs"].values()]
            if directory in subdir_uuids:
                return directory_id
            
        return None
    
    def get_files_for_dir(self, directory_id):
        if directory_id not in self.directories["directories"]:
            raise Exception()
        dir_struct = self.directories["directories"][directory_id]
        return list(dir_struct["files"].keys())

    def create_subdir_for_dir(self, parent_dir, child_name):
        if parent_dir not in self.directories["directories"]:
            raise Exception("Parent directory does not exist")
    
        if child_name in self.directories["directories"][parent_dir]["subdirs"]:
            return None  

        child_uuid = str(uuid.uuid4())
        self.directories["directories"][parent_dir]["subdirs"][child_name] = child_uuid
        self.directories["directories"][child_uuid] = {
            "files": {},
            "subdirs": {},
        }
        self.save_to_json()
        return child_uuid

    def remove_subdir_for_dir(self, parent_dir, child_name):
        if parent_dir not in self.directories["directories"]:
            raise Exception("Parent directory does not exist")

        child_uuid = self.directories["directories"][parent_dir]["subdirs"].pop(child_name, None)
        if child_uuid:
            del self.directories["directories"][child_uuid]
            self.save_to_json()
            return True
        return False
    
    def link_file_to_dir(self, directory_id, filename, blob_id):
        if directory_id not in self.directories["directories"]:
            raise Exception("Directory does not exist")

        self.directories["directories"][directory_id]["files"][filename] = blob_id
        self.save_to_json()

    def unlink_file_from_dir(self, directory_id, filename):
        if directory_id not in self.directories["directories"]:
            raise Exception("Directory does not exist")

        if filename not in self.directories["directories"][directory_id]["files"]:
            return False  # Indica que el archivo no se encontró

        del self.directories["directories"][directory_id]["files"][filename]
        self.save_to_json()
        return True
    
    def get_blob_id_for_file(self, directory_id, filename):
        if directory_id not in self.directories["directories"]:
            return None  

        dir_struct = self.directories["directories"][directory_id]
        return dir_struct["files"].get(filename)  
    
    def get_path_for_dir(self, directory_id):
        if directory_id not in self.directories["directories"]:
            raise Exception("Directory does not exist")
    
        path = [directory_id]
        current_dir = directory_id
        while current_dir in self.directories["directories"]:
            parent_dir = self.get_parent_for_dir(current_dir)
            if parent_dir is None or parent_dir == current_dir:  # Caso para el directorio raíz
                break
            path.insert(0, parent_dir)
            current_dir = parent_dir
        return '/' + '/'.join(path)



