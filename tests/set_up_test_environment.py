# SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bw2io


backup_file_path = "tests/MOCA_test_project.tar.gz"
bw2io.backup.restore_project_directory(backup_file_path, overwrite_existing=True)
