'''
class Environment:
  def __init__(self, roomA= 'Dirty', roomB= 'Dirty', start= 'A'):
    self.room = {
        'A': roomA,
        'B': roomB
    }
    self.agent_loc = start
    
  def percept(self):
    return (self.agent_loc, self.room[self.agent_loc])

  def apply(self, action):
    if action == 'clean':
      if self.agent_loc == 'A':
        self.agent_loc = 'B'
      else:
        self.agent_loc = 'A'
  

class Agent:
    def __init__(self):
       pass
    def act(self, percept):
        location, status = percept
        if status == 'Dirty':
            return 'clean'
        else:
            return 'move'


            
env = Environment('Dirty', 'Dirty', 'A')
agent = Agent()
for _ in range(4):
    percept = env.percept()
    action = agent.act(percept)
    print(f"Percept: {percept} → Action: {action}")
    env.apply(action)
    '''
class SimplyTikTokAgent:
    def __init__(self):
        self.user_mood = "neutral"
        self.recent = []
        self.scroll_speed = 0.5
        self.user_likes ={
            "dance": 0.30,
            "programming": 0.80,
            "cats": 0.60,
            "study_tips": 0.70,
            "comedy": 1.00
        }

    def detect_mood(self, behavior):
        if behavior.get("studying"):
            return "studying"
        if behavior.get("stressed"):
            return "stressed"
        if behavior.get("likes_per_minute") > 4:
            return "happy"
        if behavior.get("scroll_speed") > 5:
            return "bored"
        return "neutral"
    def learn_from_watch(self, category, watch_time, liked=False):
        score = self.user_likes[category]
        if watch_time > 0.7 or liked:
            score += 0.10
        elif watch_time < 0.2 and liked:
            score -= 0.10
        if score > 1.0:
            score = 1.0
        if score < 0.0:
            score = 0.0
        self.user_likes[category] = score
    def pick_video(self, behavior):
        self.user_mood = self.detect_mood(behavior)
        choice = "bored"
        if self.user_mood == "bored":
            choice = "dance"
        elif self.user_mood == "studying":
            choice = "study_tips"
        elif self.user_mood == "stressed":
            choice = "cats"
        self.recent.append(choice)
        if len(self.recent) > 3:
            self.recent.pop(0)
        return choice

agent = SimplyTikTokAgent()


behavior = {
    "studying": False,
    "stressed": False,
    "likes_per_minute": 3,
    "scroll_speed": 2
}

chosen = agent.pick_video(behavior)

watch_time = 0.8
liked = True

agent.learn_from_watch(chosen, watch_time, liked)

print(f"Mood:          {agent.user_mood}")
print(f"Video chosen:  {chosen}")
print(f"Watched:       {watch_time}")
print(f"Liked:         {liked}")
print(f"Recent videos: {agent.recent}")

    