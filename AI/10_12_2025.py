class RescueRobot:
 def __init__(self,zones,start_zone="Base"):
  self.zones=zones
  self.zone_names=list(zones.keys())
  self.current_zone=start_zone
  self.survivors_rescued=0
  self.total_survivors=sum(1 for s in zones.values() if s=="Survivor")
  self.i=self.zone_names.index(start_zone)

 def perceive_environment(self):
  status=self.zones[self.current_zone]
  print(f"At {self.current_zone}: {status}")
  return status
 
 def rescue(self):
  print(f"Rescuing survivor at {self.current_zone}")
  self.zones[self.current_zone]="Safe"
  self.survivors_rescued+=1
  self.move_to_next_zone()

 def find_new_path(self):
  print(f"{self.current_zone} blocked, skipping")
  self.move_to_next_zone()

 def move_to_next_zone(self):
  self.i=(self.i+1)%len(self.zone_names)
  self.current_zone=self.zone_names[self.i]
  print(f"Moving to {self.current_zone}")

 def all_rescued(self):
  return self.survivors_rescued==self.total_survivors
 
 def run(self):
  while not self.all_rescued():
   status=self.perceive_environment()
   if status=="Survivor":self.rescue()
   elif status=="Blocked":self.find_new_path()
   else:self.move_to_next_zone()
  print("All survivors rescued")
  
zones={"Base":"Safe","Zone A":"Survivor","Zone B":"Blocked","Zone C":"Survivor","Zone D":"Safe"}
robot=RescueRobot(zones)
robot.run()
