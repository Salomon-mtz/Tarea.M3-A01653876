from matplotlib import pyplot as plt
from mesa import Agent
import random
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

class Road(Agent):
  def __init__(self, unique_id, model, x, y):
    super().__init__(unique_id, model)
    self.dir = []

class Wall(Agent):
  def __init__(self, x, y):
    super().__init__(x, y)

# LUCES DE TRAFICO
class TrafficLight(Agent):
  def __init__(self, u_id, model, pos, color=True):
    super().__init__(u_id, model)
    self.pos = pos
    self.color = color
    self.lights = []
    self.current_cycle = 1
    self.counter = 0
    self.velocity = 0
    self.pasos = 0
    self.cambio = 0
    self.listaCambiosx = []
    self.listaCambiosy = []
  
    

  def check(self):
    if self.lights[0].current_cycle == 0:
      self.current_cycle = 1
    else:
      self.current_cycle = 0

    direccion = self.model.grid.get_cell_list_contents((self.pos[0], self.pos[1]), True)[0].dir

    if 'D' in direccion:
      self.x = 0
      self.y = 1
    elif 'R' in direccion:
      self.x = -1
      self.y = 0
    elif 'U' in direccion:
      self.x = 0
      self.y = -1
    elif 'L' in direccion:
      self.x = 1
      self.y = 0
             
    vehicle_cell = self.model.grid.get_cell_list_contents((self.pos[0] + self.x, self.pos[1] + self.y), True)

    if self.counter == 1:
      self.current_cycle = 0
      self.counter = 0
      self.lights[0].current_cycle = 1

    for vehicle in vehicle_cell:
      if type(vehicle) == Vehicles:
        if self.current_cycle == 1:
          vehicle.canMove = True
          self.velocity = vehicle.velocity
        else:
          vehicle.canMove = False

        self.listaCambiosx.append(self.pasos)
        self.listaCambiosy.append(self.cambio)
        self.counter = 0
        self.cambio = 0
        
        
        

      else:
        self.counter += 1
        self.pasos += 1
        self.cambio += 1
        
        
class Vehicles(Agent):
  def __init__(self, u_id, model, pos, velocity):
    super().__init__(u_id, model)
    self.original_pos = pos
    self.pos = self.original_pos
    self.x = self.pos[0]
    self.y = self.pos[1]
    self.canMove = True
    self.velocity = velocity

  def step(self):
    self.move()

  def move(self):

    cell = self.model.grid.get_cell_list_contents((self.x, self.y), True)[0].dir

    if len(cell) > 1 and self.canMove:

      pick = cell[random.randint(0, len(cell)-1)]
      
      if pick == 'R':
        self.x += 1

      elif pick == 'D':
        self.y -= 1

      elif pick == 'L':
        self.x -= 1

      elif pick == 'U':
        self.y += 1
      
      self.model.grid.move_agent(self, (self.x, self.y))

    else:
      self.checkFront()
    
  def checkFront(self):
    cell = self.model.grid.get_cell_list_contents((self.x, self.y), True)[0].dir

    if 'R' in cell and self.canMove:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, Vehicles) for x in self.model.grid.get_cell_list_contents((self.x + 1, self.y), True))):
        self.x += 1

    elif 'D' in cell and self.canMove:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, Vehicles) for x in self.model.grid.get_cell_list_contents((self.x, self.y - 1), True))):
        self.y -= 1

    elif 'L' in cell and self.canMove:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, Vehicles) for x in self.model.grid.get_cell_list_contents((self.x - 1, self.y), True))):
        self.x -= 1

    elif 'U' in cell and self.canMove:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, Vehicles) for x in self.model.grid.get_cell_list_contents((self.x, self.y + 1), True))):
        self.y += 1
    
    self.model.grid.move_agent(self, (self.x, self.y))


