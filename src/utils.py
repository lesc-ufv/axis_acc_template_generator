import math
import subprocess

import networkx as nx
import numpy as np
from veriloggen import *


def bits(n):
    if n < 2:
        return 1
    else:
        return int(math.ceil(math.log2(n)))


def get_dot_color_by_op(op):
    dic = {
        'add': 'lightblue ',
        'sub': 'lightcyan2',
        'mul': 'lightgoldenrod',
        'or': 'lightblue3',
        'xor': 'lightblue4',
        'and': 'lightcoral',
        'not': 'lightcyan',
        'abs': 'lightcyan1',
        'pass': 'lightblue1',
        'muladd': 'lightcyan3',
        'mulsub': 'lightcyan4',
        'addadd': 'lightblue',
        'subsub': 'lightgoldenrod1',
        'addsub': 'lightgoldenrod2',
        'mux': 'lightgoldenrod3',
        'slt': 'lightgoldenrod4',
        'sgt': 'lightgoldenrodyellow',
        'seq': 'lightgray',
        'sne': 'lemonchiffon',
        'shl': 'lemonchiffon1',
        'shr': 'lemonchiffon2',
        'max': 'lemonchiffon3',
        'min': 'lemonchiffon4',
    }
    return dic[op]



def initialize_regs(module: Module, values=None):
    regs = []
    if values is None:
        values = {}
    flag = False
    for r in module.get_vars().items():
        if module.is_reg(r[0]):
            regs.append(r)
            if r[1].dims:
                flag = True

    if len(regs) > 0:
        if flag:
            i = module.Integer('i_initial')
        s = module.Initial()
        for r in regs:
            if values:
                if r[0] in values.keys():
                    value = values[r[0]]
                else:
                    value = module.get_vars()[r[0]].initval if module.get_vars()[r[0]].initval else 0
            else:
                value = module.get_vars()[r[0]].initval if module.get_vars()[r[0]].initval else 0
            if r[1].dims:
                genfor = For(i(0), i < r[1].dims[0], i.inc())(
                    r[1][i](value)
                )
                s.add(genfor)
            else:
                s.add(r[1](value))


def create_chess(shape, n):
    conf_matrix = np.zeros(shape, dtype=int)
    flag = False
    for i in range(shape[0]):
        flag = not flag
        for j in range(shape[1]):
            if flag:
                conf_matrix[i][j] = n
            flag = not flag

    return conf_matrix


def commands_getoutput(cmd):
    byte_out = subprocess.check_output(cmd.split())
    str_out = byte_out.decode("utf-8")
    return str_out


def find_files(dir, typeFile, extensions):
    print("Finding %s files ... " % typeFile)
    str_sim = ""
    for extn in extensions:
        str = commands_getoutput("find " + dir + " -type f -name *" + extn)
        if len(str.strip()) != 0:
            print(str)
            for f in str.split('\n'):
                if len(f) != 0:
                    aux = f.split('/')
                    ind = 0
                    for a in aux:
                        if a == "rtl":
                            break
                        ind = ind + 1
                    filename = "../.."
                    for i in range(ind, len(aux)):
                        filename = filename + "/" + aux[i]
                    str_sim = str_sim + filename + "\n"
    return str_sim


def get_id(l, c, NC):
    return l * NC + c


def bit_rotate_left(val, r_bits, max_bits):
    return (val << r_bits % max_bits) & (2 ** max_bits - 1) | (
            (val & (2 ** max_bits - 1)) >> (max_bits - (r_bits % max_bits)))


def bit_rotate_rigth(val, r_bits, max_bits):
    return ((val & (2 ** max_bits - 1)) >> r_bits % max_bits) | (
            val << (max_bits - (r_bits % max_bits)) & (2 ** max_bits - 1))


def split_modules(str_modules):
    mods = str_modules.split('endmodule')
    modules = {}
    for m in mods:
        m = m.strip(' \n')
        if m.strip('\n') != '':
            name = m.split(' ')[1]
            name = re.sub('[\n\t()!#$%&*-+@=;:<>\/\[\{\}\]]', '', name)
            m = m + '\n\nendmodule'
            modules[name] = m
    return modules


def to_hex(val, bits):
    return format(val, '0%dx' % (bits // 4))


def bfs(g):
    queue = set()
    visitados = [False] * g.number_of_nodes()
    queue.add(0)
    path = []
    while queue:
        n = queue.pop()
        visitados[n] = True
        for v in g.neighbors(n):
            if not visitados[v]:
                path.append((n, v))
                visitados[v] = True
                queue.add(v)

    return path


def create_conf_path(cgra_arch):
    G = nx.Graph()
    for pe in cgra_arch['pe']:
        for w in pe['neighbors']:
            G.add_edge(pe['id'], w)

    return bfs(G)
