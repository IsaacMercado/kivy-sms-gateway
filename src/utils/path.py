from kivy.utils import platform


def get_app_path():
    if platform == 'android':
        from android.storage import app_storage_path
        settings_path = app_storage_path()
    else:
        from plyer import storagepath
        settings_path = storagepath.get_application_dir()
    return settings_path
