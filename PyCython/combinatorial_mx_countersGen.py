# solving maximum of counters in py

def solution(N, A):
    counter_list = [0] * N
    current_maximum = 0
    max_increase_to = 0

    for i in A:
        i_idx - i - 1

        if i_idx == N:
            max_increase_to = current_maximum
        else:
            counter_list[i_idx] = max(counter_list[i_idx], max_increase_to)
            counter_list[i_idx] += 1
            current_maximum = max(current_maximum, counter_list[i_idx])

    for idx in range(len(counter_list)):
        counter_list[idx] = max(counter_list[idx], max_increase_to)

    return counter_list

# missing item list difference
def reverse(x):
    output_len = len(x)
    output = [None] * output_len
    output_index = output_len - 1
    for c in x:
        output[output_index] = c 
        output_index -= 1

    return ''.join(output)

def find_missing(full_set, partial_set):
    missing_items = set(full_set) - set(partial_set)
    assert(len(missing_items) == 1)
    return list(missing_items)[0]

def find_missing_xor(full_set, partial_set):
    xor_sum = 0
    for num in full_set:
        xor_sum ^= num
    for num in partial_set:
        xor_sum ^= num

    return xor_sum

# edit distance string comparison
def case_insensitive_compare(s1, s2):
    if len(s1) != len(s2):
        return False
    s1_iter = iter(s1)
    s2_iter = iter(s2)
    for _ in range(len(s1)):
        s1_c = s1_iter.next()
        s2_c = s2_iter.next()
        if not s1_c.upper() == s2_c.upper():
            return False
    return True

def ins_del_compare(s1, s2, tolerance):
    if len(s1) != len(s2):
        if abs(len(s1) - len(s2)) == 1:
            shorter, longer = sorted([s1, s2], key=len)
        else:
            return case_insensitive_compare(s1, s2)
    shorter_iter = iter(shorter)
    longer_iter = iter(longer)
    for _ in range(len(shorter)):
        shorter_c = shorter_iter.next()
        longer_c = longer_iter.next()
        if not longer_c.upper() == shorter_c.upper():
            # push longer one + 1
            next_longer = longer_iter.next()
            if not next_longer.upper() == shorter_c.upper():
                return False
    return True

# pair a coder
def mySolution(mS):
    N = len(mS)
    next = dict()
    datapoint = [None]*(N+1)
    datapoints = [None]*(N+1)
    datapoint[N] = datapoints[N] = 0
    for i in range(N-1,-1,-1):
        datapoints[i] = N-i
        if mS[i] in next:
            j = next[mS[i]]
            datapoints[i] = min(datapoint[j+1], datapoints[j])
        datapoint[i] = min(1 + datapoint[i+1], datapoints[i])
        next[mS[i]] = i

    return datapoint[0]

# missing integer 
def solve(A):
    A = sorted(A)
    A = list(dict.fromkeys(A))
    samePos=1
    for j in A:
        if j>0:
            if j==samePos:
                samePos+=1

    return samePos
    pass
