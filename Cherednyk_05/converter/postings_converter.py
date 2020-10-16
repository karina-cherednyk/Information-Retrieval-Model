
def from_gamma_str(gamma_str: str):
    gaps = []
    # create gaps list
    while gamma_str:
        n = gamma_str.find('0')
        # before  0 there are n '1'
        # with leading 1 total number =  1 + str[n+1 : n+1 + n  ] = [n+1 : 2n+1]
        gaps.append(int('1' + gamma_str[n + 1: 2 * n + 1], 2))
        gamma_str = gamma_str[2 * n + 1:]
    return get_ids(gaps)


def to_gamma(id):
    # format 0b + binary num
    res = bin(id)[3:]
    res = len(res) * '1' + '0' + res
    return res


def get_ids(gaps):
    id_prev = gaps[0]
    ids = [id_prev]
    for gap in gaps[1:]:
        id_prev = gap + id_prev
        ids.append(id_prev)
    return ids


def get_gaps(ids):
    id_prev = ids[0]
    gaps = [id_prev]
    for id in ids[1:]:
        gaps.append(id - id_prev)
        id_prev = id
    return gaps


def to_str(ids, to_f):
    gaps = get_gaps(ids)
    m_str = ''
    for gap in gaps:
        m_str += to_f(gap)

    return m_str


def to_gamma_str(ids):
    return to_str(ids, to_gamma)


def to_vb_str(ids):
    return to_str(ids, to_vb)


def to_vb(id):
    b_id = bin(id)[2:]
    vb_str = ''
    leading = '1'
    while len(b_id) > 7:
        vb_str = leading + b_id[-7:] + vb_str
        b_id = b_id[:-7]
        leading = '0'
    vb_str = leading + (7 - len(b_id)) * '0' + b_id + vb_str
    return vb_str


def from_vb_str(vb_str):
    gaps = []
    gap = ''
    while len(vb_str) > 8:
        gap += vb_str[1:8]
        if vb_str[0] == '1':
            gaps.append(int(gap, 2))
            gap = ''
        vb_str = vb_str[8:]
    gaps.append(int(vb_str[1:], 2))
    return get_ids(gaps)


