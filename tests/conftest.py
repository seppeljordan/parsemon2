import os

from pytest import fixture


class FileGenerator:
    def __init__(self, tmp_path_factory):
        self.tmp_path_factory = tmp_path_factory

    def create_file(self, content: str):
        path = self.tmp_path_factory.mktemp("content-file")
        os.rmdir(path)
        with open(path, "w") as generated_file:
            generated_file.write(content)
        return path


@fixture
def file_generator(tmp_path_factory):
    return FileGenerator(tmp_path_factory)
