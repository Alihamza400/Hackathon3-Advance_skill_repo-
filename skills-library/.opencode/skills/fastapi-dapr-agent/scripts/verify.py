#!/usr/bin/env python3
import subprocess
import json
import sys
import argparse
import time

def run_command(cmd, check=True, capture_output=True, text=True, quiet=False):
    try:
        if not quiet: print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=check, capture_output=capture_output, text=text)
        if not quiet and capture_output and result.stdout: print(f"Output: {result.stdout.strip()[:100]}...")
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        if not quiet: print(f"❌ Command failed: {' '.join(cmd)}")
        if capture_output: print(f"Error: {e.stderr.strip()}")
        if check: sys.exit(1)
        return None
    except FileNotFoundError:
        if not quiet: print(f"❌ Command not found: {cmd[0]}")
        if check: sys.exit(1)
        return None

def verify_fastapi_dapr_service(service_name, namespace="default", timeout_seconds=300):
    print(f"Verifying FastAPI + Dapr service '{service_name}' in namespace: {namespace}")

    start_time = time.time()

    # 1. Check Deployment Status
    print("\n=== Step 1: Checking Deployment Status ===")
    deployment_name = f"{service_name}-deployment"
    try:
        run_command(["kubectl", "wait", "--for=condition=Available", f"deployment/{deployment_name}", "-n", namespace, f"--timeout={timeout_seconds}s"], quiet=True)
        print(f"✓ Deployment '{deployment_name}' is Available.")
    except SystemExit:
        print(f"❌ Deployment '{deployment_name}' did not become Available within {timeout_seconds}s.")
        sys.exit(1)

    # 2. Check Pods Status and Dapr Sidecar
    print("\n=== Step 2: Checking Pods Status and Dapr Sidecar ===")
    while time.time() - start_time < timeout_seconds:
        pods_output = run_command(["kubectl", "get", "pods", "-n", namespace, "-l", f"app={service_name}", "-o", "json"], check=False, quiet=True)
        if not pods_output: # If command failed or no output, retry
            print("Waiting for pods to appear...")
            time.sleep(5)
            continue

        try:
            pods_data = json.loads(pods_output)
            pods = pods_data.get("items", [])

            if not pods:
                print("No pods found yet. Retrying...")
                time.sleep(5)
                continue

            all_running = True
            all_dapr_enabled = True
            for pod in pods:
                pod_name = pod["metadata"]["name"]
                pod_status = pod["status"]["phase"]
                
                # Check main container status
                main_container_ready = False
                for container_status in pod["status"].get("containerStatuses", []):
                    if container_status["name"] == service_name and container_status["ready"]:
                        main_container_ready = True
                        break

                if pod_status != "Running" or not main_container_ready:
                    all_running = False
                    print(f"⚠️ Pod '{pod_name}' is in {pod_status} state or main container not ready. Retrying...")
                    break

                # Check Dapr sidecar status
                dapr_annotation = pod["metadata"]["annotations"].get("dapr.io/enabled", "false")
                if dapr_annotation != "true":
                    all_dapr_enabled = False
                    print(f"❌ Pod '{pod_name}' does not have Dapr enabled annotation.")

                dapr_container_found = False
                for container in pod["spec"].get("containers", []):
                    if container["name"] == "daprd":
                        dapr_container_found = True
                        break
                if not dapr_container_found:
                    all_dapr_enabled = False
                    print(f"❌ Pod '{pod_name}' is missing Dapr sidecar container.")

            if all_running and all_dapr_enabled: # Only exit if all conditions met
                print(f"✓ All {len(pods)} pods for '{service_name}' are Running with Dapr sidecar enabled.")
                break
            else:
                time.sleep(5)
        except json.JSONDecodeError:
            print("Failed to parse kubectl pods output. Retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred while checking pods: {e}. Retrying...")
            time.sleep(5)
    else:
        print(f"❌ Pods for '{service_name}' did not reach desired state within {timeout_seconds}s.")
        sys.exit(1)

    # 3. Check Dapr Components (basic check, assumes components applied)
    print("\n=== Step 3: Checking Dapr Components ===")
    components_output = run_command(["kubectl", "get", "components", "-n", namespace, "-o", "json"], check=False, quiet=True)
    if components_output:
        try:
            components_data = json.loads(components_output)
            components = components_data.get("items", [])
            if components:
                print(f"✓ Found {len(components)} Dapr components configured.")
            else:
                print("❌ No Dapr components found. Please check configure_dapr.sh.")
                sys.exit(1)
        except json.JSONDecodeError:
            print("❌ Failed to parse kubectl components output.")
            sys.exit(1)
    else:
        print("❌ Dapr components command failed or returned no output.")
        sys.exit(1)

    # 4. Test Service Health Endpoint (Optional, requires exposing service or port-forwarding)
    print("\n=== Step 4: Testing Service Health Endpoint ===")
    # This part is complex for automated testing in a generic K8s environment without ingress/LoadBalancer
    # For a simple check, we can try port-forwarding to a pod or assume internal connectivity.
    
    # Placeholder: Assuming service is reachable internally or via Dapr client for testing
    print("ℹ Manual verification of service health endpoint is recommended.")
    print(f"   Example: kubectl port-forward deploy/{deployment_name} 8000:8000 -n {namespace}")
    print(f"   Then: curl http://localhost:8000/health")

    # Final Conclusion
    print("\n=== Final Validation ===")
    print(f"🎉 FastAPI + Dapr service '{service_name}' deployment verification process completed!")
    print("   Please review the detailed logs for any warnings or manual steps required.")

    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify FastAPI + Dapr service deployment on Kubernetes.")
    parser.add_argument("service_name", help="Name of the microservice (e.g., concepts-agent).")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace where the service is deployed.")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds for deployment readiness.")
    
    args = parser.parse_args()
    verify_fastapi_dapr_service(service_name=args.service_name, namespace=args.namespace, timeout_seconds=args.timeout)
