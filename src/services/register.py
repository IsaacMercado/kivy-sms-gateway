from jnius import autoclass

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
Context = autoclass('android.content.Context')
Integer = autoclass('java.lang.Integer')


def get_package_name():
    return mActivity.getApplicationContext().getPackageName()


def get_service_name(name: str, package_name: str | None = None):
    package_name = package_name or get_package_name()
    return f'{package_name}.Service{name}'


def get_service(name: str, package_name: str | None = None):
    return autoclass(get_service_name(name, package_name))


def start_service(name: str, argument: str = '', package_name: str | None = None):
    service = get_service(name, package_name)
    service.start(mActivity, argument)


def stop_service(name: str, package_name: str | None = None):
    service = get_service(name, package_name)
    service.stop(mActivity)


def is_service_running(name: str, package_name: str | None = None):
    service_name = get_service_name(name, package_name)
    manager = mActivity.getSystemService(Context.ACTIVITY_SERVICE)
    services = manager.getRunningServices(Integer.MAX_VALUE)

    for info in services:
        if info.service.getClassName() == service_name:
            return True

    return False
