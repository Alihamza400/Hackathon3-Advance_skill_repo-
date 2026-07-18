#!/usr/bin/env python3
"""Simple load testing script for LearnFlow services."""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


try:
    import httpx
except ImportError:
    print("httpx is required. Install with: pip install httpx")
    sys.exit(1)


@dataclass
class TestResult:
    endpoint: str
    status: int
    duration_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class ScenarioResult:
    name: str
    total: int
    passed: int
    failed: int
    avg_duration_ms: float
    p95_duration_ms: float
    results: list[TestResult]


BASE_URL = "http://localhost:8000"


async def test_health(client: httpx.AsyncClient) -> TestResult:
    start = time.time()
    try:
        resp = await client.get(f"{BASE_URL}/health", timeout=5.0)
        duration = (time.time() - start) * 1000
        return TestResult(
            endpoint="GET /health",
            status=resp.status_code,
            duration_ms=round(duration, 2),
            success=resp.status_code == 200,
        )
    except Exception as e:
        duration = (time.time() - start) * 1000
        return TestResult(
            endpoint="GET /health",
            status=0,
            duration_ms=round(duration, 2),
            success=False,
            error=str(e),
        )


async def test_login_flow(client: httpx.AsyncClient) -> list[TestResult]:
    results: list[TestResult] = []
    email = f"loadtest-{int(time.time())}@learnflow.io"
    password = "LoadTestPass123!"

    # Register
    start = time.time()
    try:
        resp = await client.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password, "full_name": "Load Tester"},
            timeout=5.0,
        )
        duration = (time.time() - start) * 1000
        results.append(
            TestResult(
                endpoint="POST /auth/register",
                status=resp.status_code,
                duration_ms=round(duration, 2),
                success=resp.status_code in (200, 201),
            )
        )
    except Exception as e:
        duration = (time.time() - start) * 1000
        results.append(
            TestResult(
                endpoint="POST /auth/register",
                status=0,
                duration_ms=round(duration, 2),
                success=False,
                error=str(e),
            )
        )

    # Login
    start = time.time()
    try:
        resp = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": email, "password": password},
            timeout=5.0,
        )
        duration = (time.time() - start) * 1000
        success = resp.status_code == 200
        results.append(
            TestResult(
                endpoint="POST /auth/login",
                status=resp.status_code,
                duration_ms=round(duration, 2),
                success=success,
            )
        )
        token = resp.json().get("access_token", "") if success else ""
    except Exception as e:
        duration = (time.time() - start) * 1000
        results.append(
            TestResult(
                endpoint="POST /auth/login",
                status=0,
                duration_ms=round(duration, 2),
                success=False,
                error=str(e),
            )
        )
        token = ""

    # Get profile
    if token:
        start = time.time()
        try:
            resp = await client.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
            duration = (time.time() - start) * 1000
            results.append(
                TestResult(
                    endpoint="GET /auth/me",
                    status=resp.status_code,
                    duration_ms=round(duration, 2),
                    success=resp.status_code == 200,
                )
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            results.append(
                TestResult(
                    endpoint="GET /auth/me",
                    status=0,
                    duration_ms=round(duration, 2),
                    success=False,
                    error=str(e),
                )
            )

    return results


async def test_triage_flow(client: httpx.AsyncClient, token: str) -> list[TestResult]:
    results: list[TestResult] = []
    headers = {"Authorization": f"Bearer {token}"}

    queries = [
        "Explain how variables work in Python",
        "Why am I getting IndexError?",
        "Review my code for best practices",
    ]

    for query in queries:
        start = time.time()
        try:
            resp = await client.post(
                f"{BASE_URL}/triage",
                json={"query": query},
                headers=headers,
                timeout=10.0,
            )
            duration = (time.time() - start) * 1000
            results.append(
                TestResult(
                    endpoint=f"POST /triage (query: {query[:20]}...)",
                    status=resp.status_code,
                    duration_ms=round(duration, 2),
                    success=resp.status_code == 200,
                )
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            results.append(
                TestResult(
                    endpoint=f"POST /triage (query: {query[:20]}...)",
                    status=0,
                    duration_ms=round(duration, 2),
                    success=False,
                    error=str(e),
                )
            )

    return results


async def run_scenario(
    name: str, concurrency: int, iterations: int
) -> ScenarioResult:
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(iterations):
            for _ in range(concurrency):
                if name == "health":
                    tasks.append(test_health(client))
                elif name == "login":
                    tasks.extend([test_login_flow(client) for _ in range(concurrency)])

        if name == "health":
            results = await asyncio.gather(*tasks)
        elif name == "triage":
            # Login first to get token
            email = f"benchmark-{int(time.time())}@learnflow.io"
            resp = await client.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": email,
                    "password": "Benchmark123!",
                    "full_name": "Benchmark User",
                },
                timeout=5.0,
            )
            token = ""
            if resp.status_code in (200, 201):
                login_resp = await client.post(
                    f"{BASE_URL}/auth/login",
                    data={"username": email, "password": "Benchmark123!"},
                    timeout=5.0,
                )
                if login_resp.status_code == 200:
                    token = login_resp.json().get("access_token", "")

            if token:
                all_results = []
                for _ in range(iterations):
                    for _ in range(concurrency):
                        res = await test_triage_flow(client, token)
                        all_results.extend(res)
                results = all_results
            else:
                results = [TestResult("auth_flow", 0, 0, False, "Auth failed")]

        # Flatten nested lists
        flat_results: list[TestResult] = []
        for r in results:
            if isinstance(r, list):
                flat_results.extend(r)
            else:
                flat_results.append(r)

        passed = sum(1 for r in flat_results if r.success)
        failed = len(flat_results) - passed
        durations = [r.duration_ms for r in flat_results if r.duration_ms > 0]
        avg_dur = sum(durations) / len(durations) if durations else 0
        sorted_durs = sorted(durations)
        p95 = sorted_durs[int(len(sorted_durs) * 0.95)] if sorted_durs else 0

        return ScenarioResult(
            name=name,
            total=len(flat_results),
            passed=passed,
            failed=failed,
            avg_duration_ms=round(avg_dur, 2),
            p95_duration_ms=round(p95, 2),
            results=flat_results,
        )


