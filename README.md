pyweasyl
========

Python binding to implement the 
[Weasyl HTTP API](https://projects.weasyl.com/weasylapi/), version 1.2.

Example
=======

```python
from weasyl import Weasyl
api = Weasyl("API_Key_here")
notifications = api.message_summary()

print("You have {0} submissions".format(notifications['submissions']))
```
