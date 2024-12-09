import subprocess
import zipfile

from polymath import utils
import hashlib
import time
import os


class PacksManager:
    def __init__(self, config):
        self.config = config
        self.folder = utils.get_path("storage/")
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        self.packs_folder = self.folder + "packs/"
        self.registry = utils.SavedDict(self.folder + "registry.json")
        if not os.path.exists(self.packs_folder):
            os.mkdir(self.packs_folder)

    def register(self, pack, spigot_id, ip):
        sha1 = hashlib.sha1()
        sha1.update(pack)
        id_hash = sha1.hexdigest()

        pack_path = os.path.join(self.packs_folder, id_hash)
        with open(pack_path, "wb") as pack_file:
            pack_file.write(pack)

        work_dir = os.path.join(self.packs_folder, 'work-'+id_hash)
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        # Decompress the pack file into the work directory
        with zipfile.ZipFile(pack_path, 'r') as zip_ref:
            zip_ref.extractall(work_dir)

        # Read the packsquash configuration file
        #print PWD
        print(os.getcwd())

        config_path = '/polymath/polymath/config/packsquash.toml'
        with open(config_path, 'r') as config_file:
            config_content = config_file.read()

        # Replace {packfile} with the actual pack path
        config_content = config_content.replace('{packfile}', work_dir)
        # Replace {output} with the actual output path
        config_content = config_content.replace('{output}', pack_path)

        # Execute packsquash command with the modified configuration as standard input
        process = subprocess.Popen(['packsquash'], stdin=subprocess.PIPE)
        process.communicate(input=config_content.encode())

        self.registry[id_hash] = {
            "id": spigot_id,
            "ip": ip,
            "last_download": int(time.time()),
        }

        return id_hash

    def fetch(self, id_hash):
        output = os.path.join(self.packs_folder, id_hash)
        if id_hash in self.registry and os.path.exists(output):
            self.registry[id_hash]["last_download"] = time.time()
            return output