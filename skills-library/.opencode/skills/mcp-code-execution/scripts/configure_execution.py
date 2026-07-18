#!/usr/bin/env python3
# Configure MCP code execution server with enterprise settings

import json
import argparse
import os
import sys
from pathlib import Path

def configure_mcp_server(config_path: str = "./mcp_server_config.json", 
                        workspace_dir: str = "./mcp_workspace",
                        timeout_seconds: int = 30,
                        max_memory_mb: int = 512,
                        allowed_languages: list = None,
                        security_level: str = "high",
                        audit_log: bool = True):
    """
    Configure MCP code execution server with enterprise settings.
    
    Args:
        config_path: Path to save configuration
        workspace_dir: Directory for code execution workspace
        timeout_seconds: Max execution time per script
        max_memory_mb: Memory limit per execution
        allowed_languages: List of permitted languages
        security_level: Security enforcement level (high/medium/low)
        audit_log: Enable audit logging
    """
    
    if allowed_languages is None:
        allowed_languages = ["python", "bash"]
    
    # Create workspace directory
    workspace = Path(workspace_dir)
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Create security subdirectories
    (workspace / "scripts").mkdir(exist_ok=True)
    (workspace / "outputs").mkdir(exist_ok=True)
    (workspace / "audit").mkdir(exist_ok=True)
    
    # Enterprise configuration
    config = {
        "server": {
            "name": "enterprise-code-execution-mcp",
            "version": "1.0.0",
            "protocol_version": "2024-11-05"
        },
        "execution": {
            "timeout_seconds": timeout_seconds,
            "max_memory_mb": max_memory_mb,
            "allowed_languages": allowed_languages,
            "workspace_dir": str(workspace.absolute()),
            "max_script_size_kb": 100,
            "max_concurrent_executions": 5
        },
        "security": {
            "level": security_level,
            "allowed_imports": {
                "python": [
                    "os", "sys", "json", "math", "random", "datetime", "collections",
                    "itertools", "functools", "hashlib", "base64", "urllib.parse",
                    "re", "string", "typing", "dataclasses", "enum", "pathlib"
                ],
                "bash": [
                    "ls", "cat", "echo", "grep", "awk", "sed", "find", "wc",
                    "head", "tail", "sort", "uniq", "cut", "tr", "date"
                ]
            },
            "blocked_imports": {
                "python": [
                    "subprocess", "multiprocessing", "threading", "socket",
                    "urllib.request", "http.client", "ftplib", "smtplib",
                    "ctypes", "importlib", "pkgutil", "runpy", "sys",
                    "builtins", "types", "importlib", "runpy"
                ],
                "bash": [
                    "rm", "mv", "cp", "dd", "mkfs", "fdisk", "mount", "umount",
                    "iptables", "systemctl", "service", "apt", "yum", "pip",
                    "curl", "wget", "ssh", "scp", "rsync", "nc", "netcat"
                ]
            },
            "network_access": False,
            "filesystem_access": "workspace_only",
            "process_creation": False
        },
        "audit": {
            "enabled": audit_log,
            "log_dir": str((workspace / "audit").absolute()),
            "log_format": "json",
            "retention_days": 30,
            "log_executions": True,
            "log_errors": True,
            "log_security_violations": True
        },
        "resource_limits": {
            "cpu_percent": 50,
            "memory_mb": max_memory_mb,
            "disk_mb": 100,
            "file_descriptors": 64
        },
        "monitoring": {
            "metrics_enabled": True,
            "metrics_port": 9090,
            "health_check_interval_seconds": 30
        }
    }
    
    # Save configuration
    with open(config_path, 'w') as f:
        json.dump(config, indent=2, f)
    
    print(f"✓ MCP Code Execution Server configured at {config_path}")
    print(f"  Workspace: {workspace.absolute()}")
    print(f"  Timeout: {timeout_seconds}s")
    print(f"  Memory Limit: {max_memory_mb}MB")
    print(f"  Languages: {', '.join(allowed_languages)}")
    print(f"  Security Level: {security_level}")
    print(f"  Audit Logging: {'Enabled' if audit_log else 'Disabled'}")

def create_dockerfile(output_path: str = "./Dockerfile.mcp"):
    """Create Dockerfile for enterprise MCP server deployment."""
    dockerfile_content = '''# Enterprise MCP Code Execution Server
FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    bash \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy configuration and server code
COPY mcp_server_config.json /app/
COPY wrap_mcp.py /app/

# Create workspace directories
RUN mkdir -p /workspace/scripts /workspace/outputs /workspace/audit \\
    && chown -R mcpuser:mcpuser /workspace /app

# Switch to non-root user
USER mcpuser

# Expose metrics port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD python -c "import json; print(json.dumps({'status': 'healthy'}))"

# Run server
CMD ["python", "wrap_mcp.py"]
'''
    with open(output_path, 'w') as f:
        f.write(dockerfile_content)
    print(f"✓ Dockerfile created at {output_path}")

