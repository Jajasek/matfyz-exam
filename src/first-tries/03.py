# test: it is not good idea to push multiple views
# (I do not know how to get rid of them later)


import textual.app
import textual.views
import textual.widgets


class MyApp(textual.app.App):
    async def on_mount(self):
        view1 = await self.push_view(textual.views.DockView())
        await view1.dock(textual.widgets.Button("1", "1"))
        view2 = await self.push_view(textual.views.DockView())
        self.button2 = textual.widgets.Button("2", "2")
        await view2.dock(self.button2)

    def handle_button_pressed(self, message: textual.widgets.ButtonPressed):
        assert isinstance(message.sender, textual.widgets.Button)
        if message.sender.name == "2":
            self.button2.visible = False


if __name__ == '__main__':
    MyApp.run()
