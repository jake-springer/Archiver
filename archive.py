import tarfile 
import os
from clint.textui import progress

class Archive:

    def __init__(self):
        self.archive_name = ""
        self.archive_path = ""
        self.target_paths = []
        self.verbose = True

    def tarball(self):
        archive = os.path.join(self.archive_path, self.archive_name)
        with tarfile.open(archive, "w:gz") as tarhandle:
            for path in self.target_paths:
                for root,dirs,files in os.walk(path):
                    if self.verbose:
                        for f in progress.bar(
                            files, 
                            expected_size=len(files)):
                            tarhandle.add(os.path.join(root, f))
                    else:
                        for f in files:
                            tarhandle.add(os.path.join(root, f))
        tarfile.close()