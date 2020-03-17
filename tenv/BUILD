package(default_visibility = ["//visibility:public"])

py_library(
    name = "py_logger_lib",
    srcs = [
        "logger.py",
    ],
    deps = [],
)

py_library(
    name = "py_default_lib",
    srcs = [
        "market.py",
        "portfolio.py",
        "scenario.py",
    ],
    deps = [
        "//tenv:py_logger_lib",
    ],
)

py_test(
    name = "market_test",
    srcs = ["market_test.py"],
    deps = [
        ":py_default_lib",
        ":py_logger_lib",
    ],
)

py_test(
    name = "portfolio_test",
    srcs = ["portfolio_test.py"],
    deps = [
        ":py_default_lib",
        ":py_logger_lib",
    ],
)
