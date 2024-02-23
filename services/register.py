from jnius import autoclass

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
PACKAGE_NAME = "myapp"
PACKAGE_DOMAIN = "org.test"


def start_service(name: str, argument: str = ''):
    service = autoclass(f'{PACKAGE_DOMAIN}.{PACKAGE_NAME}.Service{name}')
    service.start(mActivity, argument)


def stop_service(name: str):
    service = autoclass(f'{PACKAGE_DOMAIN}.{PACKAGE_NAME}.Service{name}')
    service.stop(mActivity)
