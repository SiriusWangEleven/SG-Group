class FriendsManagement:
    def __init__(self):
        self.friends_dict = dict()
        self.subscribe = dict()
        self.block = dict()

    def buildConnection(self, friendsConnection):
        buildResult = dict()
        buildResult['success'] = False
        if 'friends' in friendsConnection:
            friends = friendsConnection['friends']
            if type(friends) is list and len(friends) == 2:
                
                if self.checkBlock(friends[0], friends[1]) or self.checkBlock(friends[1], friends[0]):
                    # if one is in the block list of another, cannot build friend connection
                    print(friends[0] + " and " + friends[1] + " have block relation, cannot build friend connection")
                    pass
                else:
                    self.insertConnection(self.friends_dict, friends[0], friends[1])
                    self.insertConnection(self.friends_dict, friends[1], friends[0])
                    buildResult['success'] = True

        return buildResult

    def insertConnection(self, targetDict, left, right):
        if left not in targetDict:
            targetDict[left] = list()

        # avoid redundancy
        if right not in targetDict[left]:
            targetDict[left].append(right)

    def retrieveFriends(self, email):
        ans = {'success': False, 'friends': [], 'count': 0}
        if 'email' in email:
            address = email['email']
            if address in self.friends_dict:
                ans['success'] = True
                ans['friends'] = self.friends_dict[address][:]
                ans['count'] = len(ans['friends'])
        return ans

    def retrieveCommonFriends(self, friends):
        ans = {'success': False, 'friends': [], 'count': 0}
        if ('friends' in friends) and (len(friends['friends']) == 2):
            friend0 = friends['friends'][0]
            friend1 = friends['friends'][1]
            friendlist0 = self.retrieveFriends({'email': friend0})['friends']
            friendlist1 = self.retrieveFriends({'email': friend1})['friends']
            ans['friends'] = list(set(friendlist0).intersection(set(friendlist1)))
            ans['count'] = len(ans['friends'])
            if (ans['count'] > 0):
                ans['success'] = True
        return ans

    def subscribeUpdate(self, request):
        subResult = dict()
        subResult['success'] = False
        if 'requestor' in request and 'target' in request:
            requestor = request['requestor']
            target = request['target']
            self.insertConnection(self.subscribe, requestor, target)
            subResult['success'] = True
        return subResult

    def blockUpdates(self, request):
        blockResult = dict()
        blockResult['success'] = False
        if 'requestor' in request and 'target' in request:
            requestor = request['requestor']
            target = request['target']

            # update block dict
            self.insertConnection(self.block, requestor, target)

            # if they are friends, delete target from requestor
            if requestor in self.friends_dict:
                self.friends_dict[requestor].remove(target)

            # if requestor subscribes to target, remove subscription
            if requestor in self.subscribe:
                self.subscribe[requestor].remove(target)

            blockResult['success'] = True
        return blockResult

    def checkBlock(self, requestor, target):
        if requestor in self.block and target in self.block[requestor]:
            return True
        return False

    def retrieveRecipients(self, senderText):
        ans = dict()
        ans['success'] = False
        ans['recipients'] = list()

        if 'sender' in senderText and 'text' in senderText:
            sender = senderText['sender']
            text = senderText['text']

            textWordList = str(text).split()
            mentionedRecipients = list()
            for string in textWordList:
                if '@' in string and self.checkBlock(string, sender) is False:
                    mentionedRecipients.append(string)
            ans['recipients'] += list(set(mentionedRecipients))

            senderFriends = self.friends_dict[sender]
            for friend in senderFriends:
                if sender in self.friends_dict[friend]:
                    ans['recipients'].append(friend)
            for requestor in self.subscribe:
                if sender in self.subscribe[requestor]:
                    ans['recipients'].append(requestor)

            ans['recipients'] = list(set(ans['recipients']))
            ans['success'] = True

        return ans


def printTestCase(id, ele):
    print("Case " + str(id) + ": " + str(ele))


# Test Cases

# Case 1: correct input
fm = FriendsManagement()
test_json = {'friends': ['andy@example.com', 'john@example.com']}
printTestCase(1, fm.buildConnection(test_json))

# Case 2: incorrect number of emails
fm = FriendsManagement()
test_json = {'friends': ['andy@example.com']}
printTestCase(2, fm.buildConnection(test_json))

# Case 3: empty dict
fm = FriendsManagement()
test_json = dict()
printTestCase(3, fm.buildConnection(test_json))

# Case 4: retrieve an existing email
fm = FriendsManagement()
test_json = {'friends': ['andy@example.com', 'john@example.com']}
fm.buildConnection(test_json)
emailAdd1 = {'email': 'andy@example.com'}
printTestCase(4, fm.retrieveFriends(emailAdd1))

# Case 5: retrieve an non-existing email
emailAdd2 = {'email': 'hellowordl@163.com'}
printTestCase(5, fm.retrieveFriends(emailAdd2))

# Case 6: retrieve common friends (no common)
fm = FriendsManagement()
fm.buildConnection({'friends': ['andy@example.com', 'john@example.com']})
fm.buildConnection({'friends': ['andy@example.com', 'helloworld@example.com']})
printTestCase(6, fm.retrieveCommonFriends({'friends': ['andy@example.com', 'helloworld@example.com']}))

# Case 7: retrieve common friends (has common)
printTestCase(7, fm.retrieveCommonFriends({'friends': ['john@example.com', 'helloworld@example.com']}))

# Case 8: subscribe
fm = FriendsManagement()
printTestCase(8, fm.subscribeUpdate({'requestor': "lisa@example.com", "target": "john@example.com"}))

# Case 9: subscribe (empty)
fm = FriendsManagement()
printTestCase(9, fm.subscribeUpdate({}))

# Case 10: block
fm = FriendsManagement()
printTestCase(10, fm.blockUpdates({'requestor': "andy@example.com", "target": "john@example.com"}))
printTestCase(10, fm.buildConnection({'friends': ['andy@example.com', 'john@example.com']}))

# Case 11:
senderText = {
    "sender": "john@example.com",
    "text": "Hello World! kate@example.com"
}
fm = FriendsManagement()
fm.buildConnection({'friends': ['andy@example.com', 'john@example.com']})
fm.blockUpdates({'requestor': "andy@example.com", "target": "john@example.com"})
fm.subscribeUpdate({'requestor': "helloworld@example.com", "target": "john@example.com"})
printTestCase(11, fm.retrieveRecipients(senderText))
