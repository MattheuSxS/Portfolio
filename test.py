from datetime import datetime
from zoneinfo import ZoneInfo


test = datetime.now(ZoneInfo('Europe/Dublin')).isoformat()
test2 = datetime.now().isoformat()
print(test)
print(test2)