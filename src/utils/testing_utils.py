"""Testing infrastructure and CI/CD utilities."""

from typing import Dict, List, Optional
from datetime import datetime


class TestMetrics:
    """Tracks testing metrics and coverage."""

    def __init__(self):
        self.test_results: Dict[str, Dict] = {}
        self.coverage_data: Dict[str, float] = {}
        self.ci_runs: List[Dict] = []

    def record_test_result(
        self,
        test_id: str,
        test_name: str,
        status: str,
        duration_ms: float,
        error: Optional[str] = None,
    ) -> Dict:
        """Record a test result."""
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "status": status,
            "duration_ms": duration_ms,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.test_results[test_id] = result
        return result

    def record_coverage(self, module: str, coverage_percent: float):
        """Record test coverage for a module."""
        self.coverage_data[module] = coverage_percent

    def get_test_summary(self) -> Dict:
        """Get overall test summary."""
        results = list(self.test_results.values())
        passed = len([r for r in results if r["status"] == "passed"])
        failed = len([r for r in results if r["status"] == "failed"])
        skipped = len([r for r in results if r["status"] == "skipped"])

        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / len(results) * 100) if results else 0,
            "average_duration_ms": (
                sum(r["duration_ms"] for r in results) / len(results)
                if results
                else 0
            ),
        }

    def get_coverage_report(self) -> Dict:
        """Get coverage report."""
        if not self.coverage_data:
            return {
                "total_coverage": 0,
                "modules": {},
                "compliant": False,
            }

        total = sum(self.coverage_data.values()) / len(self.coverage_data)
        return {
            "total_coverage": round(total, 2),
            "modules": self.coverage_data,
            "compliant": total >= 80,
        }

    def record_ci_run(
        self,
        run_id: str,
        branch: str,
        status: str,
        test_summary: Dict,
        coverage: Dict,
    ) -> Dict:
        """Record a CI/CD pipeline run."""
        run = {
            "run_id": run_id,
            "branch": branch,
            "status": status,
            "test_summary": test_summary,
            "coverage": coverage,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.ci_runs.append(run)
        return run

    def get_ci_history(self, branch: Optional[str] = None) -> List[Dict]:
        """Get CI/CD run history."""
        if branch:
            return [r for r in self.ci_runs if r["branch"] == branch]
        return self.ci_runs

    def get_quality_gate_status(self) -> Dict:
        """Check if code quality meets gate requirements."""
        summary = self.get_test_summary()
        coverage = self.get_coverage_report()

        passed = (
            summary["pass_rate"] >= 90
            and coverage["total_coverage"] >= 80
            and len([r for r in self.test_results.values() if r["status"] == "failed"]) == 0
        )

        return {
            "passed": passed,
            "test_pass_rate": summary["pass_rate"],
            "coverage": coverage["total_coverage"],
            "requirements": {
                "min_pass_rate": 90,
                "min_coverage": 80,
                "max_failures": 0,
            },
        }

    def recommend_improvements(self) -> List[str]:
        """Get recommendations for improving test suite."""
        recommendations = []
        summary = self.get_test_summary()
        coverage = self.get_coverage_report()

        if summary["pass_rate"] < 95:
            recommendations.append(
                f"Improve test pass rate to 95% (currently {summary['pass_rate']:.1f}%)"
            )
        if coverage["total_coverage"] < 85:
            recommendations.append(
                f"Increase coverage to 85% (currently {coverage['total_coverage']:.1f}%)"
            )

        for module, cov in self.coverage_data.items():
            if cov < 80:
                recommendations.append(f"Increase {module} coverage to 80% (currently {cov:.1f}%)")

        return recommendations
