from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub


# RipMessage represents the routing table being shared between devices
class RipMessage(MessageStub):
    def __init__(self, sender: int, destination: int, table):
        super().__init__(sender, destination)
        self.table = table  # the routing table is sent with the message

    def __str__(self):
        return f'RipMessage: {self.source} -> {self.destination} : {self.table}'


# RoutableMessage represents a message that needs to be routed through the network
class RoutableMessage(MessageStub):
    def __init__(self, sender: int, destination: int, first_node: int, last_node: int, content):
        super().__init__(sender, destination)
        self.content = content  # the actual content to be delivered
        self.first_node = first_node  # where the message originated
        self.last_node = last_node  # where the message is supposed to go

    def __str__(self):
        return f'RoutableMessage: {self.source} -> {self.destination} : {self.content}'


# RipCommunication represents each device in the network
class RipCommunication(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)

        # For a ring topology, each device has two neighbors: the previous and the next
        self.neighbors = [(self.index() - 1) % number_of_devices, (self.index() + 1) % number_of_devices]

        # Each device's routing table initially only contains itself and direct neighbors
        self.routing_table = dict()

    def run(self):
        """
        The main execution loop for the device.
        Initially, it sends its routing table to its neighbors.
        Then, it listens for incoming messages (both RipMessage and RoutableMessage).
        """
        # Initialize the routing table: direct neighbors with distance 1, self with distance 0
        for neigh in self.neighbors:
            self.routing_table[neigh] = (neigh, 1)  # Direct neighbor at distance 1
        self.routing_table[self.index()] = (self.index(), 0)  # Self at distance 0

        # Broadcast initial routing table to all neighbors
        for neigh in self.neighbors:
            self.medium().send(RipMessage(self.index(), neigh, self.routing_table))

        # Continuous loop to receive and process messages
        while True:
            ingoing = self.medium().receive()

            if ingoing is None:
                # No message received, wait for the next round (for synchronous networks)
                self.medium().wait_for_next_round()
                continue

            if isinstance(ingoing, RipMessage):
                print(f"Device {self.index()}: Got new table from {ingoing.source}")

                # Merge the received routing table with this device's table
                returned_table = self.merge_tables(ingoing.source, ingoing.table)
                if returned_table is not None:
                    # If the table has been updated, send the updated table to neighbors
                    self.routing_table = returned_table
                    for neigh in self.neighbors:
                        self.medium().send(RipMessage(self.index(), neigh, self.routing_table))

            if isinstance(ingoing, RoutableMessage):
                print(
                    f"Device {self.index()}: Routing from {ingoing.first_node} to {ingoing.last_node} via #{self.index()}: [#{ingoing.content}]")

                # If the current device is the destination, deliver the message
                if ingoing.last_node == self.index():
                    print(
                        f"\tDevice {self.index()}: delivered message from {ingoing.first_node} to {ingoing.last_node}: {ingoing.content}")
                    continue

                # If the device knows the route, forward the message to the next hop
                if self.routing_table.get(ingoing.last_node):
                    next_hop, _ = self.routing_table[ingoing.last_node]
                    self.medium().send(
                        RoutableMessage(self.index(), next_hop, ingoing.first_node, ingoing.last_node, ingoing.content))
                    continue

                # Drop the message if no route is known
                print(
                    f"\tDevice {self.index()}: DROP Unknown route #{ingoing.first_node} to #{ingoing.last_node} via #{self.index()}, message #{ingoing.content}")

            # Wait for the next round (for synchronous networks)
            self.medium().wait_for_next_round()

    def merge_tables(self, src, table):
        """
        Merges the routing table received from a neighbor into this device's routing table.
        The table is updated if shorter routes are found.
        Returns the updated table if changes were made, otherwise returns None.
        """
        updated = False
        for destination, (next_hop, distance) in table.items():
            # Calculate the new distance to the destination via the source
            new_distance = distance + 1

            # Update the routing table if the new route is shorter or if destination is not yet in the table
            if destination not in self.routing_table or new_distance < self.routing_table[destination][1]:
                self.routing_table[destination] = (src, new_distance)
                updated = True

        # If the routing table was updated, return the updated table; otherwise return None
        return self.routing_table if updated else None

    def routing_table_complete(self):
        """
        Determines if the routing table is complete.
        A complete routing table means it has routes to all other devices, and all routes are reasonable (no unnecessary long loops).
        """
        # First check if the table contains all possible devices (except self)
        if len(self.routing_table) < self.number_of_devices() - 1:
            return False

        # Ensure that the maximum distance is not greater than half the number of devices (to avoid long loops in the ring)
        for destination, (next_hop, distance) in self.routing_table.items():
            if distance > (self.number_of_devices() / 2):
                return False

        return True

    def print_result(self):
        """
        Prints the final routing table for this device after the network converges.
        """
        print(f'\tDevice {self.index()} has routing table: {self.routing_table}')
