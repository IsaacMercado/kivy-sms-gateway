from functools import cached_property
from typing import Any


from jnius import autoclass, PythonJavaClass, java_method


def get_shared_preferences(name: str | None = None):
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    Context = autoclass('android.content.Context')

    if name is not None:
        context = mActivity.getApplicationContext()
        return context.getSharedPreferences(name, Context.MODE_PRIVATE)

    return mActivity.getPreferences(Context.MODE_PRIVATE)


class Editor(object):
    def __init__(self, editor):
        self.editor = editor

    def put_boolean(self, key: str, value: bool):
        self.editor.putBoolean(key, value)
        return self

    def put_float(self, key: str, value: float):
        self.editor.putFloat(key, value)
        return self

    def put_int(self, key: str, value: int):
        self.editor.putInt(key, value)
        return self

    def put_long(self, key: str, value: int):
        self.editor.putLong(key, value)
        return self

    def put_string(self, key: str, value: str):
        self.editor.putString(key, value)
        return self

    def put_string_set(self, key: str, value: set[str]):
        self.editor.putStringSet(key, value)
        return self

    def put(self, key: str, value: Any):
        if isinstance(value, bool):
            self.put_boolean(key, value)
        elif isinstance(value, float):
            self.put_float(key, value)
        elif isinstance(value, int):
            self.put_int(key, value)
        elif isinstance(value, str):
            self.put_string(key, value)
        elif isinstance(value, set) and all(isinstance(x, str) for x in value):
            self.put_string_set(key, value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        return self

    def remove(self, key: str):
        self.editor.remove(key)
        return self

    def clear(self):
        self.editor.clear()
        return self

    def apply(self):
        self.editor.apply()

    def commit(self) -> bool:
        return self.editor.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.apply()


class SharedPreferences(object):
    class OnSharedPreferenceChangeListener(PythonJavaClass):
        __javainterfaces__ = [
            'android/content/SharedPreferences'
            '$OnSharedPreferenceChangeListener'
        ]

        def __init__(self, callback, *args, **kwargs):
            self.callback = callback
            PythonJavaClass.__init__(self, *args, **kwargs)

        @java_method('(Landroid/content/SharedPreferences;Ljava/lang/String;)V')
        def onSharedPreferenceChanged(self, sharedPreferences, key):
            self.callback(SharedPreferences(sharedPreferences), key)

    def __init__(self, shared_preferences=None):
        self.shared_preferences = shared_preferences or get_shared_preferences()

    def set(self, key: str, value: Any):
        with self.edit as editor:
            editor.put(key, value)

    def __contains__(self, key) -> bool:
        return self.shared_preferences.contains(key)

    @cached_property
    def edit(self):
        return Editor(self.shared_preferences.edit())

    def get_all(self) -> dict[str, Any]:
        return self.shared_preferences.getAll()

    def get_boolean(self, key, default_value=False) -> bool:
        return self.shared_preferences.getBoolean(key, default_value)

    def get_float(self, key, default_value=0.0) -> float:
        return self.shared_preferences.getFloat(key, default_value)

    def get_int(self, key, default_value=0) -> int:
        return self.shared_preferences.getInt(key, default_value)

    def get_long(self, key, default_value=0) -> int:
        return self.shared_preferences.getLong(key, default_value)

    def get_string(self, key, default_value=None) -> str:
        return self.shared_preferences.getString(key, default_value)

    def get_string_set(self, key, default_value=None) -> set[str]:
        return self.shared_preferences.getStringSet(key, default_value)

    def register_on_shared_preference_change_listener(self, callback):
        listener = SharedPreferences.OnSharedPreferenceChangeListener(callback)
        self.shared_preferences.registerOnSharedPreferenceChangeListener(
            listener
        )
        return listener

    def unregister_on_shared_preference_change_listener(self, listener):
        self.shared_preferences.unregisterOnSharedPreferenceChangeListener(
            listener
        )

    def set_all(self, values: dict[str, Any]):
        with self.edit as editor:
            for key, value in values.items():
                editor.put(key, value)

    def set_boolean(self, key: str, value: bool):
        with self.edit as editor:
            editor.put_boolean(key, value)

    def set_float(self, key: str, value: float):
        with self.edit as editor:
            editor.put_float(key, value)

    def set_int(self, key: str, value: int):
        with self.edit as editor:
            editor.put_int(key, value)

    def set_long(self, key: str, value: int):
        with self.edit as editor:
            editor.put_long(key, value)

    def set_string(self, key: str, value: str):
        with self.edit as editor:
            editor.put_string(key, value)

    def set_string_set(self, key: str, value: set[str]):
        with self.edit as editor:
            editor.put_string_set(key, value)

    def remove(self, key: str):
        with self.edit as editor:
            editor.remove(key)

    def clear(self):
        with self.edit as editor:
            editor.clear()
