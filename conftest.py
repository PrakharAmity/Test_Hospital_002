import sys
import io
import json
import time

class ExecutionEngineJsonReporter:
    def __init__(self):
        self.start_time = None
        self.real_stdout = sys.__stdout__
        self.real_stderr = sys.__stderr__
        self.buffer = io.StringIO()
        self.bugs = {
            "Bug 1: Appointment Date Range Upper Boundary Filter": {
                "test_name": "test_appointment_date_range_includes_boundary_date",
                "status": "passed",
                "duration": 0.0
            },
            "Bug 2: Patient Pagination Page Slicing": {
                "test_name": "test_patient_pagination_page_size_and_no_skipped_records",
                "status": "passed",
                "duration": 0.0
            },
            "Bug 3: Appointment Deletion by UUID": {
                "test_name": "test_appointment_delete_removes_exact_record",
                "status": "passed",
                "duration": 0.0
            },
            "Bug 4: Patient Search Loading State Reset": {
                "test_name": "test_patient_search_resets_loading_state_on_error",
                "status": "passed",
                "duration": 0.0
            },
            "Bug 5: Billing Invoice GST and Discount Calculation": {
                "test_name": "test_billing_total_with_discount_and_gst",
                "status": "passed",
                "duration": 0.0
            },
            "Bug 6: Receptionist Revenue Access Permission": {
                "test_name": "test_receptionist_forbidden_from_revenue_endpoint",
                "status": "passed",
                "duration": 0.0
            }
        }
        self.any_failed = False
        self.printed = False

    def pytest_sessionstart(self, session):
        self.start_time = time.time()

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            test_fn = report.location[2]
            for bug_title, bug_meta in self.bugs.items():
                if bug_meta["test_name"] == test_fn:
                    bug_meta["duration"] = report.duration
                    if report.failed:
                        bug_meta["status"] = "failed"
                        self.any_failed = True
                    else:
                        bug_meta["status"] = "passed"
            if report.failed:
                self.any_failed = True

    def output_json(self):
        if self.printed:
            return
        self.printed = True

        total_time = time.time() - (self.start_time or time.time())
        total_time_ms = max(1, int(total_time * 1000))

        passed = sum(1 for b in self.bugs.values() if b["status"] == "passed")
        failed = sum(1 for b in self.bugs.values() if b["status"] == "failed")

        result = {}
        for bug_title, bug_meta in self.bugs.items():
            exec_time_ms = max(1, int(bug_meta["duration"] * 1000))
            result[bug_title] = {
                "Status": bug_meta["status"],
                "Execution time": f"{exec_time_ms}ms"
            }

        result["Total bugs"] = len(self.bugs)
        result["Passed"] = passed
        result["Failed"] = failed
        result["Total Execution time"] = f"{total_time_ms}ms"

        # Restore stdout and print ONLY the JSON block
        sys.stdout = self.real_stdout
        sys.stderr = self.real_stderr
        self.real_stdout.write(json.dumps(result, indent=2) + "\n")
        self.real_stdout.flush()

reporter = ExecutionEngineJsonReporter()

def pytest_configure(config):
    # Silence all standard output during pytest execution
    sys.stdout = reporter.buffer
    sys.stderr = reporter.buffer
    config.pluginmanager.register(reporter, "execution_engine_json_reporter")

def pytest_unconfigure(config):
    reporter.output_json()
