from _collections import deque
from itertools import islice

if __name__ == '__main__':
    data = deque(maxlen=5)

    data.append((0, (1, 2)))
    data.append((1, (10, 20)))
    data.append((2, (100, 200)))
    data.append((3, (1000, 2000)))
    data.append((4, (10000, 20000)))
    data.append((5, (100000, 200000)))
    print(data)
    print('-------------------')

    data.clear()
    data.append((0, (3,)))
    data.append((1, (30,)))
    data.append((2, (300,)))
    data.append((3, (3000,)))
    data.append((4, (30000,)))
    data.append((5, (300000,)))

    data_slice = islice(data, max(0, len(data) - 3), len(data))
    if len(data)>0:
        for i in range(len(data[-1][1])):
            seq = [(x,y[i]) for x,y in data_slice]
            print(seq)



