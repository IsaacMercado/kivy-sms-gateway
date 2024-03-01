from jnius import autoclass

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity


def get_package_name():
    return mActivity.getApplicationContext().getPackageName()


def get_service(name: str, package_name: str | None = None):
    package_name = package_name or get_package_name()
    return autoclass(f'{package_name}.Service{name}')


def start_service(name: str, argument: str = '', package_name: str | None = None):
    service = get_service(name, package_name)
    service.start(mActivity, argument)


def stop_service(name: str, package_name: str | None = None):
    service = get_service(name, package_name)
    service.stop(mActivity)
