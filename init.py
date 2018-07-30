from kivy.app import App
#kivy.require("1.8.0")
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.window import Window
import json, re, qrcode, os
from kivy import utils
Window.clearcolor = (1, 1, 1, 1)

RollNo = ''
MenuCardData = ''
order=[[],[],[],[]]

def UpdateMenu():
    global MenuCardData
    MenuCardData = json.load(open("MenuCard.json", 'r'))
    DishStr = ''
    for category in MenuCardData:
        for item in MenuCardData[category]:
            TDishStr = """\t\t\tButton:\n\t\t\t\ttext: \"""" + item['name'] + "\" \n"
            TDishStr += """\t\t\t\tbackground_color: utils.get_color_from_hex('#2F6CE5')
				color: utils.get_color_from_hex('#FFFFFF')
				on_press: root.AddToBill(self.text)\n"""
            DishStr += TDishStr
    designTemp = re.sub('\'\'\'<Insert Items Here>\'\'\'', DishStr ,open("DesignTemplate.kv", 'r').read())
    open("DesignTemp.kv", 'w').close()
    open("DesignTemp.kv", 'w').write(designTemp)

class LoginScreen(Screen):
    username = ObjectProperty()
    status = ObjectProperty()
    def ValidateUserName(self):
        if self.username.text == "123":
            global RollNo
            RollNo = self.username.text
            self.parent.current = "bill" 
            self.status.text = ""
            self.username.text = ""
        else:
            self.status.text = "Invalid Roll Number. Please try again."
    pass

class BillScreen(Screen):
    userrollno = ObjectProperty()
    bill = ObjectProperty()
    def on_enter(self):
        global RollNo
        self.userrollno.text = 'Welcome ' + RollNo
    
    def RefreshListOfItems(self):
        self.bill.clear_widgets()
        HeadingLabel = Label(text="Your Order", color=utils.get_color_from_hex('#2F6CE5'))
        self.bill.add_widget(HeadingLabel)
        title = BoxLayout(orientation='horizontal')
        Item = Label(text="Item", color=utils.get_color_from_hex('#2F6CE5'))
        Price = Label(text="Price", color=utils.get_color_from_hex('#2F6CE5'))
        Qty = Label(text="Quantity", color=utils.get_color_from_hex('#2F6CE5'))
        Total = Label(text="Total", color=utils.get_color_from_hex('#2F6CE5'))
        title.add_widget(Item)
        title.add_widget(Price)
        title.add_widget(Qty)
        title.add_widget(Total)
        self.bill.add_widget(title)
        for i in range(len(order[0])):
            title = BoxLayout(orientation='horizontal')
            Item = Button(text=str(order[0][i]), color=utils.get_color_from_hex('#FFFFFF'))
            Item.background_color = utils.get_color_from_hex('#2F6CE5')
            Item.bind(on_press=self.RemoveFromBill)
            Price = Label(text=str(order[1][i]), color=utils.get_color_from_hex('#2F6CE5'))
            Qty = Label(text=str(order[2][i]), color=utils.get_color_from_hex('#2F6CE5'))
            Total = Label(text=str(order[3][i]), color=utils.get_color_from_hex('#2F6CE5'))
            title.add_widget(Item)
            title.add_widget(Price)
            title.add_widget(Qty)
            title.add_widget(Total)
            self.bill.add_widget(title)
        Total = Label(text="Total    Rs." + str(1.1*sum(order[3]))+ "/-    (+10% Tax added)", color=utils.get_color_from_hex('#2F6CE5'))
        self.bill.add_widget(Total)
        return

    def AddToBill(self, dish):
        for category in MenuCardData:
            for item in MenuCardData[category]:
                if dish == item['name']:
                    price = item['price']
                    break
        if dish not in order[0]:
            order[0].append(dish)
            order[1].append(price)
            order[2].append(1)
            order[3].append(price)
        else:
            index = order[0].index(dish)
            order[2][index] += 1
            order[3][index] = order[2][index] * order[1][index]     
    
        self.RefreshListOfItems()
        return
    
    def RemoveFromBill(self, button):
        dish = button.text
        index = order[0].index(dish)
        if order[2][index] > 1:
            order[2][index] -= 1
            order[3][index] = order[2][index] * order[1][index]   
        else:
            order[0].pop(index)
            order[1].pop(index)
            order[2].pop(index)
            order[3].pop(index)
        self.RefreshListOfItems()
    
    def ClearAll(self):
        global RollNo
        global order
        RollNo = ''
        order=[[],[],[],[]]
        self.parent.current = "main" 
        self.RefreshListOfItems()
        return
    
    def PrintBill(self):
        global order
        orders = open("orders.csv",'r').read().splitlines()
        OrderNo = int(orders[-1].split(',')[0]) + 1
        ptr = open("orders.csv",'a')
        ptr.write('\n'+str(OrderNo)+ ',')
        for i in range(len(order[0])):
            ptr.write(
                str(order[0][i]) +';'+str(order[1][i]) +';'+str(order[2][i]) +';'+ str(order[3][i]) +','
            )
        ptr.write(str(1.1*sum(order[3])))
        qr = qrcode.QRCode(version = 1, error_correction = qrcode.constants.ERROR_CORRECT_H, box_size = 10, border = 4)
        qr.add_data(OrderNo)
        qr.make(fit=True)
        img = qr.make_image()
        print os.getcwd()
        img.save(os.getcwd()+"/bills/"+str(OrderNo) +".jpg")
        self.ClearAll()
        return

    pass

class ScreenManagement(ScreenManager):
    pass

class BillApp(App): 
    def build(self):
        return presentation

if __name__ == "__main__":
    UpdateMenu()
    presentation = Builder.load_file("DesignTemp.kv")
    BillApp().run()