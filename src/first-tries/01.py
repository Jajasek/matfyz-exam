# my first app, testing the dock view and static widget


import textual.app
import textual.views
import textual.widgets


class MyApp(textual.app.App):
    async def on_mount(self):
        view = await self.push_view(textual.views.DockView())
        left = textual.widgets.Placeholder(name='My Second Placeholder',
                                           height=13)
        x = textual.widgets.Static('X')
        await view.dock(x, edge='right', size=2)
        await view.dock(left, edge='right')


if __name__ == '__main__':
    MyApp.run()
