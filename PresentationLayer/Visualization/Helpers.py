
def GetPathPrefix(request , requestRoot):
    return request.path[:request.path.find(requestRoot)]
