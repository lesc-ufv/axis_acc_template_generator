
from custom_accelerator import Accelerator
from create_acc_axi_interface import AccAXIInterface
from utils import commands_getoutput
import os
import sys
import argparse
import traceback

p = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

if not p in sys.path:
    sys.path.insert(0, p)


def create_args():
    parser = argparse.ArgumentParser('axis_acc_template_generator -h')
    parser.add_argument(
        '-i', '--inputs', help='Number of inputs streams', type=int, default=1)
    parser.add_argument('-o', '--outputs',
                        help='Number of outputs streams', type=int, default=1)
    parser.add_argument(
        '-n', '--name', help='Name of project', type=str, default='prj')
    parser.add_argument(
        '-c', '--clock', help='Synthesis clock in MHz', type=int, default=250)
    parser.add_argument(
        '-d', '--output', help='Project location', type=str, default='.')
    parser.add_argument(
        '-m', '--memory', help='Memory type=[HBM, DDR, HOST]', type=str, default='DDR')
    parser.add_argument(
        '-s', '--size', help='Memory num blocks', type=int, default=1)

    return parser


def write_file(name, string):
    with open(name, 'w') as fp:
        fp.write(string)
        fp.close()


def create_project(root_dir, name, clock, output_path, num_in, num_out, mem_type, size):
    acc = Accelerator(num_in, num_out)
    acc_axi = AccAXIInterface(acc)

    template_path = root_dir + '/resources/template.prj'
    cmd = 'cp -r %s  %s/%s' % (template_path, output_path, name)

    commands_getoutput(cmd)

    hw_path = '%s/%s/hw/' % (output_path, name)
    sw_path = '%s/%s/sw/' % (output_path, name)

    m = acc_axi.create_kernel_top(name)
    m.to_verilog(hw_path + 'src/%s.v' % (name))

    num_axis_str = 'NUM_M_AXIS=%d' % acc.get_num_in()

    vitis_config = acc_axi.get_clock_config(clock, name)
    vitis_config += '\n'
    vitis_config += acc_axi.get_connectivity_config(name, mem_type, size)
    vitis_config += '\n[vivado]\n'
    vitis_config += 'prop=run.impl_1.strategy=Performance_NetDelay_low\n'

    write_file(hw_path + 'simulate/num_m_axis.mk', num_axis_str)
    write_file(hw_path + 'synthesis/num_m_axis.mk', num_axis_str)
    write_file(sw_path + 'host/prj_name', name)
    write_file(hw_path + 'simulate/prj_name', name)
    write_file(hw_path + 'synthesis/prj_name', name)
    write_file(hw_path + 'simulate/vitis_config.txt', vitis_config)
    write_file(hw_path + 'synthesis/vitis_config.txt', vitis_config)


def main():
    args = create_args().parse_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.getcwd() + '/../'

    if args.output == '.':
        args.output = running_path

    create_project(root_dir, args.name, args.clock,
                   args.output, args.inputs, args.outputs, args.memory, args.size)

    print('Project successfully created in %s/%s' %
          (args.output, args.name))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
