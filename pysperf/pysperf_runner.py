

"""
Output directory structure:

- output
    - runs
        - run1
            - GDPopt-LOA
                - MeOH
                    run_script.sh
                    stdout.log
                    stderr.log
                    pysperf_runner.config
                    pysperf_result.log
                    pysperf_case.pytrace
                - 8PP
                - ...
                solver.pytrace
            - BARON-BM
                - MeOH
                - ...
            pysperf_run.pytrace
        - run2
        - ...
    [broad_overview_files]
"""
from pathlib import Path

import yaml

from pysperf import _SingleRunResult, get_formatted_time_now, config


def run_test_case():
    # Load test run configuration
    with open('pysperf_runner.config') as file:
        runner_options = yaml.safe_load(file)
        model_name = runner_options["model name"]
        solver_name = runner_options["solver name"]
        # Time limit must be updated before solver library import.
        time_limit = runner_options["time limit"]
        config.time_limit = time_limit
    # Setup run
    from pysperf.model_library import models
    from pysperf.solver_library import solvers
    test_model = models[model_name]
    test_solver = solvers[solver_name]
    run_result = _SingleRunResult()
    # Build the model
    run_result.model_build_start_time = get_formatted_time_now()
    pyomo_model = test_model.build_function()
    run_result.model_build_end_time = get_formatted_time_now()
    Path(".single_run_model_built.log").touch()
    # Run the solver
    run_result.solver_start_time = get_formatted_time_now()
    solve_run_result = test_solver.solve_function(pyomo_model)
    run_result.solver_end_time = get_formatted_time_now()
    run_result.update(solve_run_result)
    # Dump results
    with open('pysperf_result.log', 'w') as result_file:
        if 'termination_condition' in run_result:
            run_result.termination_condition = str(run_result.termination_condition)
        yaml.safe_dump(dict(**run_result), result_file)
    # Create pytrace file
    pass  # TODO: write this


if __name__ == "__main__":
    try:
        Path(".single_run_started.log").touch()
        run_test_case()
    finally:
        Path(".single_run_complete.log").touch()
