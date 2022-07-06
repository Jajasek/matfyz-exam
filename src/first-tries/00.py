# This is an example app copied from the textual source code


from textual.app import App
from textual import events
from textual.views import DockView
from textual.widget import Reactive


from textual.widgets import Header
from textual.widgets import Footer
from textual.widgets import Placeholder


class MyApp(App):
    """Just a test app."""

    async def on_load(self, event: events.Load) -> None:
        await self.bind("ctrl+c", "quit", show=False)
        await self.bind("q", "quit", "Quit")
        await self.bind("x", "bang", "Test error handling")
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")

    show_bar: Reactive[bool] = Reactive(False)

    async def watch_show_bar(self, show_bar: bool) -> None:
        self.animator.animate(self.bar, "layout_offset_x",
                              0 if show_bar else -40)

    async def action_toggle_sidebar(self) -> None:
        self.show_bar = not self.show_bar

    async def on_mount(self, event: events.Mount) -> None:
        view = await self.push_view(DockView())

        header = Header()
        footer = Footer()
        self.bar = Placeholder(name="left")

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(self.bar, edge="left", size=40, z=1)
        self.bar.layout_offset_x = -40

        sub_view = DockView()
        await sub_view.dock(Placeholder(), Placeholder(), edge="top")
        await view.dock(sub_view, edge="left")


if __name__ == '__main__':
    MyApp.run(log="textual.log")
