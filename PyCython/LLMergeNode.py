class LinkedList:
    def __init__(self, value):
        self.value = value
        self.next = None
def mergeLinkedLists(headOne, headTwo):
    dummyNode = LinkedList(0)
    currentNode = dummyNode

    while headOne is not None and headTwo is not None:
        if headOne.value < headTwo.value:
            currentNode.next = headOne
            headOne = headOne.next
        else:
            currentNode.next = headTwo
            headTwo = headTwo.next
        currentNode = currentNode.next

    if headOne is not None:
        currentNode.next = headOne
    elif headTwo is not None:
        currentNode.next = headTwo

    return dummyNode.next
