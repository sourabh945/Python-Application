from random import randint
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.widget import Widget

Builder.load_file('ui.kv')

Config.set('graphics','resizeable','0')
Config.set('graphics','width','250')
Config.set('graphics','height','250')

def outcome():
    return "Tail" if randint(0,1) == 0 else "Head"

class MyLayout(Widget):
    def __init__(self, **kwargs):
        super(MyLayout,self).__init__(**kwargs)
    def flip(self):
        out = outcome()
        
        if out == 'Head':
            self.ids.imag.source = "head.png"
            self.ids.outcome.text = 'Head'
            self.ids.refresh.text = 'Toss again'
        else:
            self.ids.imag.source = "tail.png"
            self.ids.outcome.text = 'Tail'
            self.ids.refresh.text = 'Toss again'
        return MyLayout
    
class Toss(App):
    def build(self):
        return MyLayout()
if __name__ == "__main__":
    Toss().run()