class TrafficModel(Model):
  modelo = [
    ((0, 10), (21, 10)),
    ((20, 11), (-1, 11)),

    ((10, 20), (10, -1)),
    ((11, 0), (11, 21)),
  ]

  def __init__(self, max_agents=10, road_list=modelo, width=10, height=10):
    self.grid = MultiGrid(width, height, True)
    self.schedule = RandomActivation(self)

    self.max_agents = max_agents
    self.n_agents = 0

    self.vehicles = []
    self.lights = []

    for x in range(width):
      for y in range(height):
        wall = Wall(x, y)
        self.grid.place_agent(wall, (x, y))

    for road in road_list:
      start, end = road
      calcX = end[0] - start[0]
      calcY = end[1] - start[1]
      goes = ''
      cond = None

      if not calcX == 0:
        if calcX > 0:
          goes = 'R'
          cond = 0
        else:
          goes = 'L'
          cond = 1
      elif not calcY == 0:
        if calcY > 0:
          goes = 'U'
          cond = 0
        else:
          goes = 'D'
          cond = 1

      x = start[0]
      y = start[1]
      while x != end[0]:
        cell = self.grid.get_cell_list_contents((x, y), True)

        if any(isinstance(elem, Wall) for elem in cell):
          self.grid.remove_agent(cell[0])

        if any(isinstance(elem, Road) for elem in cell):
          cell[0].dir.append(goes)
        else:
          r = Road(0, self, x, y)
          r.dir.append(goes)
          self.grid.place_agent(r, (x, y))

        if cond == 0:
          x += 1
        else:
          x -= 1

      while y != end[1]:
        cell = self.grid.get_cell_list_contents((x, y), True)

        if any(isinstance(elem, Wall) for elem in cell):
          self.grid.remove_agent(cell[0])

        if any(isinstance(elem, Road) for elem in cell):
          cell[0].dir.append(goes)
        else:
          r = Road(1, self, x, y)
          r.dir.append(goes)
          self.grid.place_agent(r, (x, y))

        if cond == 0:
          y += 1
        else:
          y -= 1
    
    self.grid.get_cell_list_contents((10, 0), True)[0].dir[0] = 'R'
    self.grid.get_cell_list_contents((19, 10), True)[0].dir[0] = 'U'
    self.grid.get_cell_list_contents((0, 11), True)[0].dir[0] = 'D'
    self.grid.get_cell_list_contents((11, 20), True)[0].dir[0] = 'L'

    self.traff = (9, 10)
    self.traffic_light = TrafficLight(0, self, self.traff, False)
    self.grid.place_agent(self.traffic_light, self.traff)

    self.traff2 = (10, 12)
    self.traffic_light2 = TrafficLight(1, self, self.traff2, False)
    self.grid.place_agent(self.traffic_light2, self.traff2)

    self.traffic_light.lights.append(self.traffic_light2)
    self.traffic_light2.lights.append(self.traffic_light)

    self.lights.append(self.traffic_light)
    self.lights.append(self.traffic_light2)

    pos = [(1,10), (3,10), (10,18)]
    vel = [(90), (100), (80)]
    for i in range(3):
      self.vehicle_pos = pos[i]
      self.vehicle_vel = vel[i]
      self.vehicle = Vehicles(i, self, self.vehicle_pos, self.vehicle_vel)
      self.grid.place_agent(self.vehicle, self.vehicle_pos)
      self.vehicles.append(self.vehicle)
      print(self.vehicle.velocity)
      
    self.running = True
  
  def step(self):
    ps = []
    for vehicle in self.vehicles:
      vehicle.move()

      xy = vehicle.pos
      p = [xy[0],xy[1],0]
      ps.append(p)

    for light in self.lights:
      light.check()
      
      
    if self.lights[0].velocity < self.lights[1].velocity:
      print("Coche más rápido por semáforo 2")
      self.lights[0].current_cycle = 0
    elif self.lights[0].velocity > self.lights[1].velocity:
      print("Coche más rápido por semáforo 1")
      self.lights[1].current_cycle = 0
    self.lights[0].velocity = 0
    self.lights[1].velocity = 0
      

    self.schedule.step()
    fig, ax = plt.subplots()
    #Colocamos una etiqueta en el eje Y
    ax.set_ylabel('Llegadas a semáforos')
    ax.set_xlabel('Pasos totales')
    #Colocamos una etiqueta en el eje X
    ax.set_title('Pasos por llegada')
    #Creamos la grafica de barras utilizando 'paises' como eje X y 'ventas' como eje y.
    plt.bar(self.traffic_light.listaCambiosx, self.traffic_light.listaCambiosy)
    plt.savefig('barras_simple.png')
    #Finalmente mostramos la grafica con el metodo show()
    plt.show()
    
    
    return ps
          


def agent_portrayal(agent):

  portrayal = {}

  if type(agent) is Wall:
    portrayal = {
      "Shape": "rect",
      "Color": 'blue',
      "Filled": "true",
      "Layer": 0,
      "w": 1,
      "h": 1,
    }

  if type(agent) is TrafficLight:
    if agent.color == True:
      w, h = .25, .5
      color = 'green'
    else:
      w, h = .5, .25
      color = 'red'

    if agent.current_cycle == 1:
      color = 'green'
    else:
      color = 'red'

    portrayal = {
      "Shape": "rect",
      "Color": color,
      "Filled": "true",
      "Layer": 3,
      "w": w,
      "h": h,
    }

  if type(agent) is Road:
    portrayal = {
      "Shape": "rect",
      "Color": 'white',
      "Filled": "true",
      "Layer": 1,
      "w": 1,
      "h": 1,
    }

  if type(agent) is Vehicles:
    portrayal = {
      "Shape": "circle",
      "Color": 'black',
      "Filled": "true",
      "Layer": 2,
      "r": 0.5
    }

  return portrayal


rows, cols = 20, 20
rows += 1
cols += 1
grid = CanvasGrid(agent_portrayal, rows, cols, 500, 500)

server = ModularServer(TrafficModel, [grid], "Traffic light model", 
  {
    'width': rows, 
    'height': cols
  }
)

server.port = 8080 
server.launch()

