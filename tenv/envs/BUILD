package(default_visibility = ["//visibility:public"])

py_library(
    name = "py_default_lib",
    srcs = [
        "average.py",
        "base.py",
        "multi_vol.py",
        "reward.py",
        "simple.py",
    ],
    deps = [
        "//tenv:py_logger_lib",
    ],
)

py_test(
    name = "simple_test",
    srcs = [
        "simple_test.py",
    ],
    deps = [
        ":py_default_lib",
        "//tenv:py_default_lib",
        "//tenv:py_logger_lib",
    ],
)

py_test(
    name = "average_test",
    srcs = [
        "average_test.py",
    ],
    deps = [
        ":py_default_lib",
        "//tenv:py_default_lib",
        "//tenv:py_logger_lib",
    ],
)

py_test(
    name = "multi_vol_test",
    srcs = [
        "multi_vol_test.py",
    ],
    deps = [
        ":py_default_lib",
        "//tenv:py_default_lib",
        "//tenv:py_logger_lib",
    ],
)

py_test(
    name = "reward_test",
    srcs = [
        "reward_test.py",
    ],
    deps = [
        ":py_default_lib",
        "//tenv:py_logger_lib",
    ],
)
