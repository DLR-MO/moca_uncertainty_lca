from PyQt5.QtCore import QSettings

class Settings:
    def __init__(self, ini_file="config.ini"):
        self.qsettings = QSettings(ini_file, QSettings.IniFormat)

    def get(self, key, default=""):
        return self.qsettings.value(key, default)

    def set(self, key, value):
        self.qsettings.setValue(key, value)
        self.qsettings.sync()
