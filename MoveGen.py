import pieces
import time
import board

def generate_all_possible_moves(dimension=20):
    N = dimension
    move_list = []


    # move has an x , y, rot, flip, and piece id

    # for each x, y
    for x in range(N):
        for y in range(N):
            for piece in pieces.get_piece_list("valid_pieces.txt"):
                for rotation in range(4):
                    for flip in range(1):
                        move = board.Move(piece, x, y, rotation, flip,)
                        ok = legal(move)
                        if ok:
                            piece_coords = move.get_indeces()
                            if piece_coords not in move_list:
                                if not contains_move(move_list, piece_coords):
                                    move_list.append(piece_coords)

    move_list = add_missing_moves(move_list)

    print "all possible moves from blank board : %d" % len(move_list)
    with open('logs/all-possible-dimensions.txt', 'w') as file:
        for move in move_list:
            file.write(move.__str__())

def contains_move(arr, coords):
    for element in arr:
        if equal(element, coords):
            return True

    return False

def add_missing_moves(arr):
    moves = [[[17, 17, 18, 19, 19], [8, 9, 9, 9, 10]],[[8, 8, 9, 9, 10], [11, 12, 10, 11, 11]],[[8, 9, 7, 8, 8], [14, 14, 13, 13, 12]],[[6, 5, 4, 4, 3], [3, 3, 3, 4, 4]],[[2, 3, 4, 3, 4], [19, 19, 19, 18, 18]],[[14, 14, 14, 14, 13], [11, 10, 9, 8, 11]],[[4, 4, 4, 5], [9, 10, 11, 9]],[[2, 2, 2, 3], [0, 1, 2, 0]],[[14, 15, 13, 14, 14], [4, 4, 3, 3, 2]],[[10, 11, 9, 10, 10], [12, 12, 11, 11, 10]],[[8, 7, 6, 6, 5], [1, 1, 1, 2, 2]],[[3, 3, 3, 4, 4], [5, 6, 7, 7, 8]],[[4, 4, 4, 5, 5], [3, 4, 5, 4, 5]],[[6, 6, 6, 7, 7], [12, 13, 14, 14, 15]],[[6, 6, 6, 7, 7], [16, 17, 18, 17, 18]],[[15, 14, 14, 14, 13], [6, 6, 7, 8, 8]],[[7, 7, 8, 8], [3, 4, 4, 5]],[[14, 14, 15, 16, 16], [0, 1, 1, 1, 2]],[[2, 3, 1, 2, 2], [16, 16, 15, 15, 14]],[[7, 6, 8, 7, 7], [0, 0, 1, 1, 2]],[[2, 3, 4, 5, 2], [1, 1, 1, 1, 0]],[[9, 8, 8, 7], [5, 5, 6, 6]],[[0, 0, 0, 1, 1], [6, 7, 8, 8, 9]],[[3, 2, 1, 2, 1], [4, 4, 4, 5, 5]],[[8, 8, 9, 9, 10], [11, 12, 10, 11, 11]],[[2, 2, 2, 1, 1], [8, 7, 6, 7, 6]],[[7, 7, 7, 6], [17, 16, 15, 17]],[[15, 16, 17, 18, 15], [9, 9, 9, 9, 8]],[[5, 6, 7, 6, 7], [19, 19, 19, 18, 18]],[[0, 0, 0, 0, 1], [7, 8, 9, 10, 7]],[[3, 3, 3, 4, 4], [2, 3, 4, 3, 4]],[[14, 13, 12, 13, 12], [13, 13, 13, 14, 14]],[[7, 6, 5, 5, 4], [0, 0, 0, 1, 1]],[[14, 13, 12, 11, 14], [1, 1, 1, 1, 2]],[[1, 1, 1, 1, 0], [6, 5, 4, 3, 6]], [[6, 5, 4, 4, 3], [5, 5, 5, 6, 6]],[[14, 13, 12, 11, 14], [16, 16, 16, 16, 17]],[[15, 14, 13, 12, 13], [12, 12, 12, 12, 13]],[[10, 11, 11, 11, 12], [11, 11, 10, 9, 9]],[[14, 14, 14, 13, 13], [10, 9, 8, 8, 7]],[[8, 9, 10, 8], [6, 6, 6, 5]],[[2, 2, 2, 2, 3], [3, 4, 5, 6, 5]],[[4, 4, 4, 4, 3], [16, 15, 14, 13, 14]], [[19, 19, 19, 19, 18], [3, 2, 1, 0, 1]], [[1, 2, 2, 3], [4, 4, 3, 3]],[[8, 9, 7, 8, 8], [13, 13, 12, 12, 11]],[[5, 5, 5, 5, 6], [0, 1, 2, 3, 0]],[[3, 3, 3, 3, 4], [6, 7, 8, 9, 6]],[[6, 5, 4, 4, 3], [11, 11, 11, 12, 12]],[[2, 2, 2, 3, 3], [13, 14, 15, 15, 16]],[[2, 1, 0, 1, 0], [5, 5, 5, 6, 6]],[[16, 15, 14, 13, 14], [7, 7, 7, 7, 8]],[[16, 15, 14, 13, 14], [9, 9, 9, 9, 10]],[[9, 9, 9, 9, 8], [9, 8, 7, 6, 7]],[[18, 17, 17, 17, 16], [8, 8, 9, 10, 10]],[[16, 15, 15, 15, 14], [11, 11, 12, 13, 13]],[[18, 18, 18, 17], [18, 17, 16, 18]],[[4, 4, 4, 3], [18, 17, 16, 18]],[[15, 14, 14, 13], [5, 5, 6, 6]],[[0, 1, 2, 3, 0], [1, 1, 1, 1, 0]],[[6, 6, 5, 5, 4], [17, 16, 18, 17, 17]],[[14, 14, 14, 13, 13], [18, 17, 16, 17, 16]],[[11, 12, 10, 11, 11], [15, 15, 14, 14, 13]],[[14, 15, 13, 14, 14], [2, 2, 1, 1, 0]],[[8, 7, 6, 6, 5], [2, 2, 2, 3, 3]],[[0, 0, 1, 1, 2], [18, 19, 17, 18, 18]],[[19], [19]],[[0, 0, 1, 2, 2], [3, 4, 4, 4, 5]],[[7, 8, 6, 7, 7], [2, 2, 1, 1, 0]],[[17, 16, 15, 14, 15], [15, 15, 15, 15, 16]],[[3, 3, 3, 3, 4], [6, 7, 8, 9, 6]],[[5, 5, 5, 6, 6], [11, 12, 13, 13, 14]],[[5, 4, 3, 3, 2], [2, 2, 2, 3, 3]],[[11, 11, 11, 11, 10], [18, 17, 16, 15, 16]],[[6, 6, 6, 6, 5], [18, 17, 16, 15, 16]], [[17, 16, 16, 15], [16, 16, 17, 17]],[[11, 11, 11, 10], [12, 11, 10, 12]],[[1, 2, 2, 3], [4, 4, 3, 3]]]
    for move in moves:
        if not contains_move(arr,move):
            arr.append(move)

    return arr

