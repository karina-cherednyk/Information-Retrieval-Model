# the same as postings_converter methods to convert id list into bit string and vice versa
# only difference - byte with rank of word in document before every doc id bit string
# rank system: = +1 if in text, +2 if in title, +4 if in author name
# to get rank in range(0,1) divide by 7


def from_gamma_str_zone(gamma_str: str):
    gaps = []
    while gamma_str:
        rank = gamma_str[:8]  # rank is always first byte
        gamma_str = gamma_str[8:]
        n = gamma_str.find('0')
        # before  0 there are n '1'
        # with leading 1 total number =  1 + str[n+1 : n+1 + n  ] = [n+1 : 2n+1]
        # append [ rank, gap ]
        gaps.append([int(rank, 2), int('1' + gamma_str[n + 1: 2 * n + 1], 2)])  # int(x,2) converts bit string in int
        gamma_str = gamma_str[2 * n + 1:]
    return get_rank_id_pairs(gaps)


def to_gamma_zone(pair):
    rank, id = pair
    res_rank = bin(rank)[2:]  # format 0b + binary num
    res_rank = '0' * (8 - len(res_rank)) + res_rank  # add leading zeros
    res_id = bin(id)[3:]  # first bit is always 1, so remove ob1
    res_id = len(res_id) * '1' + '0' + res_id  # gamma code + bin doc id without leading 1
    return res_rank + res_id


def get_rank_id_pairs(rank_gap_pairs):
    """ convert [rank, gap] to [rank, id] """
    id_prev = rank_gap_pairs[0][1]
    pairs = [rank_gap_pairs[0]]
    for rank, gap in rank_gap_pairs[1:]:
        id_prev = gap + id_prev
        pairs.append([rank, id_prev])
    return pairs


def get_gap_pairs(zone_id_pairs):
    """ convert [rank, id] to [rank, gap] """
    id_prev = zone_id_pairs[0][1]
    pairs = [zone_id_pairs[0]]
    for zone, id in zone_id_pairs[1:]:
        pairs.append([zone, id - id_prev])
        id_prev = id
    return pairs


def to_str(rank_id_pairs, to_f):
    rank_gap_pairs = get_gap_pairs(rank_id_pairs)
    m_str = ''
    for rank_gap_pair in rank_gap_pairs:
        m_str += to_f(rank_gap_pair)
    return m_str


def to_gamma_str_zone(rank_id_pairs):
    """convert [rank, id] to rank byte + gamma code bytes"""
    return to_str(rank_id_pairs, to_gamma_zone)


def to_vb_str_zone(rank_id_pairs):
    """ convert [rank, id] to rank byte + variable bytes """
    return to_str(rank_id_pairs, to_vb_zone)


def to_vb_zone(pair):
    rank, id = pair
    res_rank = bin(rank)[2:]
    res_rank = '0' * (8 - len(res_rank)) + res_rank
    b_id = bin(id)[2:]
    vb_str_id = ''
    leading = '1'
    while len(b_id) > 7:
        vb_str_id = leading + b_id[-7:] + vb_str_id
        b_id = b_id[:-7]
        leading = '0'
    vb_str_id = leading + (7 - len(b_id)) * '0' + b_id + vb_str_id
    return res_rank + vb_str_id


def from_vb_str_zone(vb_str):
    gaps = []
    gap = ''
    rank = vb_str[:8]  # get rank of fst doc id
    vb_str = vb_str[8:]
    while len(vb_str) > 8:
        gap += vb_str[1:8]
        if vb_str[0] == '1':
            gaps.append(int(rank, 2), int(gap, 2))
            gap = ''
            vb_str = vb_str[8:]
            rank = vb_str[:8]  # fst byte is rank of another doc id
        vb_str = vb_str[8:]
    gaps.append(int(rank, 2), int(vb_str[1:], 2))
    return get_rank_id_pairs(gaps)
