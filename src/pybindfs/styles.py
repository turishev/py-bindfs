from gi.repository import Gtk, Gdk


css = """
.red-button {
    # background-color: blue;
    color: red;
}
.blue-button {
    # background-color: blue;
    color: blue;
}
"""

def create_css_provider():
    provider = Gtk.CssProvider()
    provider.load_from_data(css.encode()) # В GTK 4 принимает bytes

    # Добавляем провайдер для всего приложения (Display)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
