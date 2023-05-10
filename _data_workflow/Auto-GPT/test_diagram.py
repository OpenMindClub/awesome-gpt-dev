from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.generic.os import Windows
from diagrams.generic.blank import Blank

with Diagram("tests.py Structure", show=False):
    with Cluster("tests.py"):
        main = Python("__main__")
        tests_py = Python("tests.py")
        main - tests_py

    with Cluster("autogpt/tests"):
        test_directory = Windows("autogpt/tests")
        test_files = Python("test_*")
        test_directory - test_files

    with Cluster("Python unittest library"):
        unittest = Python("unittest")
        test_loader = Python("defaultTestLoader()")
        test_runner = Python("TextTestRunner()")
        unittest - test_loader
        unittest - test_runner

    tests_py - unittest
    test_loader - test_directory
    test_runner - test_files
