#include "common_function.hpp"
#include <glog/glog.h>

namespace CommonFunctions {

void nano_sleep(int nano_seconds) {
  const int MAX_NSECS = 1000000000;

  struct timespec request;
  if (clock_gettime(CLOCK_MONOTONIC, &request) == -1)
    LOG(ERROR) << "my_nano_sleep clock_gettime err 1.";

  long nsec = request.tv_nsec;

  if (clock_gettime(CLOCK_MONOTONIC, &request) == -1)
    LOG(ERROR) << "my_nano_sleep clock_gettime err 2.";

  long interval = request.tv_nsec - nsec;
  request.tv_nsec += (nano_seconds - interval);
  if (request.tv_nsec >= MAX_NSECS) {
    request.tv_nsec -= MAX_NSECS;
    request.tv_sec++;
  }

  int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &request, NULL);
  if (ret != 0) {
    if (ret != EINTR)
      LOG(ERROR) << "my_nano_sleep clock_nanosleep err: " << ret;
    else
      LOG(ERROR) << "my_nano_sleep Interrupted by a signal.";
  }
}

void nano_sleep(double seconds) {
  int64_t nsec_64 = seconds * 1000 * 1000 * 1000;
  int nsec_32 = (int)nsec_64;

  nano_sleep(nsec_32);
}

int64_t current_time_us_monotonic() {
  // 使用CLOCK_MONOTONIC时钟，它提供了自系统启动以来的经过时间
  timespec ts;
  if (clock_gettime(CLOCK_MONOTONIC, &ts) == -1) {
    perror("clock_gettime");
    return 1;
  }

  // 将timespec转换为秒
  int64_t seconds_since_boot = ts.tv_sec;
  int64_t nanoseconds = ts.tv_nsec;

  // 可能你想得到更精确的时间，比如微秒或毫秒，可以这样转换
  int64_t microseconds = seconds_since_boot * 1000000 + nanoseconds / 1000;

  return microseconds;
}

double current_time_sec_monotonic() {
  // 使用CLOCK_MONOTONIC时钟，它提供了自系统启动以来的经过时间
  timespec ts;
  if (clock_gettime(CLOCK_MONOTONIC, &ts) == -1) {
    perror("clock_gettime");
    return 1;
  }

  // 将timespec转换为秒
  int64_t seconds_since_boot = ts.tv_sec;
  int64_t nanoseconds = seconds_since_boot * 1000 * 1000 * 1000 + ts.tv_nsec;

  double sec = (double)nanoseconds / 1000.0 / 1000.0 / 1000.0;
  return sec;
}

} // namespace CommonFunctions
