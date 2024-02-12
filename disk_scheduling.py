from prettytable import PrettyTable
import random

class Request:
    def __init__(self, number) -> None:
        self.track_number = number
        self.seek_time = 0


class Result:
    results: list['Result'] = []

    def __init__(self, n, seek_time, head_mount, average_seek_time, transfer_time, disk_access_time) -> None:
        self.n = n
        self.seek_time = seek_time
        self.head_mount = head_mount
        self.average_seek_time = average_seek_time
        self.transfer_time = transfer_time
        self.disk_access_time = disk_access_time
        self.results.append(self)

    def table():
        table_head = []
        table_data = []
        for result in Result.results:
            table_head.append(f"N = {result.n}")
        for result in Result.results:
            table_data.append([
                result.seek_time, 
                result.head_mount, 
                result.average_seek_time, 
                result.transfer_time, 
                result.disk_access_time
            ])
            
        result_table = PrettyTable()
        result_table.field_names = ['Result'] + table_head
        result_table.add_row(["Seek time"] + [col[0] for col in table_data])
        result_table.add_row(["Head Move"] + [col[1] for col in table_data])
        result_table.add_row(["Avearge Seek time"] + [col[2] for col in table_data])
        result_table.add_row(["Transfer time"] + [col[3] for col in table_data])
        result_table.add_row(["Disk access time"] + [col[4] for col in table_data])

        # for i, row_data in enumerate(table_data, start=1):
        #     result_table.add_row([f"Row {i}"] + row_data)
        #     pass

        # Print the table
        print(result_table)

class NStepScanDiskSheduling:
    def __init__(self, n, requests: list[Request], volume, no_of_bytes_to_be_tranfer, no_of_bytes_on_track, rotational_speed) -> None:
        self.volume = volume  # disk volume, 100 by default
        self.rotational_latency = 5  # milliseconds per track
        self.no_of_bytes_to_be_tranfer = no_of_bytes_to_be_tranfer
        self.no_of_bytes_on_track = no_of_bytes_on_track
        self.rotational_speed = rotational_speed
        self.total_head_movement = 0
        self.head_mount = 0
        self.seek_rate = 1

        # Raise error if any track number is greater than the disk volume
        for request in requests:
            if request.track_number > self.volume:
                raise ValueError(
                    f"Invalid track number: {request.track_number} is more than disk volume"
                )

        self.n = n
        self.main_queue = requests
        self.request_count = len(requests)
        self.served_requests = []

    def start(self, from_pos):
        current_pos = from_pos
        sub_queue: list[Request] = []
        direction = None
        while len(self.main_queue) > 0 or len(sub_queue) > 0:
            if len(sub_queue) == 0:
                for i in range(min(self.n, len(self.main_queue))):
                    sub_queue.append(self.main_queue.pop(0))
                sub_queue, _direction = self.sorter(sub_queue, current_pos)
                if not direction:
                    direction = _direction
            request = sub_queue.pop(0)

            if direction == "right":
                if request.track_number >= current_pos:
                    seek_time = request.track_number - current_pos
                    current_pos = request.track_number
                    self.head_mount += 1
                else:
                    seek_time = self.volume - current_pos
                    seek_time += self.volume - request.track_number
                    current_pos = request.track_number
                    self.head_mount += 2
                    direction = "left"
            elif direction == "left":
                if request.track_number <= current_pos:
                    seek_time = current_pos - request.track_number
                    current_pos = request.track_number
                    self.head_mount += 1
                else:
                    seek_time = current_pos + request.track_number
                    current_pos = request.track_number
                    self.head_mount += 2
                    direction = "right"

            self.serve_request(request, seek_time)

    def serve_request(self, request: Request, seek_time):
        request.seek_time = seek_time
        self.total_head_movement += seek_time
        self.served_requests.append(request)

    def print_result(self):
        print("-" * 35)
        print("Track number \t| Seek time")
        print("-" * 35)
        for request in self.served_requests:
            print(request.track_number, "\t\t|", request.seek_time)
        
        print("Total head movement:", self.total_head_movement)

        seek_time = self.total_head_movement / self.seek_rate
        print("Seek time:", seek_time)

        average_seek_time = seek_time / self.request_count
        print("Average seek time:", average_seek_time)

        transfer_time = average_seek_time + (1/2) * (self.rotational_speed) + (self.no_of_bytes_to_be_tranfer / (self.no_of_bytes_on_track * self.rotational_speed))
        print("Transfer time:", transfer_time)

        disk_access_time = seek_time + self.rotational_latency + transfer_time
        print("Disk Access time:", disk_access_time)

        Result(self.n, self.total_head_movement, self.head_mount, average_seek_time, transfer_time, disk_access_time)


    def sorter(self, requests: list[Request], current_pos):
        sort = lambda requests, reverse: sorted(
            requests, key=lambda x: x.track_number, reverse=reverse
        )
        upper = []
        lower = []
        for r in requests:
            if r.track_number > current_pos:
                upper.append(r)
            else:
                lower.append(r)

        upper = sort(upper, False)
        lower = sort(lower, True)

        if not upper or not lower:
            requests = lower + upper
            if requests[0].track_number > current_pos:
                shortest_direction = "right"
            else:
                shortest_direction = "left"
            return requests, shortest_direction

        # find shortest direction
        right_direction = upper[0].track_number - current_pos
        left_direction = current_pos - lower[-1].track_number

        if right_direction < left_direction:
            shortest_direction = "right"
            requests = upper + lower
        else:
            shortest_direction = "left"
            requests = lower + upper
        return requests, shortest_direction


if __name__ == "__main__":
    volume = int(input("Enter disk size: "))
    N = int(input("Enter N value: "))
    requests = input("Requests: ").split(',')
    requests = [int(r) for r in requests]
    more_request_count = int(input("Enter more requests count: "))
    head_pos = int(input("Enter head position: "))
    no_of_bytes_to_be_tranfer = float(input("Enter number of bytes to be trasfer: "))
    no_of_bytes_on_track = float(input("Enter number of byte on track: "))
    rotational_speed = float(input("Enter rotational speed: "))

    # Generate more random requests and add it to the list of requests
    more_requests = [random.randint(0, volume) for i in range(more_request_count)]
    requests += more_requests

    # Print request list
    print("Requests:", requests)

    # Convert each item to Request type, and raise error if any number is greater than disk size
    for i in range(len(requests)):
        x = requests[i]
        if x > volume:
            raise ValueError(f"Invalid track number: {x} is more than disk volume")
        requests[i] = Request(x)

    for i in range(1, N + 1):
        print("\nFor N =", i)
        ds = NStepScanDiskSheduling(i, requests.copy(), volume, no_of_bytes_to_be_tranfer, no_of_bytes_on_track, rotational_speed)
        ds.start(head_pos)
        ds.print_result()


    Result.table()
