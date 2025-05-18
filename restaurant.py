import json
import textwrap
import ast

from config.paths import PATHS

class Restaurant:

    def __init__(self,restaurant_id):

        self.read_restaurant_details(restaurant_id)
        self.read_menu(restaurant_id)

    def get_menu_line(self,name,price,width=80):

        price_str = f"${price:,.2f}"              
        gap = width - len(price_str)          
        return f"{name:.<{gap}}{price_str}\n"

    def get_dish(self,dish):

        try:

            dish_info = ""

            name = dish["title"]
            recipe = dish["description"]
            price = dish["price"]

            dish_info += self.get_menu_line(name,price)
            dish_info += textwrap.fill(recipe, width=60, break_long_words=False, replace_whitespace=False)+"\n\n"
        
        except Exception as e:
            print(f"Something went wrong while processing the dish {dish}\n\n")
            print(e)

        return dish_info

    def read_menu(self,restaurant_id):

        try:

            with open(PATHS.menu/f"{restaurant_id}.json","r",encoding="utf-8") as f:
                menu_dict = json.load(f)

            self.menu_details=""
            for key,menu_list in menu_dict.items():

                self.menu_details += "\n" + key + "\n"
                self.menu_details += "-"*80 +"\n\n"

                for item in menu_list:

                    self.menu_details += self.get_dish(item)

        except Exception as e:

            print(f"Error while reading menu details:\n\n {e}")
            raise

    def read_restaurant_details(self,restaurant_id):

        try:

            with open(PATHS.info/f"{restaurant_id}.json","r",encoding="utf-8") as f:
                info = json.load(f)

            self.name = info.get("name",None)
            self.address = info.get("address","")+","+info.get("city","")+","+info.get("state","")+","+info.get("postal_code","")
            self.overall_rating = info.get("stars",None)
            attributes = info["attributes"]
            self.delivery = attributes.get("RestaurantsDelivery",None)
            self.outdoor_seating = attributes.get("OutdoorSeating",None)
            self.cards_accepted = attributes.get("BusinessAcceptsCreditCards",None)
            self.goodforkids = attributes.get("GoodForKids",None)
            self.caters = attributes.get("Caters",None)
            self.attire = attributes.get("RestaurantsAttire",None)
            self.takeout = attributes.get("RestaurantsTakeOut",None)

            ambience_dict = ast.literal_eval(attributes.get("Ambience","{}"))
            self.ambience =",".join([key for key, value in ambience_dict.items() if value])
        
            self.wheelchair_access = attributes.get("WheelchairAccessible",None)

            self.hours_dict = info.get("hours",{})

            self.hours = ""

            for key,value in self.hours_dict.items():

                self.hours += key+": "
                if(value=="0:0-0:0"):
                    self.hours += "Closed\n"
                else:
                    self.hours += value+"\n"

        except Exception as e:

            print(f"Error while reading restaurant info:\n\n {e}")
            raise

    def __str__(self):

        try:

            info=""

            if(self.name):
                info += "Name: " + self.name + "\n\n"

            if(self.address):
                info += "Address: " + self.address + "\n\n"

            if(self.overall_rating):
                info += "Overall Rating: "+ str(self.overall_rating) + "\n\n"

            if(self.delivery):
                info += "Do they deliver? " + self.delivery + "\n\n"

            if(self.outdoor_seating):
                info += "Do they have outdoor seating? " + self.outdoor_seating + "\n\n"

            if(self.cards_accepted):
                info += "Do they accept Debit/Credit cards? " + self.cards_accepted + "\n\n"

            if(self.goodforkids):
                info += "Is this restuarant suitable for kids? "+self.goodforkids+"\n\n"

            if(self.caters):
                info += "Does this restaurant caters for events? " + self.caters + "\n\n"

            if(self.attire):
                info += "What kind of attire is usually wore here? " + ast.literal_eval(self.attire) + "\n\n"

            if(self.takeout):
                info += "Does this restaurant allows takeouts? " + self.takeout + "\n\n"

            if(self.ambience):
                info += "Ambience of this place:\n" + self.ambience

            if(self.wheelchair_access):
                info += "Does this place has wheelchair access? "+self.wheelchair_access + "\n\n"

            if(self.hours):
                info += "Hours:\n"+self.hours     

            info += "Menu: \n"
            info += "-"*80 +"\n\n"
            info += self.menu_details

        except Exception as e:

            print(f"Error while generating restaurant info:\n\n {e}")
            raise

        return info




            




