import bw2io


backup_file_path = "tests/MOCA_test_project.tar.gz"
bw2io.backup.restore_project_directory(backup_file_path, overwrite_existing=True)
    