class Vehicle(object):
    """Represents a vehicle"""

    def __init__(self,engine_power=100):
        self.engine_power = engine_power
    
    def __str__(self):
        return "Engine power : {}HP".format(self.engine_power)
    
    def print_name(self):
        print("From vehicle")
    
class Car(Vehicle):
    """Represents a car"""

    def __init__(self,wheels=4):
        super().__init__()
        self.wheels = wheels
    
    def __str__(self):
        return "Engine power : {}HP , Wheels = {}".format(self.engine_power,self.wheels)
    
    def print_name(self):
        print("From vehicle")

car = Car()
print(car)
car.print_name()
#output
Engine power : 100HP , Wheels = 4
From vehicle