from components import Components
from veriloggen import *


p = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
if not p in sys.path:
    sys.path.insert(0, p)


class Accelerator(Module):
    def __init__(self, inputs, outputs, data_width=32, axi_bus_data_width=256):
        super().__init__('m_accelerator')
        self.num_in = inputs
        self.num_out = outputs
        self.data_width = data_width
        self.axi_bus_data_width = data_width #axi_bus_data_width
        self.__create_accelerator()

    def get_num_in(self):
        return self.num_in

    def get_num_out(self):
        return self.num_out

    def __create_accelerator(self):
        comp = Components()

        clk = self.Input('clk')
        rst = self.Input('rst')
        start = self.Input('start')

        acc_user_done_rd_data = self.Input('acc_user_done_rd_data', self.num_in)
        acc_user_done_wr_data = self.Input('acc_user_done_wr_data', self.num_out)

        acc_user_request_read = self.Output('acc_user_request_read', self.num_in)
        acc_user_read_data_valid = self.Input('acc_user_read_data_valid', self.num_in)
        acc_user_read_data = self.Input('acc_user_read_data', self.axi_bus_data_width * self.num_in)

        acc_user_available_write = self.Input('acc_user_available_write', self.num_out)
        acc_user_request_write = self.Output('acc_user_request_write', self.num_out)
        acc_user_write_data = self.Output('acc_user_write_data', self.axi_bus_data_width * self.num_out)
        acc_user_done = self.Output('acc_user_done')
