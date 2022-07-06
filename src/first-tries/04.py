# dock layout inside layout - the overlapping is broken!!


from textual.app import App
from textual.widgets import Placeholder
from textual.views import DockView


class MyApp(App):
    async def on_mount(self):
        subview0 = DockView()
        await subview0.dock(Placeholder(name='Subview0 (z=0) left'),
                            Placeholder(name='Subview0 (z=0) right'), edge='left')
        subview1 = DockView()
        await subview1.dock(Placeholder(name='Subview1 (z=1)'))

        # Try switching the following 2 lines. It should have no effect, but it
        # switches the order of placeholder inside subviews
        # (but not the free one)!
        await self.view.dock(subview0, Placeholder(name='Free (z=0)'), size=8, z=0)
        await self.view.dock(subview1, size=15, z=1, edge='bottom')


if __name__ == '__main__':
    MyApp.run()