def generate_report(results: list[ScenarioResult]) -> str:
    lines = [
        "=" * 60,
        "  LearnFlow Load Test Report",
        f"  Generated: {datetime.now().isoformat()}",
        "=" * 60,
        "",
        f"{'Scenario':<25} {'Total':>8} {'Passed':>8} {'Failed':>8} {'Avg(ms)':>10} {'P95(ms)':>10}",
        "-" * 71,
    ]

    for r in results:
        lines.append(
            f"{r.name:<25} {r.total:>8} {r.passed:>8} {r.failed:>8} {r.avg_duration_ms:>10.2f} {r.p95_duration_ms:>10.2f}"
        )

    overall_passed = sum(r.passed for r in results)
    overall_total = sum(r.total for r in results)
    overall_pct = (overall_passed / overall_total * 100) if overall_total else 0

    lines.append("-" * 71)
    lines.append(
        f"{'TOTAL':<25} {overall_total:>8} {overall_passed:>8} {overall_total - overall_passed:>8} {'':>10} {'':>10}"
    )
    lines.append(f"\nOverall Success Rate: {overall_pct:.1f}%")
    lines.append("")

    if overall_pct < 95:
        lines.append("WARNING: Success rate below 95% threshold!")
        lines.append("Failed requests:")
        for r in results:
            for tr in r.results:
                if not tr.success:
                    lines.append(f"  - {tr.endpoint}: {tr.error or f'HTTP {tr.status}'}")
        lines.append("")

    return "\n".join(lines)


async def main():
    scenarios = [
        ("health", 10, 5),
        ("login", 5, 3),
        ("triage", 5, 3),
    ]

    results = []
    for name, concurrency, iterations in scenarios:
        print(f"Running scenario: {name} ({concurrency} concurrent x {iterations})...")
        result = await run_scenario(name, concurrency, iterations)
        results.append(result)
        print(f"  -> {result.passed}/{result.total} passed (avg: {result.avg_duration_ms}ms)")

    report = generate_report(results)
    print(f"\n{report}")

    report_path = f"load-test-report-{int(time.time())}.txt"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
