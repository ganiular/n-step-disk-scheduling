import random


class Request:
    def __init__(self, number) -> None:
        self.track_number = number
        self.seek_time = 0


class NStepScanDiskSheduling:
    def __init__(self, n, requests: list[Request], volume) -> None:
        self.volume = volume  # disk volume, 100 by default
        self.rotational_latency = 5  # milliseconds per track
        self.total_seek_time = 0

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
                else:
                    seek_time = self.volume - current_pos
                    seek_time += self.volume - request.track_number
                    current_pos = request.track_number
                    direction = "left"
            elif direction == "left":
                if request.track_number <= current_pos:
                    seek_time = current_pos - request.track_number
                    current_pos = request.track_number
                else:
                    seek_time = current_pos + request.track_number
                    current_pos = request.track_number
                    direction = "right"

            self.serve_request(request, seek_time)

    def serve_request(self, request: Request, seek_time):
        request.seek_time = seek_time
        self.total_seek_time += seek_time
        self.served_requests.append(request)

    def print_result(self):
        print("-" * 35)
        print("Track number \t| Seek time")
        print("-" * 35)
        for request in self.served_requests:
            print(request.track_number, "\t\t|", request.seek_time)
        print("Total seek time:", self.total_seek_time)
        # tranfer_time = self.total_seek_time + self.rotational_latency
        # print("Transfer time:", tranfer_time)
        # access_time = self.total_seek_time + self.rotational_latency + tranfer_time
        # print("Disk access time:", access_time)
        # print("Throughput:", self.request_count / access_time)
        throughput = self.request_count / self.total_seek_time
        print("Throughput:", throughput)

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
    requests = list(eval(input("Requests: ")))
    head_pos = int(input("Enter head position: "))

    # Convert each item to Request type, and raise error if any number is greater than disk size
    for i in range(len(requests)):
        x = requests[i]
        if x > volume:
            raise ValueError(f"Invalid track number: {x} is more than disk volume")
        requests[i] = Request(x)

    for i in range(1, N + 1):
        print("\nFor N =", i)
        ds = NStepScanDiskSheduling(i, requests.copy(), volume)
        ds.start(head_pos)
        ds.print_result()
