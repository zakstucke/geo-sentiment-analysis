# import line_profiler

# import cProfile
# import pstats

# profiler = cProfile.Profile()


# def PROFILE(fn):
#     def inner(*args, **kwargs):
#         lp = line_profiler.LineProfiler()
#         lp_wrapper = lp(fn)
#         result = lp_wrapper(*args, **kwargs)
#         lp.print_stats()
#         return result

#     return inner


# def CPROFILE(fn):
#     def inner(*args, **kwargs):
#         result = None
#         try:
#             result = profiler.runcall(fn, *args, **kwargs)
#         finally:
#             stats = pstats.Stats(profiler)
#             stats.strip_dirs().sort_stats("time").print_stats(10)
#         return result

#     return inner
