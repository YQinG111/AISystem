#include <fstream>
 #include <iostream>
 #include <vector>
 
 #include "net_generated.h"
 using namespace PiNet;
 
 int main() {
     std::ifstream infile;
     infile.open("net.mnn", std::ios::binary | std::ios::in);
     if (!infile.is_open()) {
         std::cerr << "Error: failed to open net.mnn" << std::endl;
         return 1;
     }
     infile.seekg(0, std::ios::end);
     int length = infile.tellg();
     if (length <= 0) {
         std::cerr << "Error: file is empty or unreadable" << std::endl;
         return 1;
     }
     infile.seekg(0, std::ios::beg);
     char* buffer_pointer = new char[length];
     infile.read(buffer_pointer, length);
     if (!infile) {
         std::cerr << "Error: failed to read file contents" << std::endl;
         delete[] buffer_pointer;
         return 1;
     }
     infile.close();
 
     auto net = GetNet(buffer_pointer);
     if (!net) {
         std::cerr << "Error: failed to deserialize net" << std::endl;
         delete[] buffer_pointer;
         return 1;
     }
 
     auto oplists = net->oplists();
     if (!oplists || oplists->size() < 2) {
         std::cerr << "Error: invalid oplists in net" << std::endl;
         delete[] buffer_pointer;
         return 1;
     }
 
     auto ConvOp = oplists->Get(0);
     auto ConvOpT = ConvOp->UnPack();
 
     auto PoolOp = oplists->Get(1);
     auto PoolOpT = PoolOp->UnPack();
 
     auto inputIndexes = ConvOpT->inputIndexes;
     auto outputIndexes = ConvOpT->outputIndexes;
     auto type = ConvOpT->type;
     std::cout << "inputIndexes: " << inputIndexes[0] << std::endl;
     std::cout << "outputIndexes: " << outputIndexes[0] << std::endl;
 
     PiNet::OpParameterUnion OpParameterUnion = ConvOpT->parameter;
     switch (OpParameterUnion.type) {
         case OpParameter_Conv: {
             auto ConvOpParameterUnion = OpParameterUnion.AsConv();
             auto k = ConvOpParameterUnion->kernelX;
             std::cout << "ConvOpParameterUnion, k: " << k << std::endl;
             break;
         }
         case OpParameter_Pool: {
             auto PoolOpParameterUnion = OpParameterUnion.AsPool();
             auto k = PoolOpParameterUnion->padX;
             std::cout << "PoolOpParameterUnion, k: " << k << std::endl;
             break;
         }
         default:
             std::cerr << "Warning: unknown OpParameter type" << std::endl;
             break;
     }

     delete[] buffer_pointer;
     return 0;
 }
