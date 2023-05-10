from diagrams import Cluster, Diagram, Edge
from diagrams.programming.language import Python
from diagrams.generic.os import Windows
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.framework import FastAPI
from diagrams.generic.device import Mobile

with Diagram("Auto-GPT-0.3.0 Data Ingestion", show=False):
    with Cluster("data_ingestion.py"):
        argparse = Python("argparse")
        logging = Python("logging")
        ingest_file = Python("ingest_file")
        list_files = Python("list_files")
        config = Python("Config")
        get_memory = Python("get_memory")

        configure_logging = Python("configure_logging")
        main = Python("main")

        argparse >> configure_logging
        logging >> configure_logging
        configure_logging >> main

        ingest_file >> main
        list_files >> main
        config >> main
        get_memory >> main

        argparse >> Edge(label="max_length, overlap_length") >> main
    with Cluster("tests.py"):
        unittest = Python("unittest")
        coverage = Python("coverage")

        coverage_object = Python("Coverage object")
        start_coverage = Python("start")
        discover_tests = Python("defaultTestLoader.discover")
        run_tests = Python("TextTestRunner.run")
        stop_coverage = Python("stop")
        save_coverage_report = Python("save")
        print_coverage_report = Python("report")

        coverage >> coverage_object
        coverage_object >> start_coverage
        unittest >> discover_tests
        discover_tests >> run_tests
        run_tests >> stop_coverage
        stop_coverage >> save_coverage_report
        save_coverage_report >> print_coverage_report

        main_py = Python("main.py")
        autogpt_main = Python("autogpt.main")

        main_py >> Edge(label="call") >> autogpt_main

    with Cluster("benchmark_entrepreneur_gpt_with_difficult_user.py"):
        autogpt_module = Python("autogpt")
        run_50_questions = Python("run 50 questions")
        record_correctness = Python("record correctness")
        record_errors = Python("record errors")

        autogpt_module >> run_50_questions
        run_50_questions >> record_correctness
        run_50_questions >> record_errors