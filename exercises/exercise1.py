import random

from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub


class Message(MessageStub):

    # the constructor-function takes the source and destination as arguments. These are used for "routing" but also
    # for pretty-printing. Here we also take the specific flag of "is_ping"
    def __init__(self, sender: int, destination: int, text):
        # first thing to do (mandatory), is to send the arguments to the "MessageStub" constructor
        super().__init__(sender, destination)
        self.text = text
        # finally we set the field

    # remember to implement the __str__ method such that the debug of the framework works!
    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.text}'


class GossipMessage(MessageStub):

    def __init__(self, sender: int, destination: int, secrets):
        super().__init__(sender, destination)
        # we use a set to keep the "secrets" here
        self.secrets = secrets

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.secrets}'


class Gossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system

        self._secrets = set([index])

    def run(self):
        # the following is your termination condition, but where should it be placed?
        # if len(self._secrets) == self.number_of_devices():
        #    return
        return

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')


class ImprovedGossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system

        self._secrets = set([index])

    def run(self):
        # the following is your termination condition, but where should it be placed?
        message = Message(self.index(), random.randrange(0, self.number_of_devices()), "Hejsa")

        if len(self._secrets) == self.number_of_devices():
            return
    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')
