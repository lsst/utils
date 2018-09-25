#include <iostream>
#include <typeinfo>
#include "lsst/utils/Demangle.h"


template<typename T1, typename T2>
class Foo {};

int main()
{
    Foo<float, int> im;

    std::cout << typeid(im).name()
              << " "
              << lsst::utils::demangleType(typeid(im).name())
              << std::endl;
}
