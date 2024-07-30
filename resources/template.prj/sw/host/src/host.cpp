#include <host.h>

#define DATA_SIZE (1UL << 20UL)

int main(int argc, char *argv[])
{

    if (argc != 3)
    {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File> <Kernel name>" << std::endl;
        return EXIT_FAILURE;
    }

    std::string binaryFile = argv[1];
    std::string kernel_name = argv[2];
 
    auto acc = AccFpga(NUM_CHANNELS, NUM_CHANNELS);
    acc.fpgaInit(binaryFile, kernel_name);

    for (int i = 0; i < NUM_CHANNELS; i++)
    {
        acc.createInputQueue(i,DATA_SIZE);
        acc.createOutputQueue(i,DATA_SIZE);
        auto ptr =  (int*)acc.getInputQueue(i);  
        for(int j = 0; j < DATA_SIZE/4;j++){
          ptr[j] = j+1;            
        }
        
    }

    acc.execute();

    for (int i = 0; i < NUM_CHANNELS; i++)
    {
       auto ptr =  (char*)acc.getOutputQueue(i);
       //comparar aqui!
    }

    acc.printReport();
    acc.cleanup();

    return 0;
}
