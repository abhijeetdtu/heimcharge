import wikipedia
from BusinessLogic.ExceptionHandling import *

def GetSummary(topic):
    try:
        topic = topic.lower().replace("location wise" , "")
        topic = topic.lower().replace("state wise" , "")
        return wikipedia.summary(topic)
    except Exception as e:
        HandleException(e)

    return ""