def legal(move):
    arr = move.get_indeces()
    xlist= arr[0]
    ylist = arr[1]
    assert(len(xlist) == len(ylist))

    for index in range (len(xlist)):
        x = xlist[index]
        y = ylist[index]
        if x < 0 or x >= 20 or y < 0 or y >= 20:
            return False
    return True

def get_piece_by_id(id):
    p_list = pieces.get_piece_list("valid_pieces.txt")
    for piece in p_list:
        if piece.get_id() == id:
            return piece
    return None

def get_index_old(target, arr= None):
    if arr is None:
        arr = get_all_possible_dimensions()
    for position, item in enumerate(arr):
        found = True
        if len(item) == len(target):
            for index in range(len(target)):
                if not str(item[index]) == str(target[index]):
                    found = False

            if found: return position

    return None

def get_index(target, arr= None):
    if arr is None:
        arr = get_all_possible_dimensions()

    for position, item in enumerate(arr):
        if equal(target, item):
            return position

    return None

def equal(e_d, n_d):
    assert len(e_d) == 2
    assert len(n_d) == 2

    if e_d == n_d:
        return True
    if len(e_d[0]) != len(n_d[0]) or len(e_d[1]) != len(n_d[1]):
        return False

    equal = True
    n_pairs = []
    e_pairs = []

    for i in range(len(n_d[0])):
        n_pairs.append([n_d[0][i], n_d[1][i]])
        e_pairs.append([e_d[0][i], e_d[1][i]])

    for pair in e_pairs:
        if pair not in n_pairs:
            equal = False

    return equal

def find_move(move):
    indeces = move.get_indeces()
    position = get_index(indeces)
    if position == None:
        print move.get_indeces()
    return position

def get_index_test(arr = None, p = 27378):
    #max_arr = get_all_possible_moves()
    #print max_arr.__str__ ()
    start_time = time.time()

    arr = get_all_possible_dimensions()
    target = ([19, 18], [19, 19])
    position = get_index(target, arr)
    assert position == p, "Error finding object"
    time_taken = time.time() - start_time
    print "OK"
    return

def get_all_possible_dimensions():
    move_arr = []
    with open('logs/all-possible-dimensions.txt', 'r') as file:
        for line in file:
            component = line.split("]")
            pair = []
            for i in component:
                if not i == "":
                    if len(pair) ==2:
                        move_arr.append(pair)
                        pair = []
                    arr = i.replace("[","").replace("(","").replace(")","")

                    arr2 = arr.replace("'',", "")
                    if not arr2 ==  "":
                        if arr2[0] == "," or arr2[0] == " ":
                            arr2 = arr2[1:]
                        values = []
                        for v in  arr2.split(","):
                            values.append(int(v))
                        pair.append(values)
    return move_arr

def test_single_pieces():
    count = 0
    arr = get_all_possible_dimensions()
    for value in arr:
        if value[0] == value[1]:
            print value

    return count


if __name__ == "__main__":
    generate_all_possible_moves()

    #print 15247009794202269497  < 21387237809096644609
