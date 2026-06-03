#ifndef COMMON_FUNCTION_HPP
#define COMMON_FUNCTION_HPP

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>
namespace CommonFunctions {

void nano_sleep(int nano_seconds);
void nano_sleep(double seconds);
int64_t current_time_us_monotonic();
double current_time_sec_monotonic();

} // namespace CommonFunctions

#endif // COMMON_FUNCTION_HPP