def create_k8s_manifests(output_dir: str = "./k8s-mcp"):
    """Create Kubernetes manifests for enterprise MCP server."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Deployment
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "mcp-code-execution",
            "labels": {"app": "mcp-code-execution"}
        },
        "spec": {
            "replicas": 2,
            "selector": {"matchLabels": {"app": "mcp-code-execution"}},
            "template": {
                "metadata": {"labels": {"app": "mcp-code-execution"}},
                "spec": {
                    "securityContext": {
                        "runAsNonRoot": True,
                        "runAsUser": 1000,
                        "fsGroup": 1000
                    },
                    "containers": [{
                        "name": "mcp-server",
                        "image": "mcp-code-execution:latest",
                        "ports": [{"containerPort": 9090, "name": "metrics"}],
                        "resources": {
                            "requests": {"memory": "256Mi", "cpu": "100m"},
                            "limits": {"memory": "512Mi", "cpu": "500m"}
                        },
                        "volumeMounts": [{
                            "name": "workspace",
                            "mountPath": "/workspace"
                        }, {
                            "name": "config",
                            "mountPath": "/app/mcp_server_config.json",
                            "subPath": "mcp_server_config.json"
                        }],
                        "livenessProbe": {
                            "httpGet": {"path": "/health", "port": 9090},
                            "initialDelaySeconds": 10,
                            "periodSeconds": 30
                        },
                        "readinessProbe": {
                            "httpGet": {"path": "/health", "port": 9090},
                            "initialDelaySeconds": 5,
                            "periodSeconds": 10
                        }
                    }],
                    "volumes": [{
                        "name": "workspace",
                        "emptyDir": {}
                    }, {
                        "name": "config",
                        "configMap": {"name": "mcp-config"}
                    }]
                }
            }
        }
    }
    
    import yaml
    with open(os.path.join(output_dir, "deployment.yaml"), 'w') as f:
        yaml.dump(deployment, f, default_flow_style=False)
    
    # Service
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "mcp-code-execution"},
        "spec": {
            "selector": {"app": "mcp-code-execution"},
            "ports": [{"port": 9090, "targetPort": 9090, "name": "metrics"}],
            "type": "ClusterIP"
        }
    }
    with open(os.path.join(output_dir, "service.yaml"), 'w') as f:
        yaml.dump(service, f, default_flow_style=False)
    
    # ConfigMap
    configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "mcp-config"},
        "data": {
            "mcp_server_config.json": "{{ .Files.Get \"mcp_server_config.json\" }}"
        }
    }
    with open(os.path.join(output_dir, "configmap.yaml"), 'w') as f:
        yaml.dump(configmap, f, default_flow_style=False)
    
    print(f"✓ Kubernetes manifests created in {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Configure MCP Code Execution Server")
    parser.add_argument("--config", default="./mcp_server_config.json", help="Config output path")
    parser.add_argument("--workspace", default="./mcp_workspace", help="Workspace directory")
    parser.add_argument("--timeout", type=int, default=30, help="Execution timeout (seconds)")
    parser.add_argument("--memory", type=int, default=512, help="Memory limit (MB)")
    parser.add_argument("--languages", nargs="+", default=["python", "bash"], help="Allowed languages")
    parser.add_argument("--security", choices=["high", "medium", "low"], default="high", help="Security level")
    parser.add_argument("--audit", action="store_true", default=True, help="Enable audit logging")
    parser.add_argument("--dockerfile", action="store_true", help="Generate Dockerfile")
    parser.add_argument("--k8s", action="store_true", help="Generate Kubernetes manifests")
    parser.add_argument("--k8s-dir", default="./k8s-mcp", help="K8s manifests output directory")
    
    args = parser.parse_args()
    
    # Configure server
    configure_mcp_server(
        config_path=args.config,
        workspace_dir=args.workspace,
        timeout_seconds=args.timeout,
        max_memory_mb=args.memory,
        allowed_languages=args.languages,
        security_level=args.security,
        audit_log=args.audit
    )
    
    if args.dockerfile:
        create_dockerfile()
    
    if args.k8s:
        try:
            create_k8s_manifests(args.k8s_dir)
        except ImportError:
            print("⚠️ PyYAML not installed, skipping K8s manifests. Install with: pip install pyyaml")

if __name__ == "__main__":
    main()