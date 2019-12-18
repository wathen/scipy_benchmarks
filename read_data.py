import os
import wget
import sys
import importlib
import fileinput
import inspect
import argparse
data_location = "https://raw.githubusercontent.com/scipy/scipy/master/benchmarks/benchmarks/go_benchmark_functions/"
parser = argparse.ArgumentParser(
    description=f'Scipy benchmark reader:\ncollects data from \n'
                f'{data_location} \nfor least squares problems',
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p", "--problem",
                    type=str,
                    help="Used to define specific problem, for example: \n"
                    "'python read_data.py -p Mishra08'")
parser.add_argument("-ps", "--problem-set", type=str,
                    help='Used to define the path to a text file of problems\n'
                    '(see benchmark_list.txt for example)')
args, _ = parser.parse_known_args()

problem = args.problem
problem_set = args.problem_set


def replaceAll(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)


def import_by_string(full_name):
    module_name, unit_name = full_name.rsplit('.', 1)
    return getattr(__import__(module_name, fromlist=['']), unit_name)


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{dir_path}/data")
try:
    os.mkdir("data")
except FileExistsError:
    print("Data file already exists")

if problem_set == None and problem == None:
    problem_set = [line.rstrip('\n') for line in open('benchmark_list.txt')]
elif isinstance(problem, str):
    problem_set = [problem]
else:
    problem_set = [line.rstrip('\n') for line in open(problem_set)]

prob_index = [prob[0] for prob in problem_set]
modules = []

benchmark_file = "https://raw.githubusercontent.com/scipy/scipy/master/benchmarks/benchmarks/go_benchmark_functions/go_benchmark.py"
if not os.path.isfile(f'data/go_benchmark.py'):
    wget.download(benchmark_file, f"data")

for index in list(dict.fromkeys(prob_index)):
    if not os.path.isfile(f'data/go_funcs_{index}.py'):
        print(f"Loading: go_funcs_{index}")
        prob_file = f"{data_location}go_funcs_{index}.py"
        wget.download(prob_file, f"data")
        replaceAll(f"data/go_funcs_{index}.py",
                   "from .go_benchmark import Benchmark",
                   "from go_benchmark import Benchmark")
    else:
        print(f"Data form 'go_funcs_{index}' already loaded")
    globals()[f"go_funcs_{index}"] = \
        importlib.import_module(f"go_funcs_{index}")


module = [f'go_funcs_{prob[0]}.{prob}' for prob in problem_set]
for prob in problem_set:
    boarder = "#" * (len(prob) + 4)
    print(f"\n\n{boarder}\n  {prob}  \n{boarder}")
    name = f'go_funcs_{prob[0]}.{prob}'
    prob_class = import_by_string(name)
    attributes = inspect.getmembers(
        prob_class(), lambda a: not(inspect.isroutine(a)))
    print(prob_class().__doc__)
    function = inspect.getsourcelines(prob_class.fun)
    for f in function[0]:
        print(f)
    for a in attributes:
        if not(a[0].startswith('_') or a[0].endswith('_')):
            print(f"{a[0]}: {a[1]}")

module = [f'go_funcs_{prob[0]}.{prob}' for prob in problem_set]
my_function = import_by_string(module[0])

# for m in module:
#     my_function = import_by_string(m)
#     print(my_function.__doc__)
