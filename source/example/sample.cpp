#include <iostream>

int main(int /*argc*/, char** /*argv*/)
{
    std::cout << "Sample code to init the project" << std::endl;

    // LMT_SEL_BEGIN
    std::cout << "Solution code that would be excluded by the file export" << std::endl;
    // LMT_SEL_END

    return EXIT_SUCCESS;
